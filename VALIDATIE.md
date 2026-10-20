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

Windows-buildstatus:

- Het bijgewerkte build_windows.bat bouwt en controleert een volledige onedir-map en Windows-ZIP.
- De GitHub-workflow start bij pushes naar main, voert tests en build uit en start daarna de gebouwde EXE met een timeout in stille offscreen-modus. Artifacts worden pas na een geslaagde EXE-smoketest geüpload.
- Deze Linux-machine heeft geen native Windows-build uitgevoerd. De Actions-API weigert toegang vanuit de cloud-netwerkproxy en GitHub CLI-authenticatie is niet bruikbaar voor API-aanroepen. Git-push werkt via de bestaande Git-proxy. De actuele Windows-builduitslag en download moeten daarom op GitHub Actions worden bekeken; er wordt geen geslaagde build geclaimd zonder die uitslag.
