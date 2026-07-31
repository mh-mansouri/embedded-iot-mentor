# Field Deployment Notes (glanceable)

For anything that lives outside a room. On a desk the enclosure is a nicety; in a field
it is most of the engineering, and it is where working prototypes die.

Ask first: **where exactly does it sit, what walks past it, and who fetches it when it
stops?** A node 400 m across a wet meadow is a different product from the same board on
a windowsill.

## IP ratings, only the ones worth naming

| Rating | Means | Use for |
|---|---|---|
| IP54 | Dust-limited, splashes | Sheltered, under an eave — not open weather |
| **IP65** | Dust-tight, low-pressure jets | The sane default outdoors: rain, hose, snow |
| IP67 | Dust-tight, 30 min at 1 m immersion | Ground level, flooding, snow burial |
| IP68 | Continuous immersion | Submerged sensors. Rare, and the cable is the hard part |

A rating belongs to the **assembly**, not the box. One unsealed hole and IP65 is IP00.

## Sealing rules

- **Cable glands, never tape or silicone.** A gland matched to the cable diameter is a
  few coins and is the single highest-return part in an outdoor build.
- **Glands and drains on the underside.** Water finds the top face first.
- **Drip loop below the entry** so run-off leaves the cable before the gland.
- **Vent, or condensation does the damage instead of rain.** A sealed box with a day/night
  temperature swing rains on its own PCB. Use a GORE-style breather vent, or accept IP54
  with a drain hole at the lowest point. Silica gel is a delaying tactic, not a fix.
- **Conformal coating** on the board once the design is settled — cheap insurance against
  the humidity that gets in anyway.
- **UV kills cheap plastic.** ABS chalks and cracks in a season or two; ASA, PC, or
  polycarbonate boxes hold up. A 3D-printed PLA case is an indoor part.

## Mounting

| Concern | Rule |
|---|---|
| Height | Above splash, snow line, and mowers. 1.2–1.5 m on a post is the usual answer |
| Animals | They rub far harder than they chew. Nothing loose at nose height; cable down the post inside conduit |
| Machinery | Strimmers and mowers destroy more field nodes than weather does. Mark the post |
| Metal | An antenna inside a metal box has no range. Non-metallic enclosure, or antenna outside on a bulkhead connector |
| Ground contact | Anything buried or at soil level corrodes at the connector first. Bring the cable up; keep the electronics off the ground |
| Theft & curiosity | A visible box in a public space walks away. Plain, unlabelled, hard to unbolt |

## Environment that changes the electrical design

- **Cold flattens batteries.** Alkaline cells lose most of their usable capacity near
  freezing; lithium primary (Li-FeS₂) and LiFePO₄ hold up. Never charge a normal LiPo
  below 0 °C — a charger without a temperature cut-off will damage it in winter.
- **Heat shortens them.** A dark box in summer sun runs 20–30 °C above ambient; derate
  battery life and check the part's rated maximum, not the typical figure.
- **Solar is sized by the worst month, not the average.** December in northern Europe is
  a small fraction of June. Oversize the panel or accept a seasonal battery swap.
- **Wet ground detunes antennas** and absorbs signal. Range measured across a dry car park
  is not the range across a soaked meadow; test in the conditions that matter.

## Servicing — decide this before deployment, not after

- How do you know a node stopped? A missing reading must be visible, or a dead node is
  discovered by the season's data being wrong.
- How is firmware changed once it is on the post? If the answer is "fetch the ladder",
  see `references/ota-update-notes.md` before sealing anything.
- Label each node, and keep a note of which one is where. Six identical boxes across a
  site become unidentifiable within a month.
- Assume the first field revision is wrong. Deploy one node, leave it a fortnight through
  real weather, then build the rest.
