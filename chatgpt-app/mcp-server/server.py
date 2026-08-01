#!/usr/bin/env python3
"""Embedded / IoT Mentor as an MCP server, for ChatGPT's custom connectors.

The Custom GPT route carries the mentor's judgement but leaves the reference
files behind a file upload and the helper scripts behind Code Interpreter. This
server hands ChatGPT both over the wire instead: `search` and `fetch` expose the
reference library, and three tools run the same scripts the Claude skill runs,
so a battery runtime quoted here is the number the skill would have quoted.

Nothing is reimplemented. The docs are read from the skill folder and the
calculators shell out to `embedded-iot-mentor/scripts/`, which keeps one source
of truth: edit the skill, and every port moves with it.

Run it:
  pip install -r requirements.txt
  python server.py                      # http://127.0.0.1:8000/mcp
  python server.py --transport stdio    # for MCP clients that speak stdio

ChatGPT reaches a connector over HTTPS, so a local run needs a tunnel. See
README.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from mcp.server import MCPServer

HERE = Path(__file__).resolve().parent

# The port sits two levels under the repository root; the skill folder is the
# sibling of chatgpt-app/. EIM_SKILL_DIR covers deployments that copy the server
# somewhere else and bring the skill folder along separately.
SKILL_DIR = Path(os.environ.get("EIM_SKILL_DIR", HERE.parents[1] / "embedded-iot-mentor")).resolve()
SCRIPTS_DIR = SKILL_DIR / "scripts"

# The ported rules live in one file, shared with the Custom GPT route, so the
# two ports cannot drift into giving different advice.
INSTRUCTIONS = Path(
    os.environ.get("EIM_INSTRUCTIONS", HERE.parent / "custom-gpt" / "instructions.md")
).resolve()

# Where a doc came from, for the citation ChatGPT shows next to an answer.
REPO_URL = os.environ.get(
    "EIM_REPO_URL",
    "https://github.com/mh-mansouri/embedded-iot-mentor/blob/main/embedded-iot-mentor",
)

SCRIPT_TIMEOUT_S = 20

# Question words carry no topic, and every reference file is full of them.
STOPWORDS = {
    "and", "are", "but", "can", "does", "for", "from", "has", "have", "how", "into",
    "its", "long", "make", "much", "need", "not", "one", "out", "over", "should",
    "some", "than", "that", "the", "them", "then", "there", "these", "they", "this",
    "use", "using", "want", "was", "what", "when", "where", "which", "will", "with",
    "would", "you", "your",
}

mcp = MCPServer(
    "embedded-iot-mentor",
    title="Embedded / IoT Mentor",
    version="1.1.0",
    instructions=(
        "Mentor for embedded and IoT projects. Call mentor_guidance first in any "
        "conversation about hardware, firmware, sensors or IoT dashboards, and follow "
        "what it returns. Use search/fetch for the reference library, and the three "
        "calculators instead of estimating a battery runtime or a BOM total in prose."
    ),
)


def _docs() -> dict[str, Path]:
    """The reference library, keyed by the id `search` and `fetch` speak in."""
    found = {}
    for folder in ("references", "examples"):
        for path in sorted((SKILL_DIR / folder).glob("*.md")):
            found[path.stem] = path
    return found


def _title(path: Path) -> str:
    """First heading if there is one, otherwise the filename."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ")


def _url(path: Path) -> str:
    return f"{REPO_URL}/{path.relative_to(SKILL_DIR).as_posix()}"


def _run_script(name: str, args: list[str]) -> str:
    """Run a skill helper script and return its stdout.

    argv is built from typed tool arguments, never from a shell string, so a
    description like `10k resistor; rm -rf` is one argument and nothing else.
    """
    script = SCRIPTS_DIR / name
    if not script.is_file():
        raise FileNotFoundError(
            f"{name} not found under {SCRIPTS_DIR}. Set EIM_SKILL_DIR to the "
            "embedded-iot-mentor folder."
        )
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=SCRIPT_TIMEOUT_S,
    )
    if result.returncode != 0:
        raise ValueError((result.stderr or result.stdout).strip() or f"{name} failed")
    return result.stdout.rstrip()


@mcp.tool()
def mentor_guidance() -> str:
    """How to answer embedded and IoT questions: length limits, MVP-first framing,
    the reject bar, and when to hand off. Call this before giving project advice."""
    return INSTRUCTIONS.read_text(encoding="utf-8")


@mcp.tool()
def search(query: str) -> dict:
    """Search the mentor's reference library — MCU selection, connectivity, dashboards,
    cost, PCB, power, field deployment, OTA, EMC, safety boundary, learning resources,
    worked examples. Returns ids to pass to fetch."""
    docs = _docs()
    bodies = {doc_id: path.read_text(encoding="utf-8").lower() for doc_id, path in docs.items()}
    terms = {t for t in re.split(r"\W+", query.lower()) if len(t) > 2 and t not in STOPWORDS}
    mean_length = sum(len(b) for b in bodies.values()) / len(bodies)

    hits = []
    for doc_id, body in bodies.items():
        # Weight a term by its share of that term across the whole library, so
        # "battery" points at the battery notes and a word every file uses adds
        # almost nothing. Then divide by length, or the file that touches every
        # topic — worked-examples — would answer every query.
        share = 0.0
        for term in terms:
            corpus = sum(other.count(term) for other in bodies.values())
            if corpus:
                share += body.count(term) / corpus
        score = share / (len(body) / mean_length) ** 0.5

        # The id carries the topic: "ota" reaches ota-update-notes even though
        # the acronym barely appears in its prose. Whole words only — "work"
        # must not match worked-examples.
        score += 1.5 * len(terms & set(doc_id.split("-")))

        if score:
            hits.append((score, doc_id, docs[doc_id]))
    hits.sort(key=lambda h: (-h[0], h[1]))
    return {
        "results": [
            {"id": doc_id, "title": _title(path), "url": _url(path)}
            for _, doc_id, path in hits[:5]
        ]
    }


@mcp.tool()
def fetch(id: str) -> dict:
    """Fetch one reference document in full, by the id returned from search."""
    path = _docs().get(id)
    if path is None:
        raise ValueError(f"unknown document '{id}'; call search first")
    return {
        "id": id,
        "title": _title(path),
        "text": path.read_text(encoding="utf-8"),
        "url": _url(path),
        "metadata": {"source": "embedded-iot-mentor"},
    }


@mcp.tool()
def estimate_bom_cost(items: list[dict]) -> str:
    """Total a bill of materials. Each item is {"qty": number, "unit_price": number,
    "description": string}. Use real quoted prices, not guesses."""
    if not items:
        raise ValueError("pass at least one {qty, unit_price, description} item")
    args: list[str] = []
    for item in items:
        try:
            args += [str(float(item["qty"])), str(float(item["unit_price"]))]
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"item needs numeric 'qty' and 'unit_price': {item!r}")
        description = str(item.get("description", "")).strip()
        if description:
            # The script reads a bare number as the start of the next line item,
            # so "2200" as a description would silently become a quantity.
            if _is_number(description):
                raise ValueError(
                    f"description '{description}' is a bare number; name the part "
                    "(e.g. '2200 mAh cell')"
                )
            args.append(description)
    return _run_script("cost_estimator.py", args)


@mcp.tool()
def hand_solder_hint(package: str) -> str:
    """Whether a named package (0402, 0805, SOT-23, TSSOP, QFN-32, BGA…) is realistic
    to hand-solder, and what to use instead on a first board."""
    return _run_script("footprint_hint.py", [package])


@mcp.tool()
def battery_runtime(
    capacity_mah: float,
    active_ma: float,
    active_ms: float,
    sleep_ua: float,
    interval_s: float,
    derate: float = 0.8,
) -> str:
    """Battery runtime for a duty-cycled device, and whether sleep or wake dominates.

    sleep_ua is the whole board asleep — MCU plus regulator quiescent draw plus
    sensors — which is the figure that turns a claimed two months into four days.
    """
    return _run_script(
        "sleep_budget.py",
        [
            "--capacity", str(capacity_mah),
            "--active-ma", str(active_ma),
            "--active-ms", str(active_ms),
            "--sleep-ua", str(sleep_ua),
            "--interval-s", str(interval_s),
            "--derate", str(derate),
        ],
    )


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--transport",
        default="streamable-http",
        choices=["streamable-http", "sse", "stdio"],
        help="streamable-http (default) is what ChatGPT connectors speak",
    )
    args = parser.parse_args()

    if not SKILL_DIR.is_dir():
        print(
            f"error: no skill folder at {SKILL_DIR}. Set EIM_SKILL_DIR to the "
            "embedded-iot-mentor folder.",
            file=sys.stderr,
        )
        return 1

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # A hosted deployment sets PORT; HOST has to become 0.0.0.0 there, since
        # the default only listens on the loopback interface.
        mcp.run(
            transport=args.transport,
            host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "8000")),
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
