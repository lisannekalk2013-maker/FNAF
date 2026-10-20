# FNAF Desktop Chaos 2.0 — media

Meegeleverd: gegenereerde fanillustraties, een transparante personage-atlas, 54 PNG-animatie-/gezichtsbestanden, zes camerakaarten, een nieuw donker Golden Freddy-gezicht en synthetische audio. Er zijn geen originele game-opnamen gedownload. Voeg zelf alleen media toe die je mag gebruiken.

## Eigen afbeeldingen

- `images/random/` en `images/memes/`: PNG, JPG/JPEG, WEBP. Worden automatisch ontdekt, ook in submappen.
- `popups/`: de bestaande zes camerakaarten blijven ondersteund als standaardbeelden.
- `images/characters/`: `freddy.png`, `bonnie.png`, `chica.png`, `foxy.png`, `golden_freddy.png`, `springtrap.png` (ook JPG/WEBP). Vervangt de meegeleverde loopillustratie met een wieganimatie.
- Bestaande per-personage mappen met `walk_00.png`, `walk_01.png`, enzovoort blijven werken; alle frames moeten hetzelfde canvas hebben. `scare.png` is het fallbackgezicht.
- `images/golden_freddy/golden_freddy_flicker.png`: vervangen door je eigen Golden-referentie.

Nieuwe draagbare beelden worden elke tien seconden gevonden. Voor aangepaste personages: Toepassen of app opnieuw starten. Afbeeldingen worden alleen in tijdelijke vensters getoond; je bestanden worden niet verplaatst, gewijzigd of verwijderd.

## Originele jumpscares

Per personage: `images/jumpscares/freddy/`, `bonnie/`, `chica/`, `foxy/`, `golden_freddy/`, `springtrap/`.

Plaats daar `jumpscare.mp4` of `jumpscare.webm`, of een reeks `frame_000.png`, `frame_001.png`, enzovoort. Video heeft voorrang. Frames worden op 30 fps afgespeeld, maximaal 120, met een begrensde laadresolutie. Clips worden na maximaal circa tien seconden afgebroken. Ontbrekende media gebruiken de bestaande geanimeerde illustratie.

Eigen audio gaat in `audio/`; zie [audio/README.md](audio/README.md) voor exacte namen. Deze bestanden hebben voorrang op de standaard-WAVs in de assets-hoofdmap. Een eigen video speelt zijn ingebouwde geluid, tenzij er een bijbehorende expliciete `*_scare.wav`-override in `audio/` staat. Het veilige appvolume en de stiltemodus gelden altijd.

De meegeleverde synthetische geluiden horen bij ieder personage maar zijn geen originele FNAF-opnamen. Kies in Custom Night een personage en klik Volume testen. Voor echte media moet je zelf bestanden toevoegen.

## Generators voor ontwikkeling

`python tools/generate_assets.py` bouwt de bestaande sprites/camerakaarten uit `character_atlas.png`. `python tools/generate_sounds.py` bouwt de synthetische standaard-WAVs. Deze overschrijven hun eigen standaardbestanden; gebruik ze niet als je die bestanden handmatig hebt vervangen. In een gebouwde app staat deze hele map onder `_internal/assets`.
