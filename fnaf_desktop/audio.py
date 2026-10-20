import math
import struct
import sys
import wave
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
from .core import VolumeGuard

class Audio:
    def __init__(self, parent, folder, assets):
        self.effect = QSoundEffect(parent)
        self.guard = VolumeGuard()
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
        self.effect.playingChanged.connect(self.finished)
        self.effect.statusChanged.connect(self.status_changed)

    def status_changed(self):
        if self.effect.status() == QSoundEffect.Status.Error:
            self.error = 'Het audiobestand kan niet worden afgespeeld.'
            self.stop()

    def finished(self):
        if not self.effect.isPlaying():
            self.restore()

    def play(self, name, settings, scare=False):
        self.stop()
        if settings['silent']:
            return
        try:
            custom = self.assets / (name + '.wav')
            path = custom if custom.is_file() else self.folder / ('scare.wav' if scare else 'ambient.wav')
            self.effect.setSource(QUrl.fromLocalFile(str(path.resolve())))
            self.effect.setVolume(settings['volume'] if scare else min(.08, settings['volume']))
            if scare and settings['system_volume'] and sys.platform == 'win32':
                if self.guard.endpoint is None:
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    device = AudioUtilities.GetSpeakers()
                    self.guard.endpoint = cast(device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
                self.guard.begin(settings['volume'])
            self.effect.play()
        except Exception as exc:
            self.error = str(exc)
            self.stop()

    def stop(self):
        self.effect.stop()
        self.restore()

    def restore(self):
        try:
            self.guard.restore()
        except Exception as exc:
            self.error = 'Systeemvolume kon niet worden hersteld: ' + str(exc)
