# Where the Data Is Seen (glanceable)

A reading nobody can look at is not a project. This is the last hop — sensor to a
person — and it is skipped more often than any other part of the plan.

Most builds need far less than they think here. The honest answer is usually an existing
dashboard the user already runs, or a page the device serves itself.

## Decide in this order

1. **Who looks, and from where?** In the same room, on the same network, or from
   anywhere. The third one is a different project from the first two.
2. **Live number, history, or an alert?** Three different builds. Most people asking for
   a dashboard want an alert and one current value.
3. **Is there an always-on box** — a Pi, a NAS, a home server — or does something hosted
   have to hold the data?
4. **How often, times how many nodes, kept for how long?** That triple decides whether
   any free tier survives contact with the project.
5. Only then pick a tool.

## Viewing routes

| Route | Seen on | Needs | Ongoing cost | Effort | Use when |
|---|---|---|---|---|---|
| **Device's own web page** | Browser, same Wi-Fi | Wi-Fi board | None | Very low — built into ESPHome, Tasmota, WLED | One device, live values, no history wanted |
| **BLE + an existing phone app** | Phone, in range | Nothing else | None | Very low if a vendor or generic app fits | One person, occasional readings, no gateway |
| **Home Assistant (self-hosted)** | Phone app, browser, PC | Always-on box | Electricity | Low with ESPHome, medium otherwise | The default whenever there is a home network: dashboard, history and alerts in one |
| **MQTT broker + Node-RED** | Anything that subscribes | Always-on box | Electricity | Medium | Several devices, custom logic, or other systems to feed |
| **InfluxDB + Grafana** | Browser, PC or phone | Always-on box with real RAM | Electricity | Medium–high | Long history, many series, charts that must look right |
| **Hosted IoT dashboard** — ThingSpeak, Adafruit IO, Datacake, Ubidots, Blynk | Browser + vendor app | Account, internet at the device | Free tier, then paid | Lowest of the internet routes | No always-on box, few devices, tier limits acceptable |
| **LoRaWAN network server** — TTN or ChirpStack, feeding one of the above | Whatever consumes the webhook | A gateway | Free (TTN fair-use policy) | Medium | The link is already LoRaWAN |
| **SD card / local log, collected by hand** | PC, afterwards | Card slot, RTC | None | Lowest overall | Data is a study, not a display. No radio needed at all |
| **Custom app or custom web app** | Anything | A backend, a developer, app-store accounts | Hosting + store fees | Highest by a wide margin | Nothing else fits, and the users are not the builder |

**A custom mobile app is almost never the MVP answer.** It is months of work, two
platforms, store review, and a backend, to show numbers an existing dashboard shows
today. Say that before it gets designed in, not after.

## Traps worth stating out loud

- **"On my phone" hides "from anywhere".** In the house is a LAN dashboard and costs
  nothing. Away from the house means remote access: a VPN or mesh (WireGuard, Tailscale),
  a tunnel, or a hosted service. **Never a port forward to a hobby device.**
- **Free tiers have edges, and the sampling rate finds them.** Minimum update interval,
  retention window, device count, message quota. Check the boundary against the project's
  real rate before promising it, and check what an over-limit month costs.
- **An alert is not a dashboard.** If the goal is "tell me when the tank is low", build the
  notification and skip the charts. Ready-made firmware plus Home Assistant does this with
  no code.
- **Retention is a decision, not a default.** One reading every 10 s per node, kept
  forever, is a database problem within a year. Downsample old data or set a window.
- **The always-on box is a real cost and a single point of failure.** A Pi on a cheap SD
  card will lose the history; use a good card or an SSD, and back the config up.
- **Buffer on the device, or outages become holes.** A node that only streams loses
  everything while the link is down. A few hours of readings in RAM or flash, replayed on
  reconnect, is cheap and turns a gap into a delay.
- **Whose clock?** Devices lose time across sleep and reset; server-side timestamps look
  fine until a batch arrives late and lands in the wrong minute. Pick one and know its
  failure mode.
- **Services shut down and licences change.** Prefer a route whose data can be exported —
  self-hosted, or hosted with a working export. A dashboard that cannot be left is a
  dependency, not a feature.

## Security minimums for anything reachable off the LAN

- No default or shared passwords, and one credential per device.
- **No plain MQTT over the internet.** TLS, or keep the broker inside a VPN.
- A dashboard that is reachable is also scannable — assume it will be found.
- **Occupancy, health, and location data are about a person.** Whether that goes on the
  public internet is the user's decision to make deliberately, not a default of the
  chosen platform.

## Cost lines this adds

Fold these into the running-cost table in `references/cost-estimation-guidelines.md`
rather than the BOM: platform subscription per device, cloud storage above the free tier,
the always-on box's electricity, and any app-store account fee. For the radio link's own
subscription — a SIM — see `references/connectivity-modules.md`.

## Where this guidance stops

Multiple tenants, accounts for users who are not the builder, or personal data under GDPR
or similar law is backend and legal work, not a dashboard choice. Say so plainly and stop
there rather than sketching an architecture the user cannot maintain.
