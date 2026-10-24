# Validatie FNAF Desktop V3.0

De V3-code is uitgebreid vanuit de bestaande app. Op 24 oktober 2026 is [de native V3 Windows-build](https://github.com/lisannekalk2013-maker/FNAF/actions/runs/40105011847) geslaagd voor codecommit `092de2cb392f713b3b17e1cd48740004d5001bca`.

De Windows-installatie, tests inclusief vensterherkenning, PyInstaller-build, ZIP-verpakking, zelfstandige stille EXE-test en meegebouwde UI Automation-helper zijn geslaagd. Beide artifacts zijn gepubliceerd: `FNAFDesktop-Windows` en `FNAFDesktop-V3.0-Windows-ZIP`. De openbare GitHub-jobpagina bevestigde alle stappen en het eindresultaat Success; de Actions-API was niet bereikbaar vanuit de cloudproxy.

De laatste documentatie-/broncode-ZIP-update wijzigt deze geteste applicatiecode niet.

De appvolume-update is lokaal en in de native Windows-tests gecontroleerd: 100% tijdens WAV-jumpscares, dezelfde volumeregel voor ingebouwde videoaudio, normale geluiden daarna op hun eigen volume, mute en het opslaan/uitschakelen van de optie. Bestaande persoonlijke volumewaarden blijven bewaard.

## Uitgevoerde en geautomatiseerde controles

- Op 24 oktober 2026: **61 tests geslaagd, 1 Windows-test overgeslagen** met Python 3.13 en PySide6 6.8.3 in de Linux-cloud, Qt offscreen.
- De echte app gestart met `--smoke`: stille jumpscare, automatische afloop en procesafsluiting geslaagd.
- Alle 62 meegeleverde PNG-bestanden gedecodeerd en alle 13 WAV-bestanden gecontroleerd: leesbaar.
- Regressiecontrole op bestaande afbeeldingstaken, eigendom, stelen, trekspel, achtervolgen, voorkeuren, glitch-herstel, media-overrides, configuratie en speciale events.
- Nieuwe tests op versnelling/afremmen, vensterklimmen en bewegende doelen, sluiten van een doelvenster, Golden Freddy achter een venster, gesimuleerd slepen en onaangeraakte bronafbeeldingen.
- Geen systeemvakobject; instellingen zijn bij starten verborgen en op verzoek te openen. Verwijderde autostart-/systeemvolumevelden worden niet geladen.
- Afzonderlijke jumpscarecooldowns, automatische afloop, onderbreken met Escape, loslaten/resetten en vijf seconden onafgebroken vasthouden.
- Het afsluitpad beëindigt een echt afzonderlijk appproces en ruimt vensters, audio, timers en een afzonderlijke test-helper op.
- Een simulatie van twintig minuten gedrag controleert begrensde aantallen afbeeldingen en exclusief eigendom. Dit is geen twintig minuten fysieke desktopduurtest.
- Animatiesheet/idle-animatie, ongeldige manifest-fallback, negatieve monitorcoördinaten, DPI-conversie en Golden-frequentie worden apart getest.
- Windows-specifieke test maakt een tijdelijk venster in een apart testproces, leest zijn geometrie en controleert het verdwijnen na sluiten. Deze test wordt op Linux overgeslagen.
- De Windows-workflow bouwt op Python 3.13 x64, test de zelfstandige EXE in stille modus en start de meegebouwde UI Automation-helper. Artifacts worden alleen na deze controles gepubliceerd.
- `tools/package_project.py` controleert ZIP-integriteit en vergelijkt ieder ingepakt bronbestand byte voor byte met het project. De Windows-verpakker weigert een onvolledige build.

## Controle op ongewenste wijzigingen

De applicatie bevat geen register-/autostartwijzigingen, systeemaudiovolume-API, cursorverplaatsing, toetsenblokkering of verplaatsing van echte applicatievensters. Alleen Escape wordt globaal opgevraagd; Ctrl+Shift+Q/S zijn normale Windows-sneltoetsen. Vensters worden alleen geïnventariseerd; visuele trucs vinden in de eigen overlays plaats. De bureaubladfunctie leest afbeeldingen en coördinaten en verandert geen bronbestand of pictogram. Schrijven beperkt zich tot de eigen instellingen/cache/log/lock in de applicatiemap onder LOCALAPPDATA. De app gebruikt geen internetdiensten. Een bestaand V2-opstartitem wordt niet automatisch verwijderd.

## Nog handmatig op Windows te controleren

1. Start de uitgepakte EXE; controleer dat er geen trayicoon/permanent instellingenvenster verschijnt. Open instellingen met de drie beschreven methodes.
2. Open en verplaats bijvoorbeeld Verkenner. Controleer klimmen, zitten, edge-walk, verstoppen en herstel na sluiten.
3. Activeer elke jumpscare; controleer hoorbaar geluid, synchronisatie, automatische afloop en mute. De meegeleverde WAVs zijn synthetische placeholders.
4. Houd Escape vijf seconden vast met een andere applicatie actief, ook tijdens een jumpscare en tijdens afbeeldingstaken. Controleer in Taakbeheer dat EXE/helper verdwenen zijn.
5. Test meerdere fysieke monitoren met verschillende schaling, ook links/boven het hoofdscherm en na loskoppelen. De automatische geometriecontroles vervangen dit niet.
6. Schakel bureaubladafbeeldingen in met een lokale test-PNG op het bureaublad. Controleer de pictogrampositie, het meenemen van de kopie en dat origineel en pictogram blijven staan. Sommige Explorer-providers leveren geen bruikbare coördinaten.
7. Laat de app langer draaien en beoordeel CPU/RAM en zichtbare vloeiendheid op de eigen hardware. Er is geen gemeten garantie op 60 FPS.

Originele FNAF-clips/geluiden en echte gedetailleerde ledemaat-/pose-sprites moeten nog als assets worden toegevoegd. De bestaande transparante illustraties, pose-transformaties en synthetische geluiden zijn de werkende fallback.
