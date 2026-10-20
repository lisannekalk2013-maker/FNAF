# FNAF Desktop

Een zichtbare Python-desktopapp voor Windows 10/11 met zes geanimeerde desktopmaatjes. Alleen gebruiken op een computer waarvan de eigenaar toestemming heeft gegeven. Dit is een onofficieel fanproject; de meegeleverde tekeningen en synthetische geluiden zijn zelfgemaakt, geen bestanden uit de games.

## Starten op Windows

Installeer Python 3.13 (64-bit), open een terminal in deze map en voer uit:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

Bij het starten opent altijd het instellingenvenster. Selecteer personages, stel hun aantal en snelheid in en klik **Instellingen toepassen**. Sluit het venster om de maatjes op het bureaublad te laten lopen. Met rechtsklikken op een personage of het systeemvakpictogram open je het menu. Zonder systeemvak blijft het instellingenvenster beschikbaar.

**Stoppen:** Ctrl+Shift+Q (globaal op Windows), het systeemvakmenu of de knop Afsluiten. Kan Windows de sneltoets niet registreren, dan blijven jumpscares uit. Er is geen installatie op de achtergrond en geen toetsenbord- of muisvergrendeling.

## Gedrag

- Freddy loopt rustig en speelt soms een kort synthetisch geluid (vervangbaar door een eigen lach).
- Bonnie volgt of wacht bij de cursor totdat die beweegt.
- Chica laat kort een cupcakebericht achter.
- Foxy loopt sneller en trekt af en toe een sprint.
- Golden Freddy verdwijnt tijdelijk en verschijnt opnieuw bij de schermrand.
- Springtrap loopt traag en verdwijnt en verschijnt onverwacht. Het programma verplaatst of inspecteert geen vensters van andere apps; er is geen gegarandeerd verstoppen achter een specifiek venster.

Personages worden verdeeld over de aangesloten monitoren, gebruiken de beschikbare schermruimte en passen zich aan bij het aansluiten of verwijderen van monitoren. Alleen het zichtbare spritegebied vangt klikken op. Bewegingsframes worden circa 30 keer per seconde bijgewerkt; er is geen drukke pollinglus.

Links klikken start één jumpscare: alle personages stoppen, alle monitoren worden 0,2 seconden donker, daarna volgt een geanimeerde zoom met geluid. Na in totaal circa 1,7 seconden verdwijnen de overlays en hervat de beweging. De overlay vraagt geen exclusieve fullscreenmodus en laat muisklikken door. Een geopende app of het systeem kan topmost-vensters soms overdekken.

Rustige modus vertraagt de beweging, verlaagt de gebeurteniskans en schakelt jumpscares uit. Chaosmodus verhoogt de gebeurteniskans. Pauzeren via het menu stopt geluid en jumpscares en verbergt de personages.

## Geluid en systeemvolume

De standaard geluidssterkte van de app is 15%, instelbaar tussen 0 en 50%. Dit is geen garantie over fysieke geluidsdruk: gebruik eerst **Volume testen** op een laag niveau. Volledig stil schakelt alle appgeluiden uit. Er is één audiokanaal, dus geluiden overlappen niet.

De optionele Windows-volumebegrenzing staat standaard uit. Indien ingeschakeld leest de app het oorspronkelijke volume van het standaard audioapparaat, verlaagt het uitsluitend indien nodig en herstelt het na afspelen, bij pauzeren, fouten en normaal afsluiten. De mute-instelling wordt niet gewijzigd. Als de Windows-audio-API niet beschikbaar is, wordt de betreffende afspeelpoging afgebroken. Een geforceerde procesbeëindiging of stroomuitval kan herstel verhinderen; laat de optie uit als je uitsluitend het appvolume wilt aanpassen. Verander tijdens een jumpscare bij voorkeur niet het standaard audioapparaat.

## Instellingen en opstarten

Instellingen en gegenereerde WAV-bestanden staan uitsluitend in `%LOCALAPPDATA%\FNAFDesktop` (op Linux in `~/.config/FNAFDesktop`). `settings.json` in deze projectmap toont de standaardwaarden; persoonlijke instellingen worden bij de eerste toepassing opgeslagen. Een beschadigd instellingenbestand valt terug op veilige standaardwaarden.

Opstarten met Windows staat standaard uit. Aanzetten vraagt een afzonderlijke bevestiging en schrijft alleen de eigen `FNAFDesktop`-waarde onder `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Uitzetten verwijdert die waarde. Verplaats de app daarna niet zonder deze optie opnieuw in te stellen. Zet de optie uit voordat je de projectmap of EXE verwijdert. Er worden geen andere registerwaarden gewijzigd.

## Eigen assets toevoegen

Zie [assets/README.md](assets/README.md). De meegeleverde 54 transparante PNGs zijn originele placeholders. Animatie en gedrag werken ook zonder assets dankzij de vectorfallback. Voor productie kun je gedetailleerdere sprites toevoegen waarvoor je gebruiksrechten hebt.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest -q
```

De tests gebruiken de offscreen Qt-backend: instellingen, volumebegrenzing en herstel met een nep-audioapparaat, alle zes personages, echte Qt-muisklikken, niet-overlappende jumpscares, automatische afloop, pauzeren en stille modus. Ze spelen geen geluid af en wijzigen geen Windows-opstartinstellingen.

Een korte GUI-smoketest is ook beschikbaar:

```powershell
.venv\Scripts\python.exe run.py --smoke
```

Deze stopt automatisch na enkele seconden en gebruikt stille modus. De smoketest gebruikt tijdelijk alleen Freddy en controleert een volledige jumpscarecyclus; persoonlijke instellingen worden niet gewijzigd.

Controleer op een echte Windows-desktop aanvullend: globale sneltoets vanuit een andere app, systeemvak, hoorbare volumetest, herstel van systeemvolume, twee monitoren met verschillende DPI, en expliciet aan/uitzetten van automatisch opstarten. Linux/offscreen-tests bevestigen deze Windows-integratie niet.

## Windows-EXE bouwen

Dubbelklik op `build_windows.bat` op Windows met Python 3.13. Het script gebruikt Python 3.13, maakt een aparte `.venv-windows`, installeert dependencies, voert de tests uit en bouwt met PyInstaller. Je hoeft hiervoor geen Python-opdrachten in te voeren. Het venster blijft open zodat je eventuele fouten kunt lezen. Er is geen administratoraccount nodig.

Resultaat: `dist\FNAFDesktop\FNAFDesktop.exe`. Bewaar en verspreid de **hele** map `FNAFDesktop`, inclusief `_internal`, niet alleen het EXE-bestand. De build is niet ondertekend; schakel Windows-beveiliging niet uit. Een Windows-EXE moet op Windows worden gebouwd; de Linux-cloudmachine bouwt deze niet.

## EXE downloaden via GitHub (zonder lokale Python-opdrachten)

1. Open je repository op GitHub en klik op **Actions**.
2. Als GitHub vraagt workflows toe te staan, klik **I understand my workflows, go ahead and enable them**.
3. Kies links **Build Windows EXE**.
4. Klik rechts op **Run workflow**, kies de gepubliceerde branch en klik op de groene **Run workflow**-knop.
5. Open de nieuwe run en wacht tot die groen is.
6. Klik onder **Artifacts** op **FNAFDesktop-Windows** om de ZIP te downloaden. Je moet bij GitHub ingelogd zijn.
7. Pak alles uit en dubbelklik op `FNAFDesktop.exe`. Bewaar `_internal` erbij.

Deze workflow wordt alleen handmatig gestart en publiceert geen release. Als GitHub Actions voor je account is uitgeschakeld of niet beschikbaar is, gebruik lokaal `build_windows.bat`. Een geslaagde build vervangt niet de controle van de echte Windows-desktopfuncties.

## Projectstructuur

```text
run.py                   startpunt
fnaf_desktop/
  app.py                 vensters, animatie, instellingen, systeemvak, sneltoets
  audio.py               één audiokanaal, synthetisch geluid, Windows-audio
  core.py                instellingen en herstelbare volumebegrenzing
assets/                  PNG-frames en optionele eigen WAVs
generated_audio/         meegeleverde gegenereerde WAV-voorbeelden
.github/workflows/       handmatig starten van een Windows-build op GitHub
tools/generate_assets.py originele placeholderafbeeldingen genereren
settings.json            voorbeeld van de standaardinstellingen
requirements.txt         directe dependencies
build_windows.bat        Windows-build inclusief tests
tests/                   geautomatiseerde tests
```

## Validatie in deze cloudomgeving

De app en dependencies zijn in de Linux-cloudomgeving ook met Python 3.13 geïnstalleerd en getest. De geautomatiseerde tests en een offscreen-start van de app zijn uitgevoerd; zie het opleverbericht voor de resultaten. Echte Windows-desktopintegratie, fysieke audio-uitvoer en het Windows-EXE zijn hier niet gevalideerd. De toepassing doet geen netwerkverzoeken, verzamelt geen persoonsgegevens en wijzigt geen andere gebruikersbestanden.
