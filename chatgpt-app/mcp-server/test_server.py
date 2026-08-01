#!/usr/bin/env python3
"""Tests for the connector, run in CI.

    python chatgpt-app/mcp-server/test_server.py

The connector is the one port with moving parts: it ranks documents, shells out
to the skill's scripts, and answers over a protocol whose shapes ChatGPT is
strict about. All three break silently — a ranking change sends every query to
the same file, a renamed script raises only when someone asks for a number.

No pytest. The repository's other gates are plain scripts that exit non-zero,
and a test suite that needs an install is a test suite that stops being run.
"""

from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import server  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{' — ' + detail if detail else ''}")
        FAILURES.append(name)


def section(title: str) -> None:
    print(f"\n{title}")


# --------------------------------------------------------------------------
# search ranking
#
# The weighting exists because worked-examples.md touches every topic and would
# otherwise answer every query. Each row is a question someone would actually
# ask, and the file that should come back first.
# --------------------------------------------------------------------------

RANKING = [
    ("how long will a coin cell last", "power-and-battery-notes"),
    ("LoRa range in a field", "field-deployment-notes"),
    ("OTA update", "ota-update-notes"),
    ("soldering a QFN by hand", "pcb-transition-checklist"),
    ("what does this cost", "cost-estimation-guidelines"),
    ("grafana dashboard on my phone", "data-and-dashboards"),
    ("CE marking and EMC", "emc-and-compliance"),
    ("medical device safety", "functional-safety-boundary"),
    ("which microcontroller should I pick", "mcu-selection-cheatsheet"),
    ("wifi module antenna", "connectivity-modules"),
    ("where do I learn this", "learning-resources"),
]


def test_search_ranking() -> None:
    section("search ranking")
    for query, expected in RANKING:
        results = server.search(query)["results"]
        top = results[0]["id"] if results else None
        check(f"{query!r} -> {expected}", top == expected, f"got {top}")


def test_worked_examples_does_not_dominate() -> None:
    section("worked-examples stays out of the way")
    # It is the longest file and mentions everything. If length normalisation
    # regresses, it climbs to the top of every one of these.
    tops = [server.search(q)["results"][0]["id"] for q, _ in RANKING]
    check(
        "never first for a topic query",
        "worked-examples" not in tops,
        f"first for {tops.count('worked-examples')} of {len(tops)} queries",
    )


def test_search_shape() -> None:
    section("search/fetch response shapes (ChatGPT is strict about these)")
    results = server.search("battery")["results"]
    check("returns at most 5", len(results) <= 5, f"got {len(results)}")
    check("every result has id, title, url",
          all({"id", "title", "url"} <= set(r) for r in results))
    check("urls are absolute", all(r["url"].startswith("https://") for r in results))
    check("no empty titles", all(r["title"].strip() for r in results))


def test_every_search_hit_is_fetchable() -> None:
    section("search ids round-trip through fetch")
    # A result ChatGPT cannot fetch is a dead citation.
    for doc_id in server._docs():
        doc = server.fetch(doc_id)
        ok = doc["id"] == doc_id and doc["text"].strip() and doc["url"].startswith("https://")
        check(f"fetch({doc_id})", bool(ok))


def test_fetch_rejects_unknown() -> None:
    section("fetch refuses an id it does not have")
    try:
        server.fetch("no-such-document")
        check("raises on unknown id", False, "returned instead of raising")
    except ValueError as exc:
        check("raises on unknown id", "call search first" in str(exc), str(exc))


# --------------------------------------------------------------------------
# calculators
#
# These shell out to the skill's own scripts. The point of the connector is
# that a number quoted through ChatGPT is the number the skill would quote, so
# the numbers are asserted, not just the exit status.
# --------------------------------------------------------------------------


def test_battery_runtime_matches_the_readme_claim() -> None:
    section("battery_runtime")
    # The README's headline: same firmware, same battery, sleep current 15 uA
    # against a dev board's 8 mA regulator. If these two numbers move, the
    # README is making a claim the tool no longer supports.
    good = server.battery_runtime(capacity_mah=2000, active_ma=80, active_ms=250,
                                  sleep_ua=15, interval_s=600)
    bad = server.battery_runtime(capacity_mah=2000, active_ma=80, active_ms=250,
                                 sleep_ua=8000, interval_s=600)
    check("15 uA sleep -> 3.8 years", "3.8 years" in good, good.splitlines()[-1])
    check("8 mA sleep -> 8.3 days", "8.3 days" in bad, bad.splitlines()[-1])
    check("names the dominant term", "dominates" in good and "dominates" in bad)


def test_estimate_bom_cost() -> None:
    section("estimate_bom_cost")
    out = server.estimate_bom_cost([
        {"qty": 1, "unit_price": 4.50, "description": "ESP32 DevKit"},
        {"qty": 10, "unit_price": 0.12, "description": "10k resistor"},
    ])
    check("totals the lines", "5.7000" in out, out.splitlines()[-1])
    check("keeps the descriptions", "ESP32 DevKit" in out and "10k resistor" in out)

    # A bare number as a description silently becomes the next line item's
    # quantity, which is a wrong total rather than an error.
    try:
        server.estimate_bom_cost([{"qty": 1, "unit_price": 2.0, "description": "2200"}])
        check("rejects a bare-number description", False, "accepted it")
    except ValueError as exc:
        check("rejects a bare-number description", "bare number" in str(exc), str(exc))

    try:
        server.estimate_bom_cost([])
        check("rejects an empty BOM", False, "accepted it")
    except ValueError:
        check("rejects an empty BOM", True)

    try:
        server.estimate_bom_cost([{"unit_price": 2.0, "description": "no qty"}])
        check("rejects an item with no qty", False, "accepted it")
    except ValueError:
        check("rejects an item with no qty", True)


def test_hand_solder_hint() -> None:
    section("hand_solder_hint")
    check("0603 is workable", "hand solder" in server.hand_solder_hint("0603").lower())
    check("BGA is not", "not for hand assembly" in server.hand_solder_hint("BGA").lower())


def test_no_shell_injection() -> None:
    section("script arguments are argv, never a shell string")
    # A description is user text arriving from a model. If it were ever joined
    # into a shell command, this would run rather than print.
    out = server.estimate_bom_cost(
        [{"qty": 1, "unit_price": 1.0, "description": "10k resistor; echo pwned"}]
    )
    check("semicolon survives as text", "echo pwned" in out)
    check("nothing executed", "pwned\n" not in out.replace("echo pwned", ""))


# --------------------------------------------------------------------------
# wiring
# --------------------------------------------------------------------------


def test_mentor_guidance_is_the_shared_instructions() -> None:
    section("mentor_guidance")
    text = server.mentor_guidance()
    on_disk = server.INSTRUCTIONS.read_text(encoding="utf-8")
    check("returns instructions.md verbatim", text == on_disk)
    check("carries the MVP rule", "MVP" in text)


def test_version_follows_the_skill() -> None:
    section("version")
    skill_md = (server.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    expected = re.search(r'^\s+version:\s*"([^"]+)"', skill_md, re.M).group(1)
    check(f"server reports {expected}", server._skill_version() == expected,
          server._skill_version())


def test_registry_metadata_matches_the_skill() -> None:
    section("server.json (the MCP registry listing)")
    import json

    root = Path(__file__).resolve().parents[2]
    entry = json.loads((root / "server.json").read_text(encoding="utf-8"))
    skill_md = (server.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    version = re.search(r'^\s+version:\s*"([^"]+)"', skill_md, re.M).group(1)

    # A registry listing that advertises a version nobody can pull is worse
    # than no listing, and the image tag comes from the same tag as the skill.
    check("version follows the skill", entry["version"] == version, entry["version"])
    # OCI packages carry the version in the image reference and are rejected if
    # they also carry a `version` field, so the tag is the thing to check.
    tags = [p["identifier"].rsplit(":", 1)[-1] for p in entry["packages"]]
    check("image tag follows the skill", all(t == version for t in tags), str(tags))
    check("no package repeats the version outside its tag",
          all("version" not in p for p in entry["packages"]))
    # The registry rejects anything longer, and only at submission time.
    check("description within the registry's 100 characters",
          len(entry["description"]) <= 100, f"{len(entry['description'])} chars")


def test_healthz() -> None:
    section("/healthz")
    import asyncio

    response = asyncio.run(server.healthz(None))
    check("200 while the skill folder is present", response.status_code == 200,
          str(response.status_code))


def test_every_tool_is_documented() -> None:
    section("tool docstrings (they are the model's only instructions)")
    tools = [server.mentor_guidance, server.search, server.fetch,
             server.estimate_bom_cost, server.hand_solder_hint, server.battery_runtime]
    for tool in tools:
        doc = inspect.getdoc(tool) or ""
        check(f"{tool.__name__} has a usable description", len(doc) > 40, f"{len(doc)} chars")


def main() -> int:
    print(f"connector tests — skill folder {server.SKILL_DIR}")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {', '.join(FAILURES)}")
        return 1
    print("all connector checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
