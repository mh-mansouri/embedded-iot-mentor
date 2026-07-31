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

## Cost to run (quote this whenever the device gets left somewhere)

Build cost is a one-off; running cost repeats for as long as the thing is useful. For a
deployed build — especially several nodes — it is the number that decides the design.

| Line | Ask | Typical shape |
|---|---|---|
| Batteries | Cells per node × nodes × replacements per year | Small per node, real at ten nodes |
| Subscription | SIM or platform fee, per device, per month | The line that dwarfs the BOM over three years |
| Gateway / receiver | Bought once, or already owned? | Owning it means no recurring fee at all |
| Cloud / storage | Free tier now, priced tier at what volume? | Check the tier boundary, not today's bill |
| Replacement | What fraction is lost per year to weather, machinery, animals, theft? | Assume non-zero outdoors |

Two moves worth naming explicitly when the yearly figure looks bad:

- **Solar swaps a recurring cost for a one-off** — a small panel per node usually pays for
  itself inside two years and removes the visit as well as the cell.
- **Owning the receiver removes the subscription entirely.** A gateway or mesh you run
  yourself has no per-device fee; a carrier does, forever.

Present it as its own small table with a per-year column. Do not fold it into the BOM
total — they are different decisions, and merging them hides both.

## PCB fab quick reference (prototype)

| Fab | Strength | Typical 5-pc 2-layer |
|-----|----------|---------------------|
| JLCPCB | Cheap, fast, parts assembly | $5–25 + shipping |
| PCBWay | Similar, good support | Comparable |
| Local / regional | Faster shipping, higher unit | Varies by country |

For concrete pricing always check current LCSC / Digi-Key / Mouser / local distributors when the user asks for a real estimate. Do not embed large BOM price tables.

## Script helper

A simple cost-calculator script lives in `scripts/cost_estimator.py`. Use it when the user supplies a short BOM list.
