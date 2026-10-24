# FNAF Desktop V3.0 — vervangbare media

Meegeleverd zijn gegenereerde transparante fanillustraties, acht loopframes per personage, camerakaarten, een Golden Freddy-gezicht en verschillende synthetische geluiden. Er zijn geen originele gameclips of gamegeluiden meegeleverd. De bestaande loopframes zijn pose-/wiegeffecten op illustraties. Voor realistische beweging van afzonderlijke ledematen zijn getekende of gerenderde animatiereeksen nodig.

## Afbeeldingen

- `images/random/` en `images/memes/`: PNG, JPG/JPEG, WEBP, ook in submappen.
- `popups/`: de bestaande camerakaarten.
- `images/characters/`: optionele `freddy.png`, `bonnie.png`, `chica.png`, `foxy.png`, `golden_freddy.png`, `springtrap.png` (ook JPG/WEBP). Dit vervangt de oude loopillustratie.
- `<personage>/walk_00.png` enzovoort: bestaande loopframes; `scare.png` is het fallbackgezicht.
- `images/golden_freddy/golden_freddy_flicker.png`: het Golden-gezicht.

Gebruik gelijke canvassen met transparante achtergrond; zet de voeten telkens op dezelfde baseline. Nieuwe losse afbeeldingen worden iedere tien seconden gevonden; herstart of klik Toepassen voor gewijzigde personages.

## Echte karakteranimaties

Zet nieuwe frames in `animations/freddy/`, `animations/bonnie/`, enzovoort. Ondersteunde namen:

```text
walk_000.png, walk_001.png, ...
idle_000.png, ...
run_000.png, ...
turn_000.png, ...
sit_000.png, ...
climb_000.png, ...
jump_000.png, ...
trip_000.png, ...
watch_000.png, ...
knock_000.png, ...
interact_000.png, ...
```

Maximaal 60 frames per reeks, begrensd ingeladen tot 512 pixels. Loopframes volgen de afgelegde afstand; andere reeksen volgen tijd. Zonder passende reeks gebruikt de app de bestaande illustratie met een draai-/zit-/spring-/klimtransformatie en schaduw.

Een spritesheet kan ook. Maak in dezelfde map `sheet.json` en de genoemde PNG:

```json
{
  "file": "sheet.png",
  "width": 110,
  "height": 150,
  "clips": {
    "walk": [0, 1, 2, 3, 4, 5, 6, 7],
    "idle": [8, 9],
    "sit": [10, 11],
    "turn": [12, 13]
  }
}
```

`width`/`height` zijn de frame-afmetingen. Indexen tellen vanaf linksboven, rij voor rij. Maximaal 1024 pixels per framezijde en 16.777.216 pixels per sheet. Frames uit de sheet hebben voorrang op bestanden met dezelfde statenaam. Een ontbrekende/ongeldige sheet valt terug op aanwezige frames.

## Jumpscares en audio

Per personage: `images/jumpscares/freddy/`, `bonnie/`, `chica/`, `foxy/`, `golden_freddy/`, `springtrap/`.

Plaats `jumpscare.mp4` of `jumpscare.webm`, of `frame_000.png`, `frame_001.png`, enzovoort. Video heeft voorrang. Frames spelen op 30 fps, maximaal 120 frames, tot 512 pixels ingeladen. Video wordt na maximaal circa tien seconden gestopt. Ontbrekende media gebruiken het bestaande bewegende gezicht.

Eigen PCM-WAVs gaan in `audio/`: `freddy_scare.wav`, `bonnie_scare.wav`, `chica_scare.wav`, `foxy_scare.wav`, `golden_freddy_scare.wav`, `springtrap_scare.wav`. Overige geluiden: `freddy.wav`, `foxy_sprint.wav`, `camera_static.wav`, `golden_glitch.wav`, `theft.wav`, `ambient.wav`, `chica.wav`.

Video gebruikt zijn ingebouwde audio tenzij een expliciete bijbehorende WAV in `audio/` staat; dan is videoaudio uit. Het appvolume en mute gelden voor beide. Windows-volume blijft ongewijzigd. Test eigen geluid zacht via instellingen.

In een gebouwde EXE staat deze map onder `_internal/assets`. Voeg alleen media toe die je mag gebruiken. De ontwikkelscripts `tools/generate_assets.py` en `tools/generate_sounds.py` overschrijven hun eigen standaardbestanden: voer deze niet uit over handmatig vervangen defaults.
