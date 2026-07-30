# OTA / Firmware Update Notes (glanceable)

## First ask whether it is needed yet

OTA is not an MVP feature. One device on a bench reflashes over USB in ten seconds.
Build OTA when **one** of these is true, not before:

- the device will be sealed, wall-mounted, or otherwise hard to reach;
- there will be more than a handful of them;
- someone other than the developer has to apply the update.

Adding it early costs flash, complexity, and a class of bugs that only appear in the field.

## The one rule: never brick the device

A failed update must leave a device that still boots and can try again. Power can drop
mid-write, Wi-Fi can vanish, the image can be truncated.

- **Two app slots (A/B)** plus a bootloader that falls back to the last known-good image.
- **Verify before you switch.** Checksum or signature over the whole image, then flip.
- **Confirm after you boot.** The new image marks itself healthy; if it never does, the
  bootloader rolls back on the next reset.
- Budget the flash: A/B means the app must fit in *half* the usable space.

## Platform options

| Platform | Usual route | Notes |
|---|---|---|
| ESP32 / ESP8266 | `esp_https_ota` (ESP-IDF), `ArduinoOTA` (Arduino core), built-in in ESPHome | Needs two OTA app partitions plus otadata; check the partition table before promising it fits |
| nRF52 / nRF53 | MCUboot via nRF Connect SDK, DFU over BLE | Mature; phone-app or gateway driven |
| Zephyr (any SoC) | MCUboot + SMP | The most portable answer if the project is already Zephyr |
| STM32 | Custom bootloader, or MCUboot | Rarely turnkey; budget real time for it |
| Raspberry Pi Pico / Pico W | No first-party OTA | Plan on USB/UF2 unless a community bootloader is added deliberately |
| Linux-class (Pi, SBC) | Mender, RAUC, SWUpdate, balena | A/B rootfs is the norm; heavier but solved |

## Delivery and triggering

- **Pull** — device polls an HTTPS URL for a manifest. Simplest, firewall-friendly, the
  usual choice.
- **Push** — broker tells the device to update (MQTT command, BLE from a phone). Faster,
  needs a live connection.
- **Staged rollout.** Ship to a few devices, wait, then the rest. This is the cheapest
  insurance available and costs nothing but patience.
- Have devices **report their running version**. Without it a fleet is unknowable.

## Security minimums

- **Sign the image**; verify the signature on the device before switching slots.
- **HTTPS with certificate validation** — not disabled "just to get it working".
- **No single shared secret across the fleet**; one leak should not compromise everything.
- **Block downgrades** to old, vulnerable versions (ESP32 offers anti-rollback via efuse).

## Traps

- Flash too small for two slots — discovered *after* the enclosure is designed.
- Watchdog resets the device mid-write; feed it or disable it deliberately during flash.
- No resume on a dropped download, so a marginal link never completes an update.
- **Battery devices:** an update is a long, high-current, radio-on operation. A weekly
  OTA check can outweigh the entire sensing budget — model it with
  `scripts/sleep_budget.py` before committing to a schedule.

## Where this guidance stops

The above is for hobby, prosumer, and light commercial IoT. It is **not** sufficient for
vehicles, medical devices, or anything type-approved. There, update management is itself
a regulated process: UNECE R156 software-update management systems where it applies,
supplier and OEM release procedures, diagnostic-side reprogramming (UDS / ISO 14229),
and audited rollback and traceability requirements that vary by market.

Say so plainly rather than extrapolating from the IoT practice above, help with the parts
that genuinely transfer (image signing, A/B, staged rollout, version reporting), and
recommend the user's own compliance and platform teams for the rest.
