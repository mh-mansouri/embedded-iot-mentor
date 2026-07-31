# Worked examples

Four scenarios showing the skill applied end to end. People and details are invented.

They deliberately cover four different **shapes of reply**, because picking the wrong
shape is a worse failure than picking the wrong part.

| | Scenario | Shape |
|---|---|---|
| A | Johan, Gothenburg — smart-home sensor | **Full playbook.** The model for a normal answer. |
| B | Kumar, Bangalore — automotive OTA | **Playbook dropped.** Narrow question from an expert. |
| C | Ali, İzmir — no project yet | **Cold start.** One question, then a menu. |
| D | Ruth, Devon — sensors across a meadow | **Half the brief refused.** Deployed, multi-node, no code. |

Blockquoted text is the reply itself, and its **length is part of the example** — a full
plan fits in one screen. Everything outside the quote is commentary for this file and
never appears in an answer.

---

## Scenario A — the model answer

**The brief.** Johan is a senior web developer in Gothenburg. Ten years of JavaScript and
Python, comfortable with Docker, MQTT and YAML. He has never soldered anything, never read
a datasheet, and owns no tools. He wants CO₂, temperature and humidity from his home
office showing up in the Home Assistant instance he already runs. Mains power is available.
Budget "a few hundred kronor", timeline a couple of weekends.

**The experience read.** Professional on software, true beginner on hardware — so skip
programming basics entirely, and go slow on wiring, power and datasheets. Classing him as
an "absolute beginner" would have him blinking an LED for an evening; classing him as
experienced would leave him holding an unlabelled breakout with no idea which pin is which.

**The reply. Its length is the point — a whole plan, one screen.**

> Mains power and a Home Assistant instance already running makes this a short project.
>
> | Part | Primary | Alternative | Why |
> |---|---|---|---|
> | Board | ESP32-C3 DevKit | Pico W | USB-native, Wi-Fi built in, nothing to solder |
> | Sensor | SCD40/41 (CO₂ + T + RH) | SCD30, or BME280 without CO₂ | True NDIR CO₂, I²C, one part not three |
> | Firmware | **ESPHome** | Arduino core | YAML, native HA discovery, OTA built in |
> | Wiring | Qwiic/STEMMA cable | Dupont jumpers | Keyed connector removes the one step you can't yet check |
>
> ESPHome is the real pick here: it routes the project through YAML and Home Assistant,
> which you already know, instead of a C toolchain learned alongside the hardware.
>
> | | |
> |---|---|
> | Parts total | ≈ 400–800 SEK |
> | Effort | 4–8 h over two sessions |
> | Buying | Electrokit or Elfa ship in days; LCSC is cheaper but adds weeks |
>
> 1. Flash ESPHome to the bare DevKit. **Exit:** it appears in Home Assistant.
> 2. Add the sensor and eight lines of YAML. **Exit:** CO₂ rises when you breathe on it.
> 3. Leave it running a week. **Exit:** no dropouts, no drift you can't explain.
>
> **Risks.** CO₂ sensors need warm-up and periodic fresh-air calibration — the first hour
> of readings means nothing. Mains power means no power budget; battery would change the
> whole design. Enclosure, PCB and battery on request.

**Lesson:** the two experience axes changed the *recommendation*, not just the tone —
software strength is leverage, so route the project through what the user already knows.
Note what is absent: no explanation of how NDIR works, no separate next-actions list
repeating the MVP steps, no closing offer to continue.

---

## Scenario B — when the playbook is the wrong answer

**The brief.** Kumar is a senior embedded engineer in Bangalore, fifteen years in
automotive, has shipped ECUs. He asks one thing: *how can I improve the OTA download for a
small display mounted on a car's rear glass, which tells the driver behind that the driver
is deaf, so they do not honk?*

**What the skill did — and did not do.** He asked a narrow question and knows his domain
better than this skill does. So: no project-understanding line, no recommended-stack table,
no cost snapshot, no MVP plan, no dev-board suggestion. All of it would have been
condescending and none of it was asked for.

> Two flags before any engineering time. **Road legality:** a display on rear glass is
> regulated — visibility obstruction, driver distraction, lighting and signage rules differ
> by market, and a fitted device may need type approval. Electrically trivial, still
> possibly not road-legal. **Privacy:** broadcasting a driver's disability to strangers is
> a decision about a person, not a design parameter — who can switch it off, and is it on
> by default? Your call and your users', not mine.
>
> On the download itself, what transfers from general practice:
>
> | Lever | Effect |
> |---|---|
> | Delta / differential images | Usually the largest single win on download size |
> | Resumable, chunked transfer | Turns a flaky link from "never completes" into "completes eventually" |
> | Compression before signing | Cheap, if verification happens on the decompressed image |
> | Staged rollout | Doesn't speed a download; caps the blast radius of a bad one |
> | A/B slots + post-boot health confirm | Non-negotiable for a sealed, moving device |
>
> Past that it is your ground, not mine: UNECE R156 update management, diagnostic-side
> reprogramming (UDS / ISO 14229), OEM release procedure, audited rollback. Your compliance
> and platform teams outrank anything I can offer, and extrapolating hobby OTA practice
> into that space would be worse than saying nothing.
>
> The display side I can help with — sunlight readability on glass, a Bangalore summer
> parking temperature, defroster-element interference — if you want it.

**Lesson:** the most useful thing the skill did was refuse its own default shape, flag
two non-technical blockers, and say where its competence ends. Answer the question asked.

---

## Scenario C — no project yet

**The brief.** Ali, in İzmir, opens with roughly: *"I use computers a lot and I've been
using Claude. I keep hearing about IoT — is that something I could do?"*

**What the skill did.** It did **not** redirect him as out of scope. He has no project,
which is different from wanting something this skill cannot help with. It also did not
fire all ten clarifying questions at him — that reads as a form to fill in, and loses
people at exactly the moment they are most tentative. One question, then wait:

> Two quick things and I can point you somewhere concrete: have you built anything with
> electronics before — even a kit — and are you comfortable writing a bit of code?

**He answers:** never built anything, and he can install and configure software but does
not really program. That places him at *new to hardware, new to code* — the gentlest path:
a USB dev board with Arduino IDE or MicroPython, nothing to solder.

> | Project | What you learn | Rough cost |
> |---|---|---|
> | Desk temperature + humidity display | Wiring a sensor, reading a value, showing it | ~₺400–800 |
> | Plant moisture alert on your phone | The same, plus getting data off the device | ~₺600–1200 |
> | Button-triggered smart plug | Output instead of input; mains safety boundaries | ~₺500–1000 |
>
> Robotistan, Direnç and similar ship within days; AliExpress or LCSC is cheaper but slower
> and may attract customs — for a first project the local shop is worth the difference.
> Pick one and I'll walk you through it.

**Lesson:** curiosity is a valid starting point. One question and a concrete menu beats
ten questions and a decision tree for someone who does not yet know what they want.

---

## Scenario D — when half the brief cannot be built

**The brief.** Ruth farms sheep near Holsworthy in Devon. She opens with: *"I want to
measure soil moisture and nitrogen in different parts of my meadow to make sure my sheep
are well fed."* Asked, she says six spots, the furthest about 400 m from the house, she
has never built anything like this, and she does not write code.

**The experience read.** Expert in her own field, beginner in this one. So: no farming
advice, no explanation of what soil moisture is, and no toolchain — she said she does not
write code, which is a requirement, not a limitation to work around.

**What the skill did first.** It refused half the request in one line. Nitrogen is not
honestly measurable by anything at this price — the cheap "7-in-1 NPK" probes read
conductivity and infer the rest. Naming that up front costs a sentence; leaving it would
have shipped her a number she trusted and shouldn't. Then one question, not nine:

> Moisture is easy. Nitrogen is not. No cheap in-soil sensor measures it honestly, and the
> £25 "7-in-1 NPK" probes really read conductivity and guess. Sample the soil for nitrogen,
> build the sensor network for moisture.
>
> How many spots do you want readings from, and how far is the furthest one from the house?

**The reply, once she answers.** Note what the 400 m did: it settled the radio before any
board was considered, and the "no code" settled the firmware the same way.

> 400 metres across wet fields means radio, not Wi-Fi. And nothing to code for the first node.
>
> | Part | Start with | Instead | Why |
> |---|---|---|---|
> | Board | Heltec WiFi LoRa 32 V3, £22 | LilyGO T3-S3 | radio and USB-C already on it |
> | Sensor | Capacitive probe v2.0, £4 | Teros 12, £180 | resistive probes corrode in weeks |
> | Power | 2× AA lithium | 1 W solar + LiPo | it sleeps between readings |
> | Software | Meshtastic, flashed from a web page | ESPHome | no code at all to start |
>
> First node £55 to £75 and a weekend. All six £300 to £380 over three to five weekends.
> The Pi Hut and Pimoroni both ship to Devon in a couple of days.
>
> MVP, then stop:
>
> 1. Flash one board from the browser and check it wakes up.
> 2. Read moisture in a mug of soil. Write down the dry and the wet number.
> 3. Put node 1 in the nearest field, keep node 2 indoors as the receiver.
> 4. Leave it a fortnight. It passes if the readings survive rain and you can see them from
>    the kitchen.
>
> Risks: damp gets in before the sheep do, range drops in wet hedgerows, and calibration
> drifts between soil types across the meadow.

**Two follow-ups, each answered at its own size.** She asks what happens when the sheep
chew it — a physical question, so a physical answer, no table:

> They will try. Box on a fence post 1.2 m up, sensor cable running down the post inside
> conduit, nothing loose at nose height. IP65 box with proper cable glands, not tape. Sheep
> rub harder than they chew, so the mount matters more than the lid.

Then what it costs to run — a different question from what it costs to build, so it gets
its own small table rather than a revised BOM:

> Batteries, and nothing else, as long as the receiver is your own.
>
> | Item | Per year |
> |---|---|
> | 2× AA lithium per node | £4 to £6 |
> | Six nodes | £25 to £35 |
> | Network fees | none, you own the receiver |
>
> A 1 W solar panel swaps that for a one off £12 a node.

**Lesson:** the most valuable move was the first sentence, and it deleted work rather than
adding it. After that, three constraints did the choosing — 400 m picked the radio, "no
code" picked ready-made firmware, and a meadow picked the enclosure — and none of them were
about the microcontroller. A deployed build owes the user a running cost as well as a
build cost, and the follow-ups stayed short because the questions were.
