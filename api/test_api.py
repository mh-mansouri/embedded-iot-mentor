#!/usr/bin/env python3
"""Tests for the REST port, run in CI.

    python api/test_api.py

The API's own logic is thin — models, argument building, and error mapping — but
each part fails silently. A renamed flag reaches the caller as a 400 that reads
like their mistake, and a reference file that stops being listed just disappears.

No pytest, and the routes are called as plain functions, so this needs nothing
the API itself does not already need. Same reasoning as the connector's tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import HTTPException  # noqa: E402
from pydantic import ValidationError  # noqa: E402

from api import main  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{' — ' + detail if detail else ''}")
        FAILURES.append(name)


def section(title: str) -> None:
    print(f"\n{title}")


def rejects(name: str, fn) -> None:
    """A model or route that must refuse its input."""
    try:
        fn()
    except (ValidationError, HTTPException):
        check(name, True)
    else:
        check(name, False, "accepted")


section("wiring")
check("skill dir exists", main.SKILL_DIR.is_dir(), str(main.SKILL_DIR))
check("scripts dir exists", main.SCRIPTS_DIR.is_dir())
check("instructions found", main.INSTRUCTIONS.is_file())
check("version parsed", main.skill_version() != "unknown", main.skill_version())
for key, filename in main.SCRIPTS.items():
    check(f"script present: {filename}", (main.SCRIPTS_DIR / filename).is_file())

section("references")
names = main.list_references()["references"]
check("references listed", len(names) >= 10, str(len(names)))
check("a known doc is listed", "power-and-battery-notes" in names)
check("reads a doc", "battery" in main.get_reference("power-and-battery-notes").lower())
rejects("traversal rejected", lambda: main.get_reference("../SKILL"))
rejects("unknown doc rejected", lambda: main.get_reference("nope"))

section("search")
hits = main.search(q="battery", limit=5)
check("finds something", len(hits["hits"]) > 0)
check("respects limit", len(hits["hits"]) <= 5)
check("reports a line number", all(h["line"] > 0 for h in hits["hits"]))
check("misses cleanly", main.search(q="zzzznotathing")["hits"] == [])

section("cost")
out = main.cost(main.CostRequest(items=[
    {"qty": 1, "unit_price": 4.5, "description": "ESP32 DevKit"},
    {"qty": 10, "unit_price": 0.12, "description": "2024"},
]))
check("totals correctly", "5.7000" in out, out)
# The spaced form would have read "2024" as the next quantity.
check("numeric description survives", "2024" in out)
rejects("empty BOM rejected", lambda: main.CostRequest(items=[]))
rejects("zero quantity rejected", lambda: main.CostItem(qty=0, unit_price=1))

section("sleep budget")
good = dict(capacity_mah=2000, active_ma=80, active_ms=250, sleep_ua=15, interval_s=600)
out = main.sleep_budget(main.SleepRequest(**good))
check("reports a runtime", "Runtime (rated)" in out, out)
check("names the dominant drain", "dominates" in out)
rejects("derate above 1 rejected", lambda: main.SleepRequest(**good, derate=1.5))
rejects("derate of 0 rejected", lambda: main.SleepRequest(**good, derate=0))
rejects("negative current rejected", lambda: main.SleepRequest(**{**good, "active_ma": -80}))
# Caught by the script, not the model: the two values are legal on their own.
rejects("awake longer than interval rejected",
        lambda: main.sleep_budget(main.SleepRequest(**{**good, "active_ms": 700_000})))

section("footprint")
hit = main.footprint(main.FootprintRequest(package="QFN 32"))
check("matches a known package", hit["matched"] and "qfn" in hit["hint"], str(hit))
miss = main.footprint(main.FootprintRequest(package="banana"))
check("reports a miss as a miss", miss["matched"] is False, str(miss))
check("miss still advises", "0805" in miss["hint"])
rejects("flag-like package rejected", lambda: main.FootprintRequest(package="--help"))


section("guardrails")
check("open by default", main.API_KEY == "")
check("no CORS origins by default", main.CORS_ORIGINS == [])
check("health check needs no key", "/healthz" in main.OPEN_PATHS)


class _FakeRequest:
    """Only the two attributes _client_ip touches."""

    def __init__(self, headers: dict, peer: str | None = "10.0.0.1"):
        self.headers = headers
        self.client = type("C", (), {"host": peer})() if peer else None


check("client ip from the socket",
      main._client_ip(_FakeRequest({})) == "10.0.0.1")
# Behind a proxy every caller shares one socket peer, so the header wins.
check("proxy header wins",
      main._client_ip(_FakeRequest({"x-forwarded-for": "203.0.113.7, 10.0.0.1"})) == "203.0.113.7")
check("blank header ignored",
      main._client_ip(_FakeRequest({"x-forwarded-for": "  "})) == "10.0.0.1")

original_limit = main.RATE_LIMIT_PER_MIN
main.RATE_LIMIT_PER_MIN = 3
try:
    ip = "198.51.100.9"  # documentation range, so no real bucket is disturbed
    allowed = [main._within_rate_limit(ip) for _ in range(5)]
    check("allows up to the limit", allowed[:3] == [True, True, True], str(allowed))
    check("blocks past the limit", allowed[3:] == [False, False], str(allowed))
    check("a different caller is unaffected", main._within_rate_limit("198.51.100.10"))
finally:
    main.RATE_LIMIT_PER_MIN = original_limit
    main._hits.clear()

original_timeout = main.SCRIPT_TIMEOUT_S
main.SCRIPT_TIMEOUT_S = 0.2  # the wait for a free slot; keeps the test quick
held = [main._script_slots.acquire() for _ in range(main.MAX_CONCURRENT_SCRIPTS)]
try:
    check("all slots can be taken", all(held))
    try:
        main.run_script("footprint", ["0805"])
        check("refuses when full", False, "ran anyway")
    except HTTPException as exc:
        check("refuses when full", exc.status_code == 503, str(exc.status_code))
finally:
    for _ in held:
        main._script_slots.release()
    main.SCRIPT_TIMEOUT_S = original_timeout

check("slots are given back", main.run_script("footprint", ["0805"]).startswith("0805"))


section("chat")
check("off by default", main.ANTHROPIC_API_KEY == "")
rejects("no key means 501", lambda: main._claude())

# _run_chat_tool goes through the same models/scripts as the REST routes —
# no network call, so this runs without a key.
out, is_error = main._run_chat_tool("cost_estimate", {"items": [{"qty": 2, "unit_price": 1.5}]})
check("cost tool matches the route", "3.0000" in out and not is_error, out)
out, is_error = main._run_chat_tool("footprint_hint", {"package": "0805"})
check("footprint tool matches the route", out.startswith("0805") and not is_error, out)
out, is_error = main._run_chat_tool("sleep_budget", {**good, "active_ms": 700_000})
check("tool errors come back as text, not an exception", is_error and "error:" in out, out)
out, is_error = main._run_chat_tool("not_a_real_tool", {})
check("unknown tool named in the error", is_error and "not_a_real_tool" in out, out)

original_chat_limit = main.CHAT_RATE_LIMIT_PER_MIN
main.CHAT_RATE_LIMIT_PER_MIN = 2
try:
    ip = "198.51.100.11"  # documentation range, so no real bucket is disturbed
    allowed = [main._within_chat_rate_limit(ip) for _ in range(4)]
    check("chat limit is its own bucket", allowed == [True, True, False, False], str(allowed))
    check("calculator bucket is unaffected", main._within_rate_limit(ip))
finally:
    main.CHAT_RATE_LIMIT_PER_MIN = original_chat_limit
    main._chat_hits.clear()
    main._hits.clear()


print()
if FAILURES:
    print(f"{len(FAILURES)} failed: {', '.join(FAILURES)}")
    sys.exit(1)
print("all passed")
