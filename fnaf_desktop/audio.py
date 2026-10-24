import math
import struct
import sys
import wave
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

class Audio:
    def __init__(self, parent, folder, assets):
        self.effect = QSoundEffect(parent)
        self.error = ''
        self.assets = assets
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)
        for name, frequency in [('scare', 95), ('ambient', 170)]:
            path = folder / (name + '.wav')
            if not path.exists():
                with wave.open(str(path), 'wb') as w:
                    w.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
                    length = 1.3 if name == 'scare' else .5
                    data = []
                    for i in range(int(22050 * length)):
                        t = i / 22050
                        envelope = min(1, t / .04) * max(0, 1-t/length)
                        sample = .3 * envelope * (math.sin(2*math.pi*frequency*t)+.3*math.sin(2*math.pi*frequency*2.03*t))
                        data.append(struct.pack('<h', int(sample*18000)))
                    w.writeframes(b''.join(data))
        self.effect.statusChanged.connect(self.status_changed)

    def status_changed(self):
        if self.effect.status() == QSoundEffect.Status.Error:
            self.error = 'Het audiobestand kan niet worden afgespeeld.'
            self.stop()

    def resolve(self, name):
        candidates = [self.assets/'audio'/(name+'.wav'), self.assets/(name+'.wav')]
        return next((p for p in candidates if p.is_file()), None)

    def prepare(self, name, settings, scare=False):
        self.stop()
        if settings['silent']:
            return False
        try:
            custom = self.resolve(name)
            path = custom if custom else self.folder / ('scare.wav' if scare else 'ambient.wav')
            self.effect.setSource(QUrl.fromLocalFile(str(path.resolve())))
            self.effect.setVolume(settings['volume'] if scare else min(settings.get('ambient_volume', .08), .5))
            return True
        except Exception as exc:
            self.error = str(exc)
            self.stop()
            return False

    def play(self, name, settings, scare=False):
        if self.prepare(name,settings,scare):
            try:self.effect.play()
            except Exception as exc:
                self.error=str(exc)
                self.stop()

    def stop(self):
        self.effect.stop()
