#!/usr/bin/env python3
"""Embedded / IoT Mentor as a REST API.

Nothing is reimplemented. The reference docs are read from the skill folder and
the calculators shell out to `embedded-iot-mentor/scripts/`, so an answer here is
the answer the skill would give. Edit the skill, and this port moves with it.

Run it:
  pip install -r api/requirements.txt
  uvicorn api.main:app --reload      # http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Literal

import anthropic
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, field_validator


HERE = Path(__file__).resolve().parent

# api/ is a child of the repository root, so the skill folder is its sibling.
# EIM_SKILL_DIR covers deployments that copy this file somewhere else and bring
# the skill folder along separately.
SKILL_DIR = Path(os.environ.get("EIM_SKILL_DIR", HERE.parent / "embedded-iot-mentor")).resolve()
SCRIPTS_DIR = SKILL_DIR / "scripts"
REFERENCES_DIR = SKILL_DIR / "references"

# The mentor's rules, shared with the ChatGPT ports so no route drifts.
INSTRUCTIONS = Path(
    os.environ.get("EIM_INSTRUCTIONS", HERE.parent / "chatgpt-app" / "custom-gpt" / "instructions.md")
).resolve()

SCRIPT_TIMEOUT_S = 20

# Unset means open, which is what a local run wants. Set it in any deployment.
API_KEY = os.environ.get("EIM_API_KEY", "")

# Browsers only, and empty by default: a server nobody has pointed a web page at
# needs no cross-origin permission, and "*" is hard to take back once published.
CORS_ORIGINS = [o.strip() for o in os.environ.get("EIM_CORS_ORIGINS", "").split(",") if o.strip()]

MAX_BODY_BYTES = 64 * 1024
RATE_LIMIT_PER_MIN = int(os.environ.get("EIM_RATE_LIMIT_PER_MIN", "60"))
MAX_CONCURRENT_SCRIPTS = int(os.environ.get("EIM_MAX_CONCURRENT_SCRIPTS", "4"))

# POST /chat is off until this is set — no key means no accidental spend.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CHAT_MODEL = os.environ.get("EIM_CHAT_MODEL", "claude-sonnet-5")
CHAT_MAX_TOKENS = int(os.environ.get("EIM_CHAT_MAX_TOKENS", "2000"))
CHAT_MAX_TOOL_ROUNDS = 4
# Separate from RATE_LIMIT_PER_MIN and much stricter: the calculators are free
# to run, a chat turn is a billed model call, and this page is public.
CHAT_RATE_LIMIT_PER_MIN = int(os.environ.get("EIM_CHAT_RATE_LIMIT_PER_MIN", "6"))

# A platform health check should not need the secret.
OPEN_PATHS = {"/healthz"}


def skill_version() -> str:
    """The skill's own version, so the API cannot report a stale one."""
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r'^\s*version:\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "unknown"


# Only these three scripts are ever executed, named here rather than taken from
# the request, so no input can reach the process arguments as a script path.
SCRIPTS = {
    "cost": "cost_estimator.py",
    "sleep": "sleep_budget.py",
    "footprint": "footprint_hint.py",
}


# Every calculator call is a Python process. Routes are sync, so FastAPI runs
# them in its threadpool, and without a cap a burst forks until the box gives up.
_script_slots = threading.BoundedSemaphore(MAX_CONCURRENT_SCRIPTS)


def run_script(key: str, args: list[str]) -> str:
    """Run one helper script and return its stdout.

    The scripts exit 1 on bad input and print the reason to stderr, so a non-zero
    exit is the caller's mistake (400), not a server fault.
    """
    script = SCRIPTS_DIR / SCRIPTS[key]
    # Take a slot before spawning; the timeout means a queued caller waits rather
    # than being refused the instant the box is busy.
    if not _script_slots.acquire(timeout=SCRIPT_TIMEOUT_S):
        raise HTTPException(503, "busy: too many calculations in flight")
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=SCRIPT_TIMEOUT_S,
        )
    except FileNotFoundError:
        raise HTTPException(500, f"script missing: {script}")
    except subprocess.TimeoutExpired:
        raise HTTPException(504, f"{SCRIPTS[key]} took longer than {SCRIPT_TIMEOUT_S}s")
    finally:
        # Runs on the raising paths too, or a timeout would burn a slot forever.
        _script_slots.release()

    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "script failed"
        raise HTTPException(400, detail)
    return proc.stdout


class CostItem(BaseModel):
    qty: float = Field(gt=0, description="how many of this part")
    unit_price: float = Field(ge=0, description="price for one, in your own currency")
    description: str = Field("", max_length=200)


class CostRequest(BaseModel):
    items: list[CostItem] = Field(min_length=1, max_length=200)

    def to_args(self) -> list[str]:
        # The comma form only. The spaced form guesses a description by "not a
        # number", which would eat a description like "2024" as the next quantity.
        return [f"{i.qty:g},{i.unit_price:g},{i.description}" for i in self.items]


class SleepRequest(BaseModel):
    capacity_mah: float = Field(gt=0, description="battery capacity in mAh")
    active_ma: float = Field(gt=0, description="current while awake, in mA")
    active_ms: float = Field(gt=0, description="awake time per cycle, in ms")
    sleep_ua: float = Field(ge=0, description="sleep current in uA, regulator included")
    interval_s: float = Field(gt=0, description="seconds between wake-ups")
    derate: float = Field(0.8, gt=0, le=1, description="usable fraction of rated capacity")

    def to_args(self) -> list[str]:
        return [
            "--capacity", f"{self.capacity_mah:g}",
            "--active-ma", f"{self.active_ma:g}",
            "--active-ms", f"{self.active_ms:g}",
            "--sleep-ua", f"{self.sleep_ua:g}",
            "--interval-s", f"{self.interval_s:g}",
            "--derate", f"{self.derate:g}",
        ]


class FootprintRequest(BaseModel):
    package: str = Field(min_length=1, max_length=40, examples=["0603", "QFN-32"])

    @field_validator("package")
    @classmethod
    def not_a_flag(cls, v: str) -> str:
        # The script reads argv positionally, so a leading dash would be taken
        # for an option rather than a package name.
        if v.strip().startswith("-"):
            raise ValueError("package cannot start with '-'")
        return v.strip()

    def to_args(self) -> list[str]:
        return [self.package]


_hits: dict[str, list[float]] = {}
_hits_lock = threading.Lock()


def _client_ip(request: Request) -> str:
    # Render and most hosts terminate TLS in front, so the socket peer is the
    # proxy and every caller would share one bucket. The first hop in
    # X-Forwarded-For is the real client.
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded.strip():
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(hits: dict[str, list[float]], lock: threading.Lock, limit: int, ip: str) -> bool:
    """Fixed one-minute window, per process. Good enough for one small instance;
    a second instance would need shared state, which is not worth a Redis."""
    now = time.monotonic()
    with lock:
        recent = [t for t in hits.get(ip, ()) if now - t < 60]
        if len(recent) >= limit:
            hits[ip] = recent
            return False
        recent.append(now)
        hits[ip] = recent
        if len(hits) > 10_000:
            # A spray of forged IPs would otherwise grow this map forever.
            for stale in [k for k, v in hits.items() if not v or now - v[-1] > 60]:
                hits.pop(stale, None)
        return True


def _within_rate_limit(ip: str) -> bool:
    return _check_rate_limit(_hits, _hits_lock, RATE_LIMIT_PER_MIN, ip)


_chat_hits: dict[str, list[float]] = {}
_chat_hits_lock = threading.Lock()


def _within_chat_rate_limit(ip: str) -> bool:
    # Its own bucket and a tighter cap than _within_rate_limit — a chat turn
    # calls a billed model, the calculators don't.
    return _check_rate_limit(_chat_hits, _chat_hits_lock, CHAT_RATE_LIMIT_PER_MIN, ip)


_claude_client: anthropic.Anthropic | None = None


def _claude() -> anthropic.Anthropic:
    """Lazy singleton so a key-less deployment never touches the SDK."""
    global _claude_client
    if not ANTHROPIC_API_KEY:
        raise HTTPException(501, "chat is not configured on this server: set ANTHROPIC_API_KEY")
    if _claude_client is None:
        _claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _claude_client


# Same three calculators the routes below expose, offered as tools so the
# model can call them instead of doing the arithmetic itself.
CHAT_TOOLS = [
    {
        "name": "cost_estimate",
        "description": (
            "Estimate total BOM cost from a parts list. Call this when the user "
            "gives quantities and unit prices and wants a total — do not add up "
            "the numbers yourself."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "qty": {"type": "number", "exclusiveMinimum": 0},
                            "unit_price": {"type": "number", "minimum": 0},
                            "description": {"type": "string"},
                        },
                        "required": ["qty", "unit_price"],
                    },
                },
            },
            "required": ["items"],
        },
    },
    {
        "name": "sleep_budget",
        "description": (
            "Estimate battery runtime from active/sleep current draw and duty "
            "cycle. Call this when the user gives current draw and a wake "
            "interval and wants a runtime estimate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "capacity_mah": {"type": "number", "exclusiveMinimum": 0, "description": "battery capacity in mAh"},
                "active_ma": {"type": "number", "exclusiveMinimum": 0, "description": "current while awake, in mA"},
                "active_ms": {"type": "number", "exclusiveMinimum": 0, "description": "awake time per cycle, in ms"},
                "sleep_ua": {"type": "number", "minimum": 0, "description": "sleep current in uA, regulator included"},
                "interval_s": {"type": "number", "exclusiveMinimum": 0, "description": "seconds between wake-ups"},
                "derate": {"type": "number", "exclusiveMinimum": 0, "maximum": 1, "description": "usable fraction of rated capacity, default 0.8"},
            },
            "required": ["capacity_mah", "active_ma", "active_ms", "sleep_ua", "interval_s"],
        },
    },
    {
        "name": "footprint_hint",
        "description": (
            "Look up a common footprint/package hint, e.g. '0603' or 'QFN-32'. "
            "Call this when the user names a part package and wants a quick "
            "sanity check."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"package": {"type": "string", "minLength": 1}},
            "required": ["package"],
        },
    },
]


def _run_chat_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run one chat tool call through the same models and scripts the REST
    routes use, so a chat answer and a direct API call never disagree.
    Returns (content, is_error) — errors go back to the model as text, not
    raised, so it can explain the problem instead of the turn just failing."""
    try:
        if name == "cost_estimate":
            req = CostRequest(items=[CostItem(**it) for it in tool_input.get("items", [])])
            return run_script("cost", req.to_args()), False
        if name == "sleep_budget":
            req = SleepRequest(**tool_input)
            return run_script("sleep", req.to_args()), False
        if name == "footprint_hint":
            req = FootprintRequest(**tool_input)
            return run_script("footprint", req.to_args()), False
        return f"error: unknown tool '{name}'", True
    except HTTPException as exc:
        return f"error: {exc.detail}", True
    except (ValueError, TypeError) as exc:
        return f"error: bad input — {exc}", True


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    # Prior turns, oldest first; the client resends them each time since the
    # API itself keeps no session state.
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(
    title="Embedded / IoT Mentor API",
    version=skill_version(),
    description=(
        "The Embedded / IoT Mentor skill over HTTP. The reference docs are read "
        "from the skill folder and the calculators shell out to "
        "`embedded-iot-mentor/scripts/`, so an answer here is the answer the "
        "skill would give.\n\n"
        "- `/references`, `/search` — the reference library\n"
        "- `/cost`, `/sleep-budget`, `/footprint` — the calculators\n"
        "- `/instructions` — the mentor's rules, for your own model\n"
        "- `/chat` — the mentor talking for itself, via Claude — only when "
        "ANTHROPIC_API_KEY is set\n"
    ),
)


if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["content-type", "x-api-key"],
    )


@app.middleware("http")
async def guardrails(request: Request, call_next):
    if request.url.path in OPEN_PATHS:
        return await call_next(request)
    if API_KEY and request.headers.get("x-api-key") != API_KEY:
        return JSONResponse({"detail": "missing or wrong X-API-Key"}, status_code=401)
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        return JSONResponse({"detail": f"body over {MAX_BODY_BYTES} bytes"}, status_code=413)
    if not _within_rate_limit(_client_ip(request)):
        return JSONResponse(
            {"detail": "rate limit exceeded"}, status_code=429, headers={"Retry-After": "60"}
        )
    return await call_next(request)


def _reference_files() -> dict[str, Path]:
    """Reference docs by bare name. Built from a listing, never from the request,
    so a name like '../../SKILL.md' simply is not in the map."""
    return {p.stem: p for p in sorted(REFERENCES_DIR.glob("*.md"))}


@app.get("/healthz", response_class=PlainTextResponse, tags=["meta"])
def healthz() -> str:
    return "ok"


@app.get("/version", tags=["meta"])
def version() -> dict:
    return {"skill_version": skill_version(), "skill_dir": str(SKILL_DIR)}


@app.get("/instructions", response_class=PlainTextResponse, tags=["meta"])
def instructions() -> str:
    """The mentor's rules, so a client can hand them to its own model."""
    if not INSTRUCTIONS.is_file():
        raise HTTPException(500, f"instructions missing: {INSTRUCTIONS}")
    return INSTRUCTIONS.read_text(encoding="utf-8")


@app.get("/references", tags=["references"])
def list_references() -> dict:
    return {"references": sorted(_reference_files())}


@app.get("/references/{name}", response_class=PlainTextResponse, tags=["references"])
def get_reference(name: str) -> str:
    files = _reference_files()
    if name not in files:
        raise HTTPException(404, f"no reference named '{name}'. See GET /references")
    return files[name].read_text(encoding="utf-8")


@app.get("/search", tags=["references"])
def search(q: str = Query(min_length=2, max_length=100), limit: int = Query(20, ge=1, le=100)) -> dict:
    """Plain substring search over the reference library. No index, no ranking —
    fourteen small files do not need one."""
    needle = q.lower()
    hits = []
    for name, path in _reference_files().items():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if needle in line.lower():
                hits.append({"reference": name, "line": lineno, "text": line.strip()})
                if len(hits) >= limit:
                    return {"query": q, "hits": hits, "truncated": True}
    return {"query": q, "hits": hits, "truncated": False}


@app.post("/cost", response_class=PlainTextResponse, tags=["calculators"])
def cost(req: CostRequest) -> str:
    return run_script("cost", req.to_args())


@app.post("/sleep-budget", response_class=PlainTextResponse, tags=["calculators"])
def sleep_budget(req: SleepRequest) -> str:
    return run_script("sleep", req.to_args())


@app.post("/footprint", tags=["calculators"])
def footprint(req: FootprintRequest) -> dict:
    out = run_script("footprint", req.to_args())
    # The script marks a miss with "note:", so no sentence matching is needed.
    return {"package": req.package, "matched": not out.startswith("note:"), "hint": out.strip()}


@app.post("/chat", tags=["chat"])
def chat(req: ChatRequest, request: Request) -> ChatResponse:
    """The mentor as a conversation: same instructions, same calculators, but
    Claude does the talking instead of a human copy-pasting into a chat app."""
    if not _within_chat_rate_limit(_client_ip(request)):
        raise HTTPException(429, "chat rate limit exceeded — try again in a minute",
                             headers={"Retry-After": "60"})
    if not INSTRUCTIONS.is_file():
        raise HTTPException(500, f"instructions missing: {INSTRUCTIONS}")

    client = _claude()
    system = [{
        "type": "text",
        "text": INSTRUCTIONS.read_text(encoding="utf-8"),
        # The instructions never change within a deployment's lifetime, so
        # every caller after the first reads this from cache.
        "cache_control": {"type": "ephemeral"},
    }]
    messages: list[dict] = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    response = None
    for _ in range(CHAT_MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=CHAT_MODEL,
            max_tokens=CHAT_MAX_TOKENS,
            system=system,
            tools=CHAT_TOOLS,
            messages=messages,
        )
        if response.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                content, is_error = _run_chat_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                    "is_error": is_error,
                })
        messages.append({"role": "user", "content": tool_results})
    else:
        raise HTTPException(504, "chat: too many tool calls in one turn")

    if response.stop_reason == "refusal":
        raise HTTPException(422, "the model declined to answer that")

    reply = "".join(b.text for b in response.content if b.type == "text").strip()
    return ChatResponse(reply=reply or "(no response)")
