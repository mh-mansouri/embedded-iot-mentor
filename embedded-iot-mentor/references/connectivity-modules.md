# Connectivity Choice (glanceable)

Pick the **link** first, the module second. The link decides battery life, running
cost, and certification burden; swapping it later usually means redesigning the board.

## Decide in this order

1. Does data have to leave the building? If not, BLE or wired wins on cost and power.
2. Is there mains power at the sensor? If yes, Wi-Fi stops being a problem.
3. Who owns the infrastructure — the user's phone, their router, a gateway they must
   buy, or a carrier they must pay monthly?
4. Only then choose a module.

## Links by criteria

| Link | Typical range | Draw while sending | Needs | Ongoing cost | Cert burden | Use when |
|------|---------------|--------------------|-------|--------------|-------------|----------|
| **BLE** | 10–50 m | 5–15 mA, ms bursts | A phone or a hub | None | Low (pre-certified modules) | Phone is the UI; data is small and occasional |
| **Wi-Fi** | 30–50 m indoors | 100–300 mA bursts | Existing router | None | Low (modules) | Mains power or frequent large payloads |
| **LoRa (P2P)** | 1–5 km | 40–120 mA, short TX | Your own second radio | None | Low–medium (duty-cycle limits) | Two fixed points, no internet needed |
| **LoRaWAN** | 2–15 km | 40–120 mA, short TX | Gateway (yours or public) | Free–low | Medium (regional bands) | Battery sensors spread over a site |
| **NB-IoT / LTE-M** | Carrier coverage | 100–300 mA bursts | SIM + carrier | Monthly per device | High (carrier + regional approval) | No gateway possible, small payloads, years on battery |
| **LTE Cat-1 / 4G** | Carrier coverage | 500 mA–2 A peaks | SIM + carrier | Monthly, higher | High | Real bandwidth in the field; mains or big battery |
| **Zigbee / Thread / Matter** | 10–100 m, meshes | 10–30 mA | Hub / border router | None | Medium (interop certification) | Joining an existing smart-home ecosystem |
| **Wired (Ethernet, RS-485)** | 100 m / 1 km | Steady, modest | Cable run | None | Lowest | Cable is possible and reliability matters most |

## Traps worth stating out loud

- **Peak current, not average, kills the design.** Cellular peaks of 1–2 A brown out a
  small LiPo or a weak regulator. Size the supply and add bulk capacitance for the peak.
- **Cellular costs money forever.** A subscription per device changes the business case
  more than any BOM line. Say so before recommending it.
- **Radio bands are regional.** LoRa is 868 MHz in Europe, 915 MHz in the Americas,
  and elsewhere varies. Confirm the user's country before naming a part.
- **Wi-Fi and battery rarely mix.** Association and DHCP dominate the wake budget;
  check with `scripts/sleep_budget.py` before promising a runtime.
- **Pre-certified module vs bare chip.** A module carries its own radio approval. A bare
  chip means the finished product needs full testing — a real cost at low volume.

## Modules

Named modules go stale fast, so treat any specific part as an example to verify, not a
recommendation. Choose by these properties instead:

- Pre-certified for the user's region, and still in production (not NRND).
- Castellated or through-hole footprint if the board will be hand-assembled.
- A maintained driver or AT-command library for the chosen MCU and toolchain.
- Stocked by a distributor the user can actually order from (see their region).

Check current stock on LCSC, Digi-Key, or Mouser at the moment of recommending, and
prefer the module family the vendor's own dev board uses — the examples will match.
