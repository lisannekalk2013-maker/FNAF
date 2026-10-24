# FNAF Desktop V3.0 — Ultimate Desktop Animatronics

Een desktopspel voor Windows 10/11, verder gebouwd op het bestaande Python/PySide6-project. Freddy, Bonnie, Chica, Foxy en Golden Freddy bewegen zelfstandig, onderzoeken vensters en dragen tijdelijke afbeeldingen. Springtrap blijft beschikbaar als zesde personage.

Er is **geen systeemvakpictogram** en instellingen verschijnen alleen op verzoek. **Houd Escape vijf seconden onafgebroken ingedrukt om alles af te sluiten**, ook terwijl een andere app actief is. De app verandert geen bureaubladbestanden, cursor, echte vensterposities of Windows-volume en maakt geen opstartvermelding.

## Downloaden en starten zonder Python-opdrachten

**[Open de geslaagde V3.0-build met Windows-downloads](https://github.com/lisannekalk2013-maker/FNAF/actions/runs/40104314488)** (24 oktober 2026). Tests, EXE-start/afloop en de meegebouwde pictogramlezer zijn geslaagd.

1. Open [Actions → Build Windows EXE](https://github.com/lisannekalk2013-maker/FNAF/actions/workflows/windows-exe.yml).
2. Open de nieuwste **geslaagde** uitvoering voor `main` met V3.0-code.
3. Klik onder **Artifacts** op **FNAFDesktop-Windows**. Hiervoor moet je bij GitHub ingelogd zijn.
4. Pak de download volledig uit en dubbelklik **FNAFDesktop.exe**. Bewaar `_internal` en de andere bestanden bij de EXE. Python is hiervoor niet nodig.
5. Open **Instellingen.bat** om instellingen aan te passen, ook als het spel al draait.

Het artifact **FNAFDesktop-V3.0-Windows-ZIP** bevat de afzonderlijk gemaakte Windows-ZIP binnen de artifact-download. Gebruik het eerste artifact voor de eenvoudigste download.

[downloads/FNAF-project.zip](downloads/FNAF-project.zip) bevat het volledige **broncodeproject**, inclusief assets, requirements en bouwscript. Dit is geen vooraf gebouwde EXE. De daadwerkelijk uitgevoerde controles staan in [VALIDATIE.md](VALIDATIE.md).

## Bediening

- **Linksklik op een personage:** zijn eigen jumpscare, mits ingeschakeld en buiten de cooldown.
- **Rechtsklik:** instellingen, pauze, afbeeldingen tonen/opruimen, personages verbergen en afsluiten.
- **Ctrl+Shift+S:** instellingen openen op Windows. Alternatief: `Instellingen.bat` of starten met `--settings`.
- **Escape kort:** een jumpscare of speciaal effect onderbreken.
- **Escape vijf seconden vasthouden:** alle vensters, geluid, timers en de eventuele pictogramlezer sluiten. Loslaten zet de teller terug.
- **Ctrl+Shift+Q:** tweede globale noodstop. Windows Taakbeheer kan de app ook beëindigen.

Alleen de toestand van Escape wordt passief opgevraagd. De app blokkeert geen toetsen en verplaatst de muis niet. Kan de tweede noodstop niet worden geregistreerd, dan worden jumpscares uitgeschakeld. Personages, effecten en afbeeldingsvensters nemen de toetsenbordfocus niet over; de personages en afbeeldingen zijn zelf wel aanklikbaar.

## Wat is toegevoegd en behouden?

### Beweging en persoonlijkheden

Beweging gebruikt versnelling, afremmen, een vloeiende draai, afstandsgebonden loopframes, pauzes en verschillende snelheden. Er zijn zit-, klim-, spring-, struikel-, kijk- en klopposes, schaduwen en een instelbare schaal. Iedere figuur werkt één taak af voordat een nieuwe wordt gekozen; taken hebben een eindtijd en worden opgeruimd bij ontbrekende doelobjecten.

Freddy beweegt rustig en neemt vensterpauzes. Bonnie volgt de cursor, onderzoekt nieuwe vensters en kan beelden aan Freddy geven. Chica struikelt, reageert op snelle cursorbewegingen en laat soms iets vallen. Foxy sprint, stopt voor de cursor en verstopt zich achter vensters. Golden Freddy verschijnt kort, kijkt en verdwijnt zonder rond te lopen. Het bestaande ophalen van afbeeldingen vanaf de schermrand, meenemen, neerleggen, stelen, trekspel en Freddy/Foxy-achtervolgen blijven werken.

### Windows-vensters

De app leest iedere halve seconde zichtbare vensterrechthoeken. Personages kunnen langs een zijde klimmen, naar de bovenrand stappen, daar zitten/lopen, erop springen, kloppen en achter een venster verdwijnen. Verplaatsen of sluiten van dat venster kan een verschijning veroorzaken. Vensterdoelen worden bijgewerkt wanneer de gebruiker ze verplaatst.

Verdwijnen achter een venster gebeurt met een uitsnede van de eigen overlay. Het meeslepen van een venster gebruikt een verschuivende gestippelde omtrek. Echte applicatievensters worden nooit verplaatst of aangepast. Als er boven een venster onvoldoende ruimte is, wordt een passende andere actie gekozen. Zonder bruikbaar venster blijft normaal bewegen werken.

Personages worden over aangesloten monitoren verdeeld en bewegen binnen hun eigen monitor. Negatieve coördinaten en schaling worden verwerkt; aansluiten/verwijderen van een monitor bouwt overlays opnieuw op. Vrij oversteken tussen monitoren en perfecte fysieke botsingen tussen personages zijn niet geïmplementeerd. Personages kunnen elkaar passeren zodat zij elkaar niet blokkeren.

### Afbeeldingen visueel stelen

Schakel **Visuele kopieën van bureaubladafbeeldingen** in om lokale PNG/JPG/WEBP-bestanden op je eigen bureaublad te gebruiken. Windows UI Automation leest alleen namen en posities van bureaubladpictogrammen. De figuur loopt naar het pictogram, inspecteert het, draagt een tijdelijke afbeeldingskopie mee en laat deze vallen of geeft deze door. Het originele bestand en pictogram blijven staan.

De lezer draait kort in een afzonderlijk proces met een timeout en wordt bij afsluiten beëindigd. Alleen de bovenste bureaubladmap wordt bekeken, maximaal 100 bestanden tot 20 MiB; symlinks en offline/cloud-only bestanden worden overgeslagen. Een pictogram met ontbrekende of dubbelzinnige coördinaten wordt overgeslagen. Ondersteuning hangt af van de UI Automation-provider van Windows Verkenner; een leeg resultaat laat de bestaande meegeleverde afbeeldingen gewoon werken. Andere mappen worden niet doorzocht en niets wordt geüpload.

### Jumpscares, Golden Freddy en groepen

De optie **Tijdens jumpscares naar 100% appvolume** staat standaard aan, ook bij het laden van oudere instellingen. Tijdens de jumpscare gebruiken WAV-geluiden en ingebouwde videoaudio 100% appvolume; overige geluiden behouden hun eigen instelling. Dempen heeft voorrang. Je Windows-hoofdvolume blijft ongewijzigd. Zet de optie uit onder **Geluid & systeem** om zelf het jumpscarevolume (0–1) te kiezen.

Ieder personage heeft een eigen gezicht/geluid en cooldown. Hoogstens één jumpscare tegelijk speelt, met een klein cameratrileffect binnen de overlay en automatische afloop. Meerdere monitoren delen één audiobron. Optionele automatische jumpscares hebben een instelbare kans per 20–40 seconden; deze optie staat standaard uit.

Golden Freddy heeft korte kijkverschijningen, verschijningen achter vensters, `IT'S ME`, optionele gezichtseffecten en een zeldzame ontmoeting die alle figuren tijdelijk laat stilstaan. De Golden-instelling beïnvloedt de zeldzame ontmoetingen en losse verschijningen; activiteit beïnvloedt ook zijn gedrag. Korte flits-/ruis-/verduisteringseffecten staan standaard uit. Ontmoetingen gebruiken een geleidelijke fade, geen snelle stroboscoop.

Groepsactiviteiten zijn onder andere volgen/achtervolgen, bijeenkomen, samen aan een venster zitten, een korte gezamenlijke pose en Bonnie die Freddy een afbeelding geeft. Zij zijn begrensd in duur en frequentie. Stilte- en pauzestand blijven beschikbaar.

## Instellingen

Open instellingen via rechtsklik, Ctrl+Shift+S of `Instellingen.bat`. Pas onder meer aan:

- Personages aan/uit, activiteit 0–20 en aantal figuren.
- Bewegings-/animatiesnelheid, grootte, 15–60 FPS of prestatiemodus met maximaal 30 FPS.
- Venster-, cursor- en groepsinteracties; gebruik van bureaubladafbeeldingen.
- Frequentie van afbeeldingen, meeslepen, stelen, achtervolgen en maximale levensduur/aantallen.
- Jumpscares, fullscreen/klein, automatische kans, individuele cooldown en appvolume.
- Golden Freddy-interval, speciale gebeurtenissen, lichteffecten en volledig dempen.

**Toepassen en opslaan** bewaart alles in `%LOCALAPPDATA%\FNAFDesktop\config.json`. Oude persoonlijke `settings.json` wordt ingelezen als er nog geen `config.json` is. Het voorbeeld in de projectmap overschrijft je persoonlijke instellingen niet. Ongeldige waarden worden begrensd.

De vroegere opties voor systeemvolume en automatisch starten zijn verwijderd; oude waarden worden genegeerd. Als je zelf in V2 automatisch starten had aangezet, schakel die bestaande vermelding uit via Windows **Instellingen → Apps → Opstarten**. V3 schrijft of verwijdert geen registerwaarden.

## Assets en grenzen

De meegeleverde transparante fanillustraties en synthetische karaktergeluiden blijven bruikbaar. **Het zijn geen originele FNAF-jumpscareclips of originele gamegeluiden.** Zonder nieuwe assets gebruiken lopen, zitten, springen en klimmen de bestaande frames met pose-transformaties. Dat levert meer beweging op, maar geen anatomisch realistische ledemaatanimatie.

Er is ondersteuning voor echte animatiereeksen en spritesheets, inclusief idle-, loop-, draai-, zit- en klimclips. Voeg geschikt materiaal toe om die poses te vervangen. Eigen geanimeerde jumpscares gebruiken MP4/WEBM of PNG-frames met bijbehorende WAVs. Zie [assets/README.md](assets/README.md) voor exacte paden, formaat en een spritesheetvoorbeeld.

De app streeft naar 60 FPS; werkelijke prestaties hangen af van hardware, schermen en media. Mixed-DPI, fysieke audio en globale toetsen moeten ook op de eigen Windows-desktop worden geprobeerd. De tests simuleren gedrag en controleren levensduur/eigendom/afsluiten; zij vervangen geen visuele duurtest op echte monitoren.

## Zelf bouwen met Python 3.13

Dubbelklik **build_windows.bat** op Windows 10/11 met **Python 3.13 64-bit**. Het script maakt `.venv-windows`, installeert requirements, test en bouwt de complete Windows-map:

- `dist\FNAFDesktop\FNAFDesktop.exe`, `_internal` en `Instellingen.bat`.
- `dist\FNAFDesktop-V3.0-Windows.zip`.

Bewaar en verplaats de hele map. Er zijn geen administratorrechten nodig. De EXE is niet ondertekend; schakel beveiliging niet uit.

Voor ontwikkeling:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py --settings
.venv\Scripts\python.exe -m pytest -q
```

De bestaande modules voor afbeeldingen, events, audio en noodstop blijven behouden. Nieuwe modules: `motion.py` (beweging), `animation.py` (clips/poses), `world.py` (venstergeometrie), `interactions.py` (venster-/cursor-/groepsacties) en `desktop_images.py` (pictogramlezer). Er worden geen AI-modellen of externe diensten gebruikt.
