# Validatie FNAF Desktop Chaos 2.0

Uitgevoerd in de Linux-cloudomgeving met Python 3.13.5 en PySide6 6.8.3:

- 46 regressietests geslaagd. Bestaande tests zijn behouden en aangepast waar Golden Freddy nu bewust meestal onzichtbaar is en de afbeeldinglimiet instelbaar is.
- Getest: onafhankelijk bewegen, vloeiende fetchroute, meenemen/neerleggen, exclusief eigendom, directe Foxy-diefstal en Freddy-terugpakactie, Bonnie-inspectie, Chica-voedselvoorkeur, sluiten tijdens een taak, glitch-verdwijnen en terugkomen, opruimen en beperkte levensduur.
- Getest: alle tien eventtypes, geen overlappende events, Golden-frequentie/uitschakelen, pauze, verbergen en de negatieve coördinaten van een linker monitor.
- Getest: Custom Night opslaan/herladen in config.json, activiteit 0, FPS en configuratiegrenzen, overname van bestaande settings.json.
- Getest: juiste karakter-WAVs en override, eigen jumpscareframes, fallback bij beschadigde video, cooldown, direct onderbreken met Escape, vijf seconden onafgebroken vasthouden en afsluiten van een afzonderlijk echt proces.
- Twee extra verpakkingstests controleren de complete Windows-mapstructuur en het afwijzen van een onvolledige build met uitsluitend testfixtures (geen echte EXE).
- Een stille start/jumpscare/automatische-afloop-smoketest geslaagd.
- Aanvullend een één seconde MP4-testclip gemaakt met FFmpeg. Qt heeft deze daadwerkelijk gedecodeerd, afgespeeld en binnen 2,3 seconden overlay en speler gesloten. Fysieke scherm- en audio-uitvoer zijn hiermee niet gevalideerd.
- Meegeleverde beelden zijn gegenereerde fanillustraties. De genoemde eerdere Golden Freddy-referentie was niet als afzonderlijk bestand beschikbaar; er is een nieuw vervangbaar donker gezicht gemaakt. Alle geluiden zijn synthetische placeholders; originele game-media moet de gebruiker zelf toevoegen.
- Gecontroleerd: de app verplaatst geen echte bestanden/cursor/iconen, leest geen wachtwoorden, installeert geen keyboardhook, wijzigt geen monitor- of taakbalkinstellingen. Alleen de eigen Windows-opstartwaarde kan na expliciete toestemming veranderen; optioneel systeemvolume wordt verlaagd en hersteld. Geen nieuwe netwerkfunctionaliteit in de app.

Windows-build uitgevoerd op GitHub Actions op 20 oktober 2026:

- [Geslaagde native Windows-build](https://github.com/lisannekalk2013-maker/FNAF/actions/runs/39481454031) voor codecommit `7c31d3295c5404aed9320258248340b9d39b1c86`.
- Installatie, regressietests, PyInstaller-build en verpakking van de volledige Windows-ZIP zijn geslaagd op windows-latest met Python 3.13 x64.
- De gebouwde FNAFDesktop.exe is als zelfstandige EXE gestart met `--smoke`, heeft een stille Freddy-jumpscarecyclus uitgevoerd en is binnen de ingestelde timeout succesvol geëindigd.
- Beide artifacts zijn succesvol geüpload: `FNAFDesktop-Windows` (de complete applicatiemap, download als ZIP) en `FNAFDesktop-Chaos-2.0-Windows-ZIP` (de afzonderlijk gemaakte Windows-ZIP in een artifact).
- De laatste documentatie-/broncode-ZIP-update verandert de geteste applicatiecode niet. Het broncodearchief onder downloads blijft een broncode-ZIP; de echte Windows-versie staat bij de genoemde run.
- De GitHub Actions-API was vanuit de cloud-netwerkproxy niet bereikbaar. De openbare GitHub-webpagina was wel bereikbaar en heeft de geslaagde stappen en artifacts bevestigd.
- Fysieke audio-uitvoer, echte globale Windows-sneltoetsen in combinatie met andere apps en meerdere fysieke monitors zijn niet bevestigd door de offscreen-CI-test. Controleer die bij gebruik op de eigen Windows 11-desktop.
