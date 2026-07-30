# PCB Transition Checklist

Use when moving from breadboard / perfboard to first custom PCB.

## Minimum viable schematic checklist

- [ ] Power input protection (reverse polarity, TVS if needed)
- [ ] Decoupling capacitors on every IC (0.1 µF close to pins)
- [ ] Clear power nets: 3V3, 5V, GND, battery
- [ ] Test points on power, UART, SWD/JTAG, key signals
- [ ] Reset button / boot button if required by MCU
- [ ] USB connector footprint matches chosen type (USB-C preferred)
- [ ] Antenna keep-out (if RF) and matching notes
- [ ] Silkscreen labels for connectors and polarity

## First-PCB review checklist

- [ ] 2-layer is enough? (or 4-layer for dense / RF / power)
- [ ] Trace width for current (especially battery / motor)
- [ ] Via size and count under pads if needed
- [ ] Component packages: prefer 0805/0603 for hand soldering; 0402 only if required
- [ ] Fiducials if assembly house will be used
- [ ] Panelization notes if ordering >10
- [ ] DRC clean (clearance, silk, mask)
- [ ] Gerber + BOM + pick-and-place files ready

## Package size guidance (hand-solder friendly)

| Package | Hand solder | Notes |
|---------|-------------|-------|
| 1206 / 0805 | Easy | Resistors, caps for beginners |
| 0603 | Good | Most common sweet spot |
| 0402 | Hard | Avoid for first PCB |
| SOT-23 | Good | Transistors, LDOs |
| QFN / BGA | Needs stencil / hot air | Skip for first board unless necessary |

## Recommended free tools

- **KiCad** — primary, full-featured, offline
- **EasyEDA** — faster for beginners who want instant JLCPCB order
- Horizon EDA, LibrePCB, gEDA/pcb-rnd — alternatives if user prefers

Never push paid EDA unless user already uses it or has regulatory need.
