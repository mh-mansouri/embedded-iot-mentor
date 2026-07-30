# Worked examples

Three scenarios showing the skill applied end to end. People and details are invented.

They deliberately cover three different **shapes of reply**, because picking the wrong
shape is a worse failure than picking the wrong part.

| | Scenario | Shape |
|---|---|---|
| A | Johan, Gothenburg — smart-home sensor | **Full playbook.** The model for a normal answer. |
| B | Kumar, Bangalore — automotive OTA | **Playbook dropped.** Narrow question from an expert. |
| C | Ali, İzmir — no project yet | **Cold start.** One question, then a menu. |

---

## Scenario A — the model answer

**The brief.** Johan is a senior web developer in Gothenburg. Ten years of JavaScript and
Python, comfortable with Docker, MQTT and YAML. He has never soldered anything, never read
a datasheet, and owns no tools. He wants CO₂, temperature and humidity from his home
office showing up in the Home Assistant instance he already runs. Mains power is available.
Budget "a few hundred kronor", timeline a couple of weekends.

**The experience read — and why it changes the answer.**

| Axis | Level | Consequence |
|---|---|---|
| Software | Professional | Skip programming basics entirely. YAML and MQTT need no explanation. |
| Hardware | True beginner | Go slow on wiring, power, I²C pull-ups, and what a datasheet is for. |

Classing him as an "absolute beginner" on one axis would have him blinking an LED for an
evening. Classing him as experienced would leave him holding an unlabelled sensor breakout
with no idea which pin is which. He needs neither.

**Recommended stack.**

| Part | Primary | Alternatives | Why the primary |
|---|---|---|---|
| Board | ESP32-C3 or S3 DevKit | Pico W, off-the-shelf Zigbee sensor | USB-native, Wi-Fi built in, nothing to solder |
| Sensor | SCD40/SCD41 (CO₂ + T + RH) breakout | SCD30, or BME280 if CO₂ is dropped | True NDIR CO₂, I²C, one part instead of three |
| Firmware | **ESPHome** | Arduino core, MicroPython | YAML config, native Home Assistant discovery, OTA built in |
| Wiring | Breadboard + Qwiic/STEMMA cable | Dupont jumpers | A keyed connector removes the one step he cannot yet check |

The firmware choice is the point. ESPHome turns this into a YAML file and a Home Assistant
integration — the half of the project he is already expert in — and removes the C toolchain
he would otherwise have to learn *at the same time* as the hardware.

**Time & cost.**

| Item | Range |
|---|---|
| ESP32 DevKit | 60–150 SEK |
| SCD40/41 breakout | 250–450 SEK |
| Breadboard, cables, USB-C lead | 100–200 SEK |
| **Parts total** | **≈ 400–800 SEK** |
| Effort to working sensor | 4–8 h across two sessions |

Sweden: Electrokit or Elfa Distrelec ship domestically in days; LCSC or AliExpress cost
less but add weeks and possible customs handling. For a first build, pay the premium and
get the parts this week — waiting three weeks kills more projects than cost does.

**MVP plan.**

1. Flash ESPHome to the bare DevKit over USB. **Exit:** it appears in Home Assistant.
2. Connect the sensor with the keyed cable, add eight lines of YAML. **Exit:** a CO₂
   number that rises when he breathes on it.
3. Leave it running a week. **Exit:** no dropouts, no drift he cannot explain.

Later stages — enclosure, PCB, battery — on request. Not needed here.

**Immediate next actions.** Order the three parts today; install ESPHome; skim the SCD40
datasheet's *recommended operating conditions* only; decide where in the room it sits
(not in direct sun, not next to his face).

**Risks.** CO₂ sensors need a warm-up and periodic auto-calibration in fresh air — readings
in the first hour mean nothing. Wi-Fi on mains is fine, so no power budget is needed here;
that changes entirely if he later wants it battery-powered.

**Lesson:** the two experience axes changed the *recommendation*, not just the tone.
Software strength is leverage — route the project through what the user already knows.

---

## Scenario B — when the playbook is the wrong answer

**The brief.** Kumar is a senior embedded engineer in Bangalore, fifteen years in
automotive, has shipped ECUs. He asks one thing: *how can I improve the OTA download for a
small display mounted on a car's rear glass, which tells the driver behind that the driver
is deaf, so they do not honk?*

**What the skill did — and did not do.**

He asked a narrow question and knows his domain better than this skill does. So: no
project-understanding section, no recommended-stack table, no cost snapshot, no MVP plan,
no dev-board suggestion. All of it would have been condescending and none of it was asked
for.

**Two flags first, before any engineering time.**

- **Road legality.** A display on the rear glass is regulated: rear-visibility
  obstruction, driver distraction, and lighting or signage rules differ by market, and a
  fitted vehicle device may need type approval. The build can be electrically trivial and
  still not be road-legal. Confirm this before optimising anything.
- **Privacy.** Broadcasting a driver's disability to strangers is a decision about a
  person, not a design parameter. Who can switch it off, and is it on by default? That is
  Kumar's call and his users' — the skill names it and hands it back.

**Then the actual question.** What transfers from general practice, at his level:

| Lever | Effect |
|---|---|
| Delta / differential images | Usually the largest single win on download size |
| Resumable, chunked transfer | Turns a flaky link from "never completes" into "completes eventually" |
| Compression before signing | Cheap, as long as verification happens on the decompressed image |
| Staged rollout | Does not speed one download; caps the blast radius of a bad one |
| A/B slots + post-boot health confirm | Non-negotiable for a sealed, moving device |

**Where this skill stops, stated plainly.** Automotive update management is a regulated
process in its own right — UNECE R156 software-update management where it applies,
diagnostic-side reprogramming (UDS / ISO 14229), OEM and supplier release procedure,
audited rollback and traceability. Kumar's own compliance and platform teams outrank
anything here. Extrapolating hobby OTA practice into that space would be worse than
saying nothing.

**What it did offer.** One line, as an offer rather than an unrequested section: the
display side *is* in scope — sunlight readability on glass, temperature range in a car
parked in Bangalore summer, and defroster-element interference — if he wants it.

**Lesson:** the most useful thing the skill did was refuse its own default shape, flag
two non-technical blockers, and say where its competence ends. Answer the question asked.

---

## Scenario C — no project yet

**The brief.** Ali, in İzmir, opens with roughly: *"I use computers a lot and I've been
using Claude. I keep hearing about IoT — is that something I could do?"*

**What the skill did.** It did **not** redirect him as out of scope. He has no project,
which is different from wanting something this skill cannot help with. It also did not
fire all nine clarifying questions at him — that reads as a form to fill in, and loses
people at exactly the moment they are most tentative.

**One question, then wait:**

> Two quick things and I can point you somewhere concrete: have you built anything with
> electronics before — even a kit — and are you comfortable writing a bit of code?

**He answers:** never built anything, and he can install and configure software but does
not really program.

**Which places him** at *new to hardware, new to code* — the gentlest path: a USB dev board
with Arduino IDE or MicroPython, one guided step at a time, nothing to solder.

**Three starter projects at that level.**

| Project | What he learns | Rough cost |
|---|---|---|
| Desk temperature + humidity display | Wiring one sensor, reading a value, showing it | ~₺400–800 |
| Plant moisture alert on his phone | The same, plus getting data off the device | ~₺600–1200 |
| Button-triggered smart plug or light | Output instead of input; mains safety boundaries | ~₺500–1000 |

**Buying in Turkey.** Local hobby retailers (Robotistan, Direnç, and similar) ship within
days; ordering from AliExpress or LCSC is cheaper but slower and may attract customs
handling on import — check the current threshold before ordering. For a first project the
local shop is worth the difference: a three-week wait for a ₺50 saving is how first
projects die.

**Closing.** One invitation, not a lecture: pick one, and the skill walks him through it
step by step.

**Lesson:** curiosity is a valid starting point. One question and a concrete menu beats
nine questions and a decision tree for someone who does not yet know what they want.
