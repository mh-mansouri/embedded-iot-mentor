#!/usr/bin/env python3
"""Quick footprint / package advisability for hand assembly.

Usage:
  python footprint_hint.py 0603
  python footprint_hint.py QFN-32
"""

import sys

HINTS = {
    "1206": "Easy hand solder. Good for beginners.",
    "0805": "Easy hand solder. Recommended default for passives.",
    "0603": "Good hand solder with fine tip. Most common sweet spot.",
    "0402": "Hard by hand. Avoid on first PCB unless space forces it.",
    "0201": "Not practical by hand. Use only with stencil + reflow.",
    "sot-23": "Good hand solder. Common for transistors and small LDOs.",
    "sod-123": "Good hand solder.",
    "soic": "Good hand solder.",
    "ssop": "Possible with care; prefer wider pitch if available.",
    "tssop": "Challenging; flux + hot air or fine tip needed.",
    "qfn": "Needs stencil and hot air / reflow. Skip for first hand-assembled board if possible.",
    "qfp": "Doable with care and flux; still harder than SOIC.",
    "bga": "Not for hand assembly. Requires reflow and often X-ray.",
    "dip": "Easiest. Through-hole; use for early prototypes if size allows.",
}

def main() -> int:
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        print("Known keys (partial match):", ", ".join(sorted(HINTS)))
        return 0
    if not args:
        print("Usage: footprint_hint.py <package>", file=sys.stderr)
        print("Known keys (partial match):", ", ".join(sorted(HINTS)), file=sys.stderr)
        return 1

    # Accept "QFN 32" as well as "QFN-32"; normalising drops the separator anyway.
    query = " ".join(args).lower().strip()
    norm = lambda s: s.replace("-", "").replace(" ", "").replace("_", "")
    nq = norm(query)
    matches = [(k, v) for k, v in HINTS.items() if norm(k) in nq or nq in norm(k)]
    if not matches:
        # "note:" marks a miss, so a caller need not string-match the sentence.
        print(f"note: no built-in hint for '{query}'. Prefer 0805/0603 and SOT-23/SOIC for first boards.")
        return 0
    for k, v in matches:
        print(f"{k}: {v}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
