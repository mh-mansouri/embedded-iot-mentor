# Cost Estimation Guidelines

Use ranges. Always separate parts, tools, PCB, and certification.

## Typical solo project ranges (USD, 2024–2026 ballpark)

| Stage | Effort (solo) | Parts only | Notes |
|-------|---------------|------------|-------|
| Breadboard MVP | 1–5 days | $15–60 | Dev board + sensors + wires |
| Refined prototype | 1–3 weeks | $30–120 | Better power, connectors, enclosure mock |
| First custom PCB (5–10 pcs) | 1–4 weeks | $20–80 (fab + parts) | JLCPCB / PCBWay 2-layer |
| Small run (50–200) | +2–6 weeks | Depends on BOM | Assembly optional; test jig needed |
| Certification (FCC/CE) | — | $2k–15k+ | Flag as risk; not required for personal MVP |

## Major cost drivers

- RF modules / cellular modem
- Display or high-end sensor
- Custom enclosure / mechanical
- Battery + protection + charging
- Assembly (hand vs pick-and-place)
- Shipping and tariffs

## PCB fab quick reference (prototype)

| Fab | Strength | Typical 5-pc 2-layer |
|-----|----------|---------------------|
| JLCPCB | Cheap, fast, parts assembly | $5–25 + shipping |
| PCBWay | Similar, good support | Comparable |
| Local / regional | Faster shipping, higher unit | Varies by country |

For concrete pricing always check current LCSC / Digi-Key / Mouser / local distributors when the user asks for a real estimate. Do not embed large BOM price tables.

## Script helper

A simple cost-calculator script lives in `scripts/cost_estimator.py`. Use it when the user supplies a short BOM list.
