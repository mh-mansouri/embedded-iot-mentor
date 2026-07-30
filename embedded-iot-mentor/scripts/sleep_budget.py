#!/usr/bin/env python3
"""Rough battery runtime for a duty-cycled device, and what dominates the drain.

Takes the numbers a datasheet actually gives you rather than an average current,
which is the figure nobody knows up front and the usual reason a "two month"
battery lasts four days.

Example:
  python sleep_budget.py --capacity 2000 --active-ma 80 --active-ms 250 \\
                         --sleep-ua 15 --interval-s 600

Sleep current includes the regulator's quiescent draw, not just the MCU. See
references/power-and-battery-notes.md for typical figures.
"""

import argparse
import sys

# Rated capacity is measured under ideal conditions. Real designs lose to
# self-discharge, cold, and a cut-off voltage reached before the cell is empty.
DEFAULT_DERATE = 0.8


def fmt_duration(hours: float) -> str:
    if hours < 48:
        return f"{hours:.1f} h"
    days = hours / 24
    if days < 90:
        return f"{days:.1f} days"
    return f"{days:.0f} days ({days / 365:.1f} years)"


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--capacity", type=float, required=True,
                   help="battery capacity in mAh")
    p.add_argument("--active-ma", type=float, required=True,
                   help="current while awake, in mA")
    p.add_argument("--active-ms", type=float, required=True,
                   help="how long the device stays awake each cycle, in ms")
    p.add_argument("--sleep-ua", type=float, required=True,
                   help="current while asleep, in uA (MCU + regulator + sensors)")
    p.add_argument("--interval-s", type=float, required=True,
                   help="seconds between wake-ups")
    p.add_argument("--derate", type=float, default=DEFAULT_DERATE,
                   help=f"usable fraction of rated capacity (default {DEFAULT_DERATE})")
    args = p.parse_args()

    if args.interval_s <= 0 or args.capacity <= 0:
        print("error: --capacity and --interval-s must be greater than zero", file=sys.stderr)
        return 1

    active_s = args.active_ms / 1000
    if active_s > args.interval_s:
        print("error: the device is awake longer than the interval, so it never sleeps",
              file=sys.stderr)
        return 1

    duty = active_s / args.interval_s
    active_avg_ma = args.active_ma * duty
    sleep_avg_ma = (args.sleep_ua / 1000) * (1 - duty)
    avg_ma = active_avg_ma + sleep_avg_ma

    if avg_ma <= 0:
        print("error: average current came out at zero", file=sys.stderr)
        return 1

    raw_h = args.capacity / avg_ma
    derated_h = (args.capacity * args.derate) / avg_ma
    sleep_share = sleep_avg_ma / avg_ma

    print(f"{'Duty cycle':<22}{duty * 100:.3f} %  ({active_s:g} s awake every {args.interval_s:g} s)")
    print(f"{'Average current':<22}{avg_ma:.4f} mA")
    print(f"{'  from active':<22}{active_avg_ma:.4f} mA  ({(1 - sleep_share) * 100:.0f} %)")
    print(f"{'  from sleep':<22}{sleep_avg_ma:.4f} mA  ({sleep_share * 100:.0f} %)")
    print("-" * 52)
    print(f"{'Runtime (rated)':<22}{fmt_duration(raw_h)}")
    print(f"{'Runtime (x' + format(args.derate, 'g') + ' derate)':<22}{fmt_duration(derated_h)}")
    print()

    if sleep_share >= 0.5:
        print(f"Sleep dominates ({sleep_share * 100:.0f} %). Cutting sleep current beats")
        print("shortening the wake time. Check the regulator's quiescent draw first.")
    else:
        print(f"Active wake dominates ({(1 - sleep_share) * 100:.0f} %). Shorten the wake time,")
        print("drop the radio duty, or wake less often before chasing sleep current.")

    if derated_h / 24 / 365 > 3:
        print()
        print("Note: past ~3 years, self-discharge and shelf life matter more than this sum.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
