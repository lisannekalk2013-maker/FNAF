# Controle voor GitHub-publicatie

- Python 3.13.5: installatie van requirements geslaagd, 14 tests geslaagd.
- Een complete stille Qt-smoketest met Freddy en jumpscare is op Linux/offscreen geslaagd, inclusief automatisch afsluiten.
- Dependency-resolutie voor Windows x64 en Python 3.13 is geslaagd, inclusief pycaw en comtypes. Dit is geen uitgevoerde Windows-build.
- Alle Python-bestanden zijn gecontroleerd op syntaxis. Alle 54 PNGs zijn leesbaar met transparantie; beide meegeleverde WAVs zijn geldige PCM-bestanden.
- `fnaf_desktop/*.py`, `run.py`, `settings.json` en de 54 sprites zijn byte voor byte gelijk aan de vorige ZIP. Alleen bouwinstructies, documentatie, aanvullende geluidsexemplaren, de GitHub-buildworkflow en een deterministische testaanpassing zijn toegevoegd/aangepast.
- De applicatiecode is nagelopen op bestands-, register-, proces- en netwerkaanroepen. De app schrijft eigen instellingen/geluiden/lockbestand, vraagt expliciete toestemming voor de eigen Windows-opstartwaarde en begrenst het systeemvolume alleen als die optie is ingeschakeld. Beide opties staan standaard uit. Geen code voor verspreiding, dataverzameling, beveiligingsuitschakeling of het verwijderen van andere gebruikersbestanden aangetroffen.
- Het bouwscript installeert dependencies in een lokale virtuele omgeving en schrijft bouwresultaten onder build/dist. Het vraagt geen administratorrechten en wijzigt geen Windows-opstartinstellingen. De GitHub-workflow draait alleen op handmatig verzoek, heeft read-only repositoryrechten en uploadt de volledige EXE-map als artifact.
- Windows-EXE, Windows-audio, de globale sneltoets, systeemvak en fysieke monitors zijn niet vanuit deze Linux-machine gevalideerd. De eerste Windows-build moet via Actions of build_windows.bat worden uitgevoerd; controleer daarna die desktopfuncties op Windows. Dit is een codecontrole met tests, geen garantie dat elke mogelijke fout is uitgesloten.
