# Afbeeldingen en geluiden

De PNGs in deze map zijn speciaal voor dit project getekende placeholders. Er zijn geen originele game-assets gedownload. De scripts en deze placeholderbeelden/-geluiden mogen vrij worden aangepast voor dit project; de FNAF-personages en merknamen blijven eigendom van hun respectieve rechthebbenden.

Per personage een map:

- `freddy/`
- `bonnie/`
- `chica/`
- `foxy/`
- `golden_freddy/`
- `springtrap/`

Voeg transparante `walk_00.png`, `walk_01.png`, enzovoort toe. Frames worden alfabetisch afgespeeld en naar 110×150 geschaald; gebruik voor alle frames hetzelfde canvas. Het klikmasker volgt het eerste frame. Optioneel vervangt `scare.png` de jumpscaretekening; dit beeld krijgt een zoom- en wieganimatie. Ontbrekende of onleesbare beelden vallen terug op de vectorillustratie.

Optionele WAV-bestanden direct in `assets/`:

- `freddy.wav`: Freddy's korte omgevingsgeluid.
- `freddy_scare.wav`, `bonnie_scare.wav`, `chica_scare.wav`, `foxy_scare.wav`, `golden_freddy_scare.wav`, `springtrap_scare.wav`: jumpscares.
- `scare.wav`: geluid voor de knop Volume testen.

Gebruik PCM-WAV, bijvoorbeeld mono 16-bit 22050 Hz. Zonder eigen audio genereert de app korte zachte synthetische geluiden in zijn eigen instellingenmap. Langere aangepaste jumpscaregeluiden worden bij het sluiten van de overlay gestopt.

Genereer de originele placeholders opnieuw met `python tools/generate_assets.py` vanuit de projectmap (dit overschrijft bestaande sprites). Voeg alleen bestanden toe die je mag gebruiken.
