# Embedded / IoT Mentor — en Claude Skill

[English](./README.md) · **Svenska** · [فارسی](./README.fa.md)

En skill för [Claude](https://claude.ai) som agerar erfaren mentor inom inbyggda system:
den väljer mikrokontroller, kort och verktygskedja åt ditt projekt, uppskattar vad det
kommer att kosta och hur lång tid det tar, och ger dig en byggplan som stannar vid ett
**fungerande kopplingsdäck** i stället för en produktionslinje du aldrig bad om.

De flesta råd om inbyggda system missar åt ett av två håll — en komponentlista utan plan,
eller en produktionsplan till någon som ännu inte fått en lysdiod att blinka. Den här
skillen frågar vad du faktiskt har byggt tidigare, och svarar sedan på den nivån.

## Demo

![En bonde vill mäta markfuktighet och kväve över en äng; skillen avvisar kvävedelen, ställer två frågor och levererar en LoRa-plan med sex noder utan en rad kod](./embedded-iot-mentor-demo.gif)

En fårbonde i Devon, ingen kod, sex mätpunkter, den längst bort 400 m från huset. Värd att
titta på för vad skillen *inte* gör: den inleder med att avvisa halva förfrågan — ingen
billig givare mäter kväve i jord ärligt — och låter sedan tre begränsningar göra valen.
400 meter väljer radio framför Wi-Fi, ”jag skriver inte kod” väljer färdig firmware framför
en verktygskedja, och en blöt äng väljer kapslingen. Kortet bestäms sist, inte först. Hela
transkriptet finns i
[Scenario D](./embedded-iot-mentor/examples/worked-examples.md#scenario-d--when-half-the-brief-cannot-be-built).

## Vad den gör

- **Väljer en plattform** — ESP32, Pico, STM32, nRF52 — och säger rakt ut varför just den,
  plus ett eller två alternativ och när vart och ett skulle vinna i stället.
- **Skiljer hårdvaruspåret från firmwarespåret**, så att du vet vad du ska köpa och vad du
  ska installera utan att blanda ihop de två.
- **Kontrollerar om du behöver skriva firmware över huvud taget.** Om ESPHome, Meshtastic
  eller Tasmota redan gör jobbet är det svaret — att skriva kod är en kostnad, inte en
  leverans.
- **Uppskattar tid och kostnad** som intervall, och pekar ut vad som faktiskt driver dem —
  inklusive vad saken kostar att *driva*, när det väl är sex noder som äter batterier ute
  på en åker.
- **Säger vad en givare verkligen mäter.** Billiga ”NPK”-prober mäter konduktivitet och
  gissar resten; det får du veta innan du köper sex av dem, inte efteråt.
- **Planerar fram till MVP och stannar där.** Ingenjörsprototyp, förserie och produktion
  finns som faser, men du får dem först när du ber om dem.
- **Namnger riskerna** — energibudget, komponenttillgång, ingen felsökningsväg,
  certifiering, inlärningskurvan för det som just rekommenderats.
- **Underkänner sina egna förslag** mot en fast ribba: inget underhållet bibliotek,
  komponent från en enda leverantör, en kapsel du inte kan löda, ingen seriekonsol — då
  stryks kandidaten och den väljer om.

## Varför den finns

Felen den är byggd för att fånga:

- **En nybörjare som pekas mot en STM32 med en ST-Link** för att ett forum sa att det var
  ”mer professionellt” — tre kvällar förlorade på verktygskedjan innan första lysdioden.
- **Ett batteriprojekt byggt kring ett utvecklingskort** vars regulator drar 20 mA i
  tomgång, så att den ”två månader” långa drifttiden i själva verket är fyra dagar. Kortet
  var aldrig problemet; ingen räknade på viloströmmen.
- **Ett första kretskort beställt med 0402-komponenter och en QFN**, handlött med lödkolv,
  dött vid leverans och utan testpunkter för att ta reda på varför.
- **Sex givare utplacerade på en åker i inomhuslådor**, tätade med tejp i stället för
  kabelgenomföringar, med kondens på sina egna kretskort redan andra veckan.

## Installation

**Alternativ A — en fil.** Ladda ner
[`embedded-iot-mentor.skill`](./embedded-iot-mentor.skill) och öppna den i Claude.
(Sparande av skills måste vara aktiverat för ditt konto eller din organisation.)

**Alternativ B — Claude Code.** Packa upp den i din skills-katalog:

```bash
python package_skill.py --install                                     # för din användare
python package_skill.py --install --skills-dir <repo>/.claude/skills  # för ett enskilt projekt
```

Eller installera ett paket du redan har, utan en kopia av det här repot:

```bash
python package_skill.py --install-from embedded-iot-mentor.skill
```

Eller för hand — en `.skill` är bara en zip:

```bash
mkdir -p ~/.claude/skills && unzip embedded-iot-mentor.skill -d ~/.claude/skills/
```

```powershell
# Windows: Expand-Archive accepterar bara filändelsen .zip, så byt namn på en kopia först
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item embedded-iot-mentor.skill "$env:TEMP\embedded-iot-mentor.zip"
Expand-Archive "$env:TEMP\embedded-iot-mentor.zip" -DestinationPath "$HOME\.claude\skills" -Force
```

Claude Code hittar den vid nästa session — `/skills` listar den, och Claude laddar den även
på eget initiativ när ett samtal matchar beskrivningen.

## Använd den

Beskriv bara projektet. Till exempel:

> Jag vill logga markfuktighet i ett växthus och se den i mobilen. Jag har gjort ett par
> Arduino-skisser. Budget kanske 100 €, och jag vill ha det igång inom en månad.

eller

> Vilket kort för en batteridriven givare som ska hålla ett år på ett knappcellsbatteri?
> Jag har levererat firmware förut, så förenkla inte i onödan.

eller

> Jag har en ESP32 och en BME280 liggande i en låda. Vad är värt att bygga med dem?

eller, den från demon ovan:

> Jag är bonde och vill mäta markfuktighet och kväve på olika delar av min äng för att vara
> säker på att fåren får tillräckligt med foder.

Den ställer ett par korta frågor om målet, erfarenhetsnivån, strömförsörjningen, miljön
eller tidsplanen fortfarande är oklara — och svarar sedan i tabeller i stället för uppsatser.
En hel projektplan ska få plats på en skärm; vill du ha resonemanget bakom ett val får du
fråga efter det.

## Bra att veta

- **Priser och lagersaldon blir snabbt inaktuella.** Uppskattningar är intervall, inte
  offerter. Kolla LCSC, Digi-Key eller din lokala leverantör innan du beställer.
- **Den kan inte verifiera komponenttillgången** i ditt land, och det är den vanligaste
  orsaken till att en bra plan kör fast.
- **Den stannar vid MVP med flit.** Be uttryckligen om de senare faserna.
- **Inte för säkerhetskritiskt arbete.** Den hjälper dig fram till en prototyp för medicin,
  fordon eller säkerhetssystem, och säger sedan rakt ut var hobbyråden tar slut.

## Struktur

Själva skillen ligger i `embedded-iot-mentor/`. Allt i repots rot är paketering och
projektmetadata som skillen aldrig läser.

| Sökväg | Vad det är |
|---|---|
| `embedded-iot-mentor/SKILL.md` | Instruktionerna Claude följer. De flesta ändringar hör hemma här. |
| `embedded-iot-mentor/references/` | Detaljer som läses vid en utlösare: val av MCU, uppkoppling, kostnadsuppskattning, PCB-checklista, ström och batteri, fältinstallation, OTA, EMC, säkerhetsgräns, lärresurser. |
| `embedded-iot-mentor/scripts/` | Små deterministiska hjälpprogram, som körs bara när ett konkret tal efterfrågas. |
| `embedded-iot-mentor/examples/` | Genomarbetade scenarier som visar vilken *form* ett svar ska ha när en förfrågan inte passar mallen. |
| `embedded-iot-mentor.skill` | **Genererad.** En zip av mappen ovan — redigera den inte för hand. |
| `package_skill.py` | Bygger, verifierar och installerar paketet. |
| `embedded-iot-mentor-demo.gif` | Inspelningen som visas högst upp. Ingår inte i paketet — packaren tar bara skill-mappen. |

Att hålla skillen i en egen mapp spelar roll: specifikationen kräver att en skills `name`
matchar mappnamnet, så att bygga direkt från repots rot skulle gå sönder i samma stund som
någon laddade ner repot som ZIP och fick `embedded-iot-mentor-main/`.

## Bygga

```bash
python package_skill.py          # -> ./embedded-iot-mentor.skill
python package_skill.py --check  # validera källa + paket, bygg ingenting
```

En `.skill`-fil är ett zip-arkiv som innehåller skill-mappen — formatet definieras av
[Agent Skills-specifikationen](https://agentskills.io/specification). Packaren tar med allt
under `embedded-iot-mentor/`, så en ny referensfil plockas upp automatiskt utan att
byggskriptet behöver ändras. Textfiler lagras med LF och zip-tidsstämplar är låsta, så
paketet blir byte-identiskt oavsett vem som bygger det.

`--check` är grinden, och CI kör den vid varje push och pull request. Den fallerar när:

- frontmattern bryter mot en regel i specifikationen (`name`-mönster/längd, mappmatchning, `description`-längd);
- `SKILL.md` pekar på en fil under `references/…` eller `scripts/…` som inte finns;
- den incheckade `.skill`-filen inte matchar källmappen.

Det sista spelar roll eftersom paketet är incheckat: ändra skillen, glöm att bygga om, och
nedladdningen skulle leverera en annan version än källmappen.

## Skript

```bash
python embedded-iot-mentor/scripts/cost_estimator.py 1 4.50 "ESP32 DevKit" 10 0.12 "10k resistor"
python embedded-iot-mentor/scripts/footprint_hint.py 0603
python embedded-iot-mentor/scripts/sleep_budget.py --capacity 2000 --active-ma 80 \
    --active-ms 250 --sleep-ua 15 --interval-s 600
```

`sleep_budget.py` tar indata om arbetscykeln i stället för en medelström, eftersom
medelströmmen är det tal ingen känner till i förväg. Samma firmware, samma batteri,
viloström ändrad från 15 µA till ett utvecklingskorts 8 mA-regulator: **3,8 år blir
8,3 dagar.**

## Bidra

Förbättringar är välkomna — särskilt handfast kunskap om komponenter, leverantörer och vad
som faktiskt går fel på arbetsbänken. Se [CONTRIBUTING.md](./CONTRIBUTING.md).

## Licens

Släppt under [MIT-licensen](./LICENSE) — fri att använda, dela och bygga vidare på.
