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
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
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


def run_script(key: str, args: list[str]) -> str:
    """Run one helper script and return its stdout.

    The scripts exit 1 on bad input and print the reason to stderr, so a non-zero
    exit is the caller's mistake (400), not a server fault.
    """
    script = SCRIPTS_DIR / SCRIPTS[key]
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
    ),
)


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
