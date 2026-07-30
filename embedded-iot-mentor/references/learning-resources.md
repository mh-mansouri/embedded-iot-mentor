# Learning Resources (high-level)

Point users to free, high-quality material only when they ask or when a clear knowledge gap appears. Keep lists short.

## Electronics basics

- Kirchhoff, Ohm, voltage dividers, pull-ups
- How to read a datasheet (absolute max, recommended operating, timing)
- Multimeter + cheap logic analyzer / USB-UART

## Firmware / programming

| Path | Good starting points |
|------|----------------------|
| Arduino-style | Official Arduino docs + PlatformIO docs |
| ESP32 | Espressif docs + ESP-IDF getting started (or Arduino core) |
| STM32 | STM32CubeIDE / CubeMX tutorials, then bare-metal or HAL |
| RP2040 | Raspberry Pi Pico C/C++ SDK or MicroPython docs |
| General embedded C | "Making Embedded Systems" concepts, interrupt vs polling |

## PCB / schematic

- KiCad official documentation and FAQ
- JLCPCB / PCBWay capabilities pages (stack-up, tolerances)
- Basic DFM: annular rings, trace/space, solder mask

## Parts selection

- Prefer parts with good stock on LCSC + Digi-Key / Mouser
- Check package, temperature range, and longevity (not NRND)
- For cost estimates at PCB stage, query current distributor prices; do not hard-code large tables

## PCB fabrication by region (examples)

| Region | Common cheap/fast options |
|--------|---------------------------|
| Global / China | JLCPCB, PCBWay |
| Europe | Aisler, Eurocircuits, local makerspaces |
| US | OSH Park, PCBWay/JLCPCB (shipping), local quick-turn |
| Other | Search "PCB prototype [country]" + check lead time |

Always confirm current pricing and shipping; suggest the user pick the fab that minimizes total time-to-board for their location.
