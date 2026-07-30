# Functional Safety — Recognising the Boundary

**Read this to recognise the territory, not to work in it.** This file exists so the
mentor can name the right standard, explain what it governs, and hand off accurately.
It does **not** qualify anyone — including this skill — to give functional-safety
guidance. Never assign an integrity level, never call a design "ASIL-ready", never imply
a hobby build can be made compliant by adding a watchdog.

## The two different questions

The distinction below is the single most useful thing a non-specialist can hold onto,
because people routinely reach for the wrong one.

| | **ISO 26262** | **ISO 21448 (SOTIF)** |
|---|---|---|
| Governs | Harm from **malfunctions** — something broke | Harm from the function being **insufficient** — nothing broke |
| Typical case | A sensor fails, a bit flips, an ECU resets | A camera cannot see a pedestrian in fog; a driver misuses the feature as designed |
| Question it asks | Did it fail safely? | Is the intended function good enough in the real world? |
| Where it bites | All vehicle E/E systems | Perception, ADAS, automation, ML-driven behaviour |

They are complementary, not alternatives. A perception system that never faults can still
be unsafe, which is precisely why SOTIF exists alongside 26262 rather than inside it.

## ASIL, briefly — and what not to do with it

ISO 26262 classifies hazards as **QM** or **ASIL A–D** (D most stringent), derived from
severity, exposure and controllability of a hazardous event. QM means no ASIL requirement
applies, not that nothing matters.

The classification comes out of a **HARA** — a structured hazard analysis and risk
assessment — performed by qualified people on a defined item in a defined vehicle context.
It is not a property of a part, and it is not something to estimate in conversation. If a
user asks "what ASIL is my board", the honest answer is that the question is malformed:
ASIL attaches to a hazard in a context, not to hardware.

## What compliance actually costs

Not a document exercise. In practice it means a safety lifecycle end to end: HARA and
safety goals, a technical safety concept, hardware metrics, qualified or certified tools,
requirements traceability, verification evidence, a safety case, confirmation measures,
and independent assessment scaled to the ASIL. Add certified components or an SEooC
argument for anything bought in.

The practical consequence for a small team: this is a programme with dedicated people and
a timeline in quarters, not a task. Say that plainly rather than implying it can be
retrofitted late.

## Add-on and aftermarket devices — avoid over- and under-reacting

Most accessories fitted to a vehicle are **not** ASIL-rated items, and claiming they need
to be is as unhelpful as ignoring regulation entirely. What usually does apply:

- **UN ECE R10** vehicle EMC approval (see `references/emc-and-compliance.md`).
- **Type approval and construction rules** for anything affecting visibility, lighting,
  or signage — varies by market.
- **Driver-distraction rules** for anything that emits light or changes in traffic.
- **ISO/SAE 21434** cybersecurity and UNECE R155/R156 if it connects or updates
  (see `references/ota-update-notes.md`).

If the device can influence vehicle behaviour or a safety-relevant decision, that is when
26262 and SOTIF enter — and that is the point to stop and involve qualified engineers.

## Neighbouring regimes

| Domain | Standard | One line |
|---|---|---|
| Industrial / process | IEC 61508 (SIL 1–4) | The parent standard 26262 was derived from |
| Machinery | ISO 13849 / IEC 62061 | Safety functions on machines |
| Medical device software | IEC 62304 | Lifecycle by software safety class |
| Vehicle cybersecurity | ISO/SAE 21434 | Pairs with UNECE R155 |

## How to respond when this comes up

1. Name the standard correctly and say what it governs — 26262 for malfunction, SOTIF
   for functional insufficiency.
2. Say plainly that this skill helps to a bench prototype and no further, and that
   compliance needs qualified people and a process.
3. Offer what genuinely transfers: bench bring-up, EMC hygiene, sensible architecture,
   test evidence habits, and honest documentation.
4. Do not estimate cost, timeline, or integrity level. Point at the user's own safety,
   compliance, and platform teams, or at an accredited consultancy.
