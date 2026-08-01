# Example prompts

Try these once the GPT is configured, or against the connector in a normal ChatGPT chat.
Each one is chosen to exercise a behaviour the port is supposed to keep.

| Prompt | What should happen |
|---|---|
| *I want a battery-powered air-quality sensor with Wi-Fi and a phone dashboard. I can solder and have used Arduino, but I'm new to embedded firmware.* | Two-axis experience is already answered, so no intake questions. One stack table, a note that "air quality" is not one number, and an MVP plan. |
| *I am a farmer and want to measure soil moisture and nitrogen across my meadow.* | Refuses the nitrogen half in one line, asks about sensing points and distance before choosing a radio. |
| *Which LDO for a 3.3 V ESP32 node that sleeps most of the time?* | ~80 words, one table at most. No project plan, no cost table — it's a narrow question. |
| *How long will a 2000 mAh cell last if I wake for 250 ms every 10 minutes at 80 mA and sleep at 15 µA?* | Runs `sleep_budget.py` (GPT) or calls `battery_runtime` (connector) instead of estimating in prose. |
| *Can I hand-solder a QFN-32 on my first board?* | Runs `footprint_hint.py` or calls `hand_solder_hint`, and says what to use instead. |
| *I want to put a brake-light repeater on my trailer.* | Raises the road-legality question before the electronics. |
| *Build me a React dashboard for my todo app.* | One line saying this is not the right fit. |
