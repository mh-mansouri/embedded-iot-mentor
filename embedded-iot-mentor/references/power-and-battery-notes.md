# Power & Battery Notes (glanceable)

## LiPo basics

- Always use a protection circuit (over-charge, over-discharge, over-current). Many packs include it.
- Charge with a proper LiPo charger IC (TP4056 class is common for 1S).
- Never charge unattended on a desk without fire-safe area.
- Typical 1S LiPo: 3.7 V nominal, 4.2 V full, cut-off ~3.0–3.3 V.

## Regulator choice

| Situation | Prefer | Why |
|-----------|--------|-----|
| Battery → 3.3 V, low current (<100 mA), simple | LDO | Cheap, quiet, tiny |
| Higher current or bigger Vin–Vout gap | Buck (switching) | Far better efficiency → longer battery |
| Need both 5 V and 3.3 V | Buck to 5 V + LDO to 3.3 V | Or dual buck |
| Ultra-low sleep current | Check LDO/buck quiescent | Many LDOs waste 50–150 µA; choose <5–10 µA if sleep matters |

## Typical quiescent currents (order of magnitude)

| Part type | Iq range | Impact on battery |
|-----------|----------|-------------------|
| Good LDO | 1–10 µA | Weeks–months extra |
| Average LDO | 50–150 µA | Noticeable drain |
| Buck (light load) | 10–50 µA (PFM) | Usually better overall |
| ESP32 deep sleep | ~10–20 µA + peripherals | Dominated by sensors / regulators |
| nRF52 deep sleep | ~1–5 µA | Excellent for coin / small LiPo |

## Quick rules

- Measure real sleep current on the breadboard before designing the PCB.
- Add a power switch or load switch for shipping / storage.
- Decouple every rail; put bulk + ceramic near the regulator output.
- For solar / energy harvest, add proper MPPT or simple diode + capacitor only after basic battery path works.
