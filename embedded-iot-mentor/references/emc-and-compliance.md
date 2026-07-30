# EMC & Compliance Notes (glanceable)

## When this matters

| Stage | EMC effort |
|---|---|
| Breadboard MVP | None. Do not raise it. |
| First custom PCB | Design it in — free now, expensive later |
| Before selling, or fitting to a vehicle | Formal testing, and it gates shipping |

EMC is the most common reason a working prototype cannot be sold. The board does what
it should on the bench and still fails the scan.

## The two halves

- **Emissions** — what the device radiates or conducts out. This is what most first
  products fail.
- **Immunity** — what it tolerates coming in: ESD, surge, nearby transmitters. Usually
  easier, but ESD on exposed connectors catches people.

## What actually applies

| Market | Regime | Notes |
|---|---|---|
| EU | EMC Directive 2014/30/EU; **RED 2014/53/EU** if it has any radio | RED absorbs EMC, spectrum and safety for radio products |
| US | **FCC Part 15** — Subpart B unintentional radiators, Subpart C intentional | Class B (residential) is stricter than Class A |
| In or on a vehicle | **UN ECE R10** vehicle EMC approval | Separate from, and additional to, consumer EMC |
| Elsewhere | Usually mirrors one of the above | Confirm per market; do not assume |

## The single biggest lever: pre-certified modules

A radio **module** carries its own FCC ID or RED assessment. A bare radio chip means the
finished product needs full intentional-radiator testing — a five-figure difference at
low volume.

The catch: modular approval comes with conditions — the specified antenna, the specified
layout and keep-out, sometimes specified firmware. Deviate and the approval no longer
covers you. The end product still needs its own unintentional-emissions assessment
regardless.

## Why first boards fail

- **Switching regulator harmonics.** The commonest single cause. A buck at 500 kHz
  produces energy far up the spectrum.
- **Cables as antennas.** Long unshielded USB, sensor, or power leads radiate whatever
  noise is on them. Often the real emitter, not the PCB.
- **Broken ground plane.** Splitting or slotting the plane forces return current on a
  long detour, and that loop is the antenna.
- **No decoupling / large loops.** Every unbypassed IC and every big current loop.
- **Fast edges nobody needed.** A clock or driver far quicker than the application
  requires, radiating for nothing.

## Cheap hygiene, worth doing on any first PCB

- Solid, continuous ground plane; never route across a split.
- Decouple every IC, capacitor as close to the pin as the footprint allows.
- Keep high-current switching loops physically small.
- Ferrite bead or common-mode choke provision on cables entering or leaving.
- ESD protection (TVS) on anything a person or a connector can touch.
- Series termination pads on fast lines — cheap to fit, expensive to retrofit.
- Respect the module's antenna keep-out exactly (see `references/pcb-transition-checklist.md`).

## Testing and budget

- **Pre-compliance** — near-field probes and a cheap spectrum analyser on the bench, or a
  few hours booked at a test house. Finds most problems while they are still fixable.
- **Full test** — accredited lab, formal report. This is the figure in the certification
  row of `references/cost-estimation-guidelines.md`.
- Book pre-compliance **before** the enclosure and PCB are frozen. After that, the fixes
  left are shielding cans and ferrites, which cost per unit forever.

Always confirm current lab rates and the applicable standards for the target market;
they change, and they differ by product class.
