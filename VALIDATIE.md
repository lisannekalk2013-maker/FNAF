# Controle van de bijgewerkte versie

- Python 3.13.5 / Linux: 20 tests geslaagd, waaronder een volledige jumpscarecyclus, volumebegrenzing en herstel met een testapparaat, alle personages, pop-upvensters en zes unieke PCM-WAVs.
- Escape moet vijf seconden continu worden vastgehouden; loslaten zet de teller terug. Tests controleren dit met een testklok en verifiëren dat timers, audio, overlays en pop-ups sluiten. Een afzonderlijk Python-proces is gestart en is na de Escape-afsluitroute daadwerkelijk geëindigd.
- De bestaande stiltemodus, volumelimiet, optionele systeemvolumebegrenzing en expliciete bevestiging voor Windows-opstarten blijven behouden. Escape wordt alleen gecontroleerd, niet geblokkeerd; er worden geen toetsen of persoonlijke gegevens opgeslagen.
- Afbeeldingen worden in eigen sluitbare appvensters getoond, zonder externe programma’s te starten of bestanden naar het bureaublad te schrijven. Er zijn maximaal drie pop-ups tegelijk; afbeeldingsvensters sluiten automatisch na 12 seconden en bij afsluiten van de app.
- De illustraties zijn gegenereerde fanillustraties; de zes personagegeluiden en Freddy-lach zijn origineel gesynthetiseerd. Er zijn geen gamebestanden gedownload.
- Windows-buildscript blijft Python 3.13 gebruiken. Er is geen uitgevoerde Windows-build op deze Linux-machine. De echte globale Escape-toets, Windows-audio, systeemvak en meerdere fysieke monitors moeten op Windows worden gecontroleerd; de tests gebruiken gesimuleerde toetsstatus voor de globale Windows-toets.
