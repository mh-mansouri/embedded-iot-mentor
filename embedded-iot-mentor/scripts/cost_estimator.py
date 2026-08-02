#!/usr/bin/env python3
"""Tiny BOM cost estimator. Pass lines of: qty,unit_price[,description]

Two forms, mixable:
  python cost_estimator.py 1 4.50 "ESP32 DevKit" 10 0.12 "10k resistor"
  python cost_estimator.py "1,4.50,ESP32 DevKit" "10,0.12,10k resistor, 1%"

The comma form is unambiguous. Use it when a description could be read as a
number ("2024") or contains a comma; the spaced form guesses by "not a number".
"""

import sys

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return

    args = sys.argv[1:]
    total = 0.0
    rows = []
    i = 0
    while i < len(args):
        try:
            if "," in args[i]:
                qty, price, desc = _split_line(args[i])
                i += 1
            else:
                qty = float(args[i])
                price = float(args[i + 1])
                desc = ""
                i += 2
                if i < len(args) and not _is_number(args[i]):
                    desc = args[i]
                    i += 1
            line = qty * price
            total += line
            rows.append((qty, price, line, desc))
        except (IndexError, ValueError):
            print("Usage: qty unit_price [description] ...", file=sys.stderr)
            print('Tip: quote each line, e.g. "1,4.50,ESP32 DevKit"', file=sys.stderr)
            sys.exit(1)

    print(f"{'Qty':>8} {'Unit':>10} {'Line':>10}  Description")
    print("-" * 50)
    for qty, price, line, desc in rows:
        print(f"{qty:8.1f} {price:10.4f} {line:10.4f}  {desc}")
    print("-" * 50)
    print(f"{'TOTAL':>8} {'':>10} {total:10.4f}")

def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

def _split_line(token: str):
    parts = [p.strip() for p in token.split(",", 2)]
    if len(parts) < 2:
        raise ValueError("need qty,unit_price")
    return float(parts[0]), float(parts[1]), (parts[2] if len(parts) > 2 else "")

if __name__ == "__main__":
    main()
