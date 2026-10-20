# FNAF Desktop Chaos 2.0

Uitbreiding van de bestaande Windows 11-app: zes desktopmaatjes lopen rond, halen afbeeldingen van de schermrand, slepen ze mee, leggen ze neer en kunnen elkaars afbeeldingen stelen. Alle afbeeldingen zijn eigen tijdelijke vensters: er worden geen echte bestanden, muiscursor, bureaubladpictogrammen, taakbalkinstellingen of monitoren verplaatst/aangepast.

Gebruik uitsluitend op een computer waarvan de eigenaar toestemming heeft gegeven. Dit is een onofficieel fanproject. De meegeleverde illustraties zijn gegenereerde fanillustraties, de geluiden zijn eigen synthetische placeholders. Originele game-opnamen en de afzonderlijke Golden Freddy-referentie van de gebruiker zijn niet meegeleverd.

## De Windows-versie downloaden

1. Open [Actions → Build Windows EXE](https://github.com/lisannekalk2013-maker/FNAF/actions/workflows/windows-exe.yml).
2. Open de nieuwste uitvoering voor branch `main`. Nieuwe pushes naar `main` starten automatisch een build. Handmatig starten kan met **Run workflow → main → Run workflow**.
3. Wacht tot de uitvoering groen is. De build voert tests uit, bouwt de EXE en start deze kort in stille testmodus.
4. Klik bij **Artifacts** op **FNAFDesktop-Windows**. GitHub vereist hiervoor dat je bent ingelogd.
5. Pak de ZIP volledig uit en open **FNAFDesktop.exe**. Bewaar `_internal` en de andere bestanden erbij. Je hebt voor deze EXE geen Python nodig.

Het tweede artifact **FNAFDesktop-Chaos-2.0-Windows-ZIP** bevat de apart gemaakte complete Windows-ZIP. Na het downloaden hiervan zit de Windows-ZIP in de artifact-ZIP.

De eerste Windows-build van Chaos 2.0 is geslaagd: [open de geteste build en downloads](https://github.com/lisannekalk2013-maker/FNAF/actions/runs/39481454031).

De [ZIP onder downloads/](downloads/FNAF-project.zip) bevat **broncode**, geen vooraf gebouwde Windows-EXE. Als een workflow rood is, open de mislukte stap voor de foutmelding; de ZIP wordt alleen als artifact aangeboden na een geslaagde build en EXE-smoketest. Een geslaagde offscreen-buildtest bevestigt nog niet alle fysieke Windows-desktopfuncties.

## Afsluiten en pauzeren

- **Escape indrukken:** jumpscare of speciaal effect onmiddellijk onderbreken.
- **Escape vijf seconden onafgebroken vasthouden:** hele app afsluiten, ook tijdens pauze of een jumpscare. Loslaten zet de teller terug.
- **Ctrl+Shift+Q:** tweede globale Windows-noodstop.
- **Systeemvak → Afsluiten:** sluit alles, inclusief geluid en tijdelijke afbeeldingsvensters.

Op Windows wordt uitsluitend de Escape-toets passief opgevraagd; er worden geen andere toetsen vastgelegd of geblokkeerd. Op Linux werkt Escape alleen met toetsenbordfocus bij de app. Kan Windows Ctrl+Shift+Q niet registreren, dan blijven jumpscares uitgeschakeld. Bij afsluiten stoppen timers en audio en worden alle overlays gesloten. Er zijn geen losse helperprocessen voor afbeeldingen.

In het systeemvak kun je pauzeren/hervatten, Custom Night openen, direct een afbeelding tonen, alle afbeeldingen opruimen en personages tijdelijk verbergen. Pauzeren bevriest beweging, taken en afbeeldingstimers en verbergt de afbeeldingen. Speciale effecten en geluid stoppen. Verbergen laat afbeeldingen liggen en laat personages hun afbeeldingen loslaten.

## Afbeeldingen meeslepen en stelen

Een personage loopt naar de schermrand, mag gedeeltelijk buiten beeld komen en keert terug met een afbeelding aan zijn hand. Het beeld volgt met een lichte vertraging en wiegt tijdens het lopen. Aan de bestemming laat het personage het beeld los; na de ingestelde levensduur verdwijnt het. Het kruisje sluit een afbeelding meteen, ook als iemand hem draagt.

- **Foxy:** hoogste kans op stelen, sprint met buit, kan onderweg iets laten vallen en zelden direct uit iemands handen stelen.
- **Freddy:** rustig transport; heeft voorkeur voor eigen afbeeldingen en kan Foxy achtervolgen om die terug te halen.
- **Bonnie:** onderzoekt eerst en besluit daarna of hij iets meeneemt.
- **Chica:** heeft voorkeur voor bestandsnamen met `chica`, `cupcake`, `food` of `pizza`; laat ook cupcakeberichten achter.
- **Golden Freddy:** loopt niet permanent rond, verschijnt zelden bij de cursor en laat afbeeldingen glitchend verdwijnen en op een andere plek terugkomen.
- **Springtrap:** blijft als extra zesde personage beschikbaar en beweegt langzaam.

Slechts één personage kan een afbeelding vasthouden. Tijdens een kort visueel trekspel blijft er één logische eigenaar; daarna wordt het eigendom in één stap overgedragen. Personages kunnen elkaars achtergelaten afbeeldingen opzoeken of hun eigen beeld opnieuw meenemen. Afsluiten, opruimen, een beeld handmatig sluiten en monitorwisselingen ruimen ook de bijbehorende taken op. De beelden nemen de toetsenbordfocus niet over; alleen hun eigen venster vangt muisklikken op.

## Custom Night en config.json

Bij starten opent altijd het instellingenvenster. Per personage kun je selectie en activiteit **0–20** instellen. Activiteit 0 schakelt hem uit; hogere waarden verhogen de frequentie van acties binnen de limieten. Stel verder in:

- Aantal personages, bewegings- en animatiesnelheid, FPS (15–60).
- Kans op losse afbeeldingen, frequentie meeslepen, kans op stelen en achtervolgen.
- Maximum afbeeldingen (1–12), levensduur na neerleggen (10–300 seconden).
- Speciale gebeurtenissen, verminderde lichteffecten en Golden Freddy-ontmoetingsinterval.
- Jumpscares, fullscreen of kleiner venster, cooldown (2–60 seconden).
- Jumpscarevolume, apart omgevingsvolume, volledig stil, rustige of chaosmodus.

Klik **Toepassen en opslaan**. Je persoonlijke configuratie staat in `%LOCALAPPDATA%\FNAFDesktop\config.json`. Bestaande persoonlijke `settings.json`-waarden worden overgenomen zolang er nog geen `config.json` is. Het oude bestand blijft bestaan. `config.json` in deze projectmap is alleen het standaardvoorbeeld; het wijzigen ervan overschrijft bestaande persoonlijke instellingen niet. Ongeldige configuratiewaarden worden begrensd; bij onleesbare JSON worden standaardwaarden gebruikt.

Opstarten met Windows en systeemvolumebegrenzing blijven standaard uit. Opstarten inschakelen vraagt apart toestemming en schrijft uitsluitend de eigen waarde `FNAFDesktop` onder `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Uitzetten verwijdert alleen die waarde. Zet het uit voordat je de app verplaatst of verwijdert.

## Speciale gebeurtenissen en Golden Freddy

De eventmanager laat hoogstens één speciaal effect tegelijk actief zijn: cameraruis, IT'S ME, Freddy's lach, Foxy-sprint, een korte gesimuleerde blackout, taakbalk-overlay, gezamenlijk staren, afbeeldingsdiefstal of Golden Freddy-hallucinatie. De echte monitor en taakbalk blijven ongewijzigd. Verminderde lichteffecten staan standaard aan; er zijn geen snelle stroboscoopflitsen.

Golden Freddy's aparte gezicht staat in `assets/images/golden_freddy/golden_freddy_flicker.png`. Een zeldzame ontmoeting pauzeert de figuren kort, toont het gezicht met IT'S ME en een glitchgeluid en hervat daarna alles. Standaard wordt de volgende ontmoeting gekozen tussen ongeveer 15 en 29 minuten (gemiddeld 22 minuten actieve looptijd). Pauze en jumpscares tellen hiervoor niet mee. Kortere Golden-flickers zijn afzonderlijke willekeurige effecten. Zet zijn activiteit op 0 of deselecteer hem om Golden-events uit te schakelen.

## Originele/eigen media toevoegen

De bestaande meegeleverde assets blijven als fallback werken. Voeg eigen bestanden toe waarvoor je gebruiksrechten hebt. Bij een gebouwde EXE staat `assets` onder `_internal/assets`.

```text
assets/images/random/                 PNG, JPG/JPEG, WEBP voor losse/draagbare beelden
assets/images/memes/                  extra memes in dezelfde formaten
assets/images/characters/             optionele freddy.png, bonnie.png, enz.
assets/images/jumpscares/freddy/       jumpscare.mp4 of jumpscare.webm
                                     OF frame_000.png, frame_001.png, enz.
assets/images/jumpscares/bonnie/       dezelfde namen, eigen media
assets/images/jumpscares/chica/
assets/images/jumpscares/foxy/
assets/images/jumpscares/golden_freddy/
assets/images/jumpscares/springtrap/
assets/images/golden_freddy/           golden_freddy_flicker.png (vervangbaar)
assets/audio/                         eigen PCM-WAVs
```

Afbeeldingen worden elke tien seconden opnieuw ontdekt; klik Toepassen of herstart voor gewijzigde personages. Frames worden op 30 fps afgespeeld, maximaal 120 frames van maximaal 512 pixels bij het inladen. Video heeft voorrang op frames; zonder eigen animatie gebruikt de app het bestaande gezicht met een per personage verschillend bewegingsritme. Clips worden na maximaal circa tien seconden afgebroken.

Audio in `assets/audio/` heeft voorrang op de synthetische standaardbestanden:

- `freddy_scare.wav`, `bonnie_scare.wav`, `chica_scare.wav`, `foxy_scare.wav`, `golden_freddy_scare.wav`, `springtrap_scare.wav`.
- `freddy.wav` (lach), `foxy_sprint.wav`, `camera_static.wav`, `golden_glitch.wav`, `theft.wav`, `ambient.wav`, `chica.wav`.

Een eigen video gebruikt zijn ingebouwde audio als er geen expliciete bijbehorende WAV in `assets/audio/` staat. Bij een WAV-override wordt videogeluid onderdrukt. Bij meerdere monitoren wordt geluid slechts één keer gestart. Tijdens een jumpscare stoppen andere geluiden. Volume testen kiest het personage afzonderlijk. Stille modus geldt ook voor video. Ontbrekende of onleesbare beelden worden overgeslagen of vallen terug op een placeholder; beschadigde video valt terug op de stilstaande illustratie.

Appvolume is standaard 15% voor jumpscares en 8% voor andere geluiden, maximaal 50%. Dit bepaalt niet de fysieke geluidsdruk: test eerst zacht. De optionele systeemvolumebegrenzing geldt voor WAV-afspelen en verlaagt alleen; zij herstelt het oorspronkelijke endpointvolume na afspelen, fouten, pauze en normaal afsluiten. Ingebouwde videoaudio wordt alleen op appniveau begrensd. Geforceerd beëindigen, stroomuitval of het verdwijnen van een audioapparaat kan systeemvolumeherstel verhinderen; laat de systeemoptie uit voor uitsluitend appvolume.

## Starten en bouwen met Python 3.13

Gebruik Python 3.13 **64-bit** op Windows 11. Voor ontwikkelen:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
.venv\Scripts\python.exe -m pytest -q
```

Zonder opdrachten: dubbelklik **build_windows.bat**. Het script gebruikt een aparte `.venv-windows`, installeert dependencies, voert de tests uit en bouwt PyInstaller onedir. Resultaat:

- `dist\FNAFDesktop\FNAFDesktop.exe` met `_internal` en startinstructies.
- `dist\FNAFDesktop-Chaos-2.0-Windows.zip`: de volledige Windows-map, geverifieerd op verplichte bestanden.

Er zijn geen administratorrechten nodig. De build is niet ondertekend: schakel beveiliging niet uit. Een Windows-EXE wordt op Windows gebouwd, niet op de Linux-cloudmachine.

## Validatie en grenzen

De regressietests controleren beweging, vloeiend fetchgedrag, eigendom, stelen, Foxy/Freddy-achtervolging, Bonnie/Chica-voorkeuren, glitch-herstel, beeldlimieten en opruimen, speciale gebeurtenissen, cooldown, media-overrides, Custom Night, legacyconfig-migratie, pauze en echte procesafsluiting. Er is ook een stille GUI-smoketest: `python run.py --smoke`. Zie [VALIDATIE.md](VALIDATIE.md) voor daadwerkelijk uitgevoerde controles.

Fysieke audio, Windows globale sneltoetsen, hoge DPI op meerdere monitors en interactie met andere Windows-apps vereisen een echte Windows-desktoptest. De native Windows-build en de zelfstandige EXE-smoketest zijn op GitHub Actions geslaagd; de run is hierboven gelinkt. De Actions-API was niet bereikbaar vanuit de cloud, maar de openbare webpagina bevestigde de uitslag en beide artifacts. Controleer bij latere updates altijd de nieuwe builduitslag.
