import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import time
import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from fnaf_desktop.app import Controller
from fnaf_desktop.core import NAMES

@pytest.fixture
def controller(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    c = Controller(app)
    c.timer.stop()
    c.settings['silent'] = True
    yield c
    c.cleanup()
    app.processEvents()

def test_all_personalities_and_motion(controller, monkeypatch):
    monkeypatch.setattr("fnaf_desktop.app.random.random", lambda: .5)
    c = controller
    assert [p.name for p in c.pets] == list(NAMES)
    for p in c.pets:
        p.deadline = time.monotonic()+10
        before = p.posx
        p.direction = 1 if p.posx < p.screen.availableGeometry().center().x() else -1
        p.tick(.1, time.monotonic())
        assert p.posx != before
        p.random_event(time.monotonic())
        p.tick(.1, time.monotonic())
    assert c.pets[3].state == 'run'
    assert c.pets[4].state == 'hide'
    assert c.pets[5].state == 'hide'

def test_click_jumpscare_exclusive_and_recovers(controller):
    c = controller
    QTest.mouseClick(c.pets[0], Qt.MouseButton.LeftButton, pos=QPoint(55, 60))
    assert c.scaring
    windows = list(c.scare_windows)
    c.scare(c.pets[1])
    assert c.scare_windows == windows
    before = c.pets[0].posx
    c.pets[0].tick(.1, time.monotonic())
    assert c.pets[0].posx == before
    QTest.qWait(1850)
    assert not c.scaring
    assert not c.scare_windows
    assert c.audio.guard.original is None

def test_calm_disabled_silent_and_pause(controller):
    c = controller
    c.settings['mode'] = 'calm'
    c.scare(c.pets[0])
    assert not c.scaring
    c.audio.play('scare', c.settings, True)
    assert not c.audio.effect.isPlaying()
    c.pause()
    assert all(not p.isVisible() for p in c.pets)
    c.pause()
    assert all(p.isVisible() for p in c.pets)

def test_rebuild_and_empty_selection(controller):
    c = controller
    c.settings['characters'] = ['Freddy']
    c.settings['count'] = 1
    c.rebuild()
    assert len(c.pets) == 1
    c.settings['characters'] = []
    c.rebuild()
    assert c.pets == []

class FakeSound:
    def __init__(self):
        self.active = False
        self.stops = 0
        self.plays = 0
        self.fail = False
    def stop(self):
        self.active = False
        self.stops += 1
    def setSource(self, url): self.source = url
    def setVolume(self, volume): self.volume = volume
    def play(self):
        if self.fail: raise RuntimeError('audio device failure')
        self.active = True
        self.plays += 1

@pytest.mark.parametrize('fail', [False, True])
def test_audio_playback_volume_and_failure_restore(controller, monkeypatch, fail):
    from fnaf_desktop.core import VolumeGuard
    from fnaf_desktop import audio
    class Endpoint:
        value = .7
        def GetMasterVolumeLevelScalar(self): return self.value
        def SetMasterVolumeLevelScalar(self, value, context): self.value = value
    c = controller
    sound = FakeSound()
    sound.fail = fail
    c.audio.effect = sound
    endpoint = Endpoint()
    c.audio.guard = VolumeGuard(endpoint)
    monkeypatch.setattr(audio.sys, 'platform', 'win32')
    settings = dict(c.settings, silent=False, system_volume=True)
    c.audio.play('freddy_scare', settings, True)
    if fail:
        assert endpoint.value == .7
        assert not sound.active
        assert 'audio device failure' in c.audio.error
    else:
        assert sound.volume == .15
        assert endpoint.value == .15
        c.audio.play('foxy_scare', settings, True)
        assert sound.plays == 2
        assert sound.stops == 2
        c.audio.stop()
        assert not sound.active
        assert endpoint.value == .7


def test_random_image_popups_close_and_limit(controller, monkeypatch):
    c = controller
    assert len(c.image_paths) >= 6
    c.settings['event_chance'] = 1
    monkeypatch.setattr('fnaf_desktop.app.random.random', lambda: 0)
    c.next_image = 0
    c.tick()
    assert len(c.popups) == 1
    assert c.popups[0].isVisible()
    c.image_popup()
    c.image_popup()
    c.image_popup()
    assert len(c.popups) == 3
    c.popups[0].close()
    assert len(c.popups) == 2
    c.settings['image_popups'] = False
    c.next_image = 0
    c.tick()
    assert len(c.popups) == 2


def test_escape_quits_everything_even_during_scare(controller, monkeypatch):
    c = controller
    called = []
    monkeypatch.setattr(c.app, 'quit', lambda: called.append(True))
    c.image_popup()
    windows = [*c.pets, *c.popups, c.dialog]
    c.scare(c.pets[0])
    assert c.scaring
    pressed = [True]
    c.emergency.key_reader = lambda: pressed[0]
    c.emergency.poll(10)
    c.emergency.poll(14.9)
    assert not called
    pressed[0] = False
    c.emergency.poll(15)
    pressed[0] = True
    c.emergency.poll(20)
    c.emergency.poll(25)
    assert called == [True]
    assert c.closing
    assert not c.scaring and not c.scare_windows
    assert not c.timer.isActive() and not c.emergency.timer.isActive()
    assert not c.scare_timer.isActive()
    assert not c.audio.effect.isPlaying()
    assert all(not w.isVisible() for w in windows)
    QTest.qWait(50)
    assert not c.dialog.isVisible()


def test_character_sounds_are_present_and_distinct():
    import hashlib
    import wave
    from fnaf_desktop.app import ASSETS
    hashes = set()
    for name in NAMES:
        path = ASSETS / (name.lower().replace(' ', '_') + '_scare.wav')
        with wave.open(str(path), 'rb') as sound:
            assert sound.getnchannels() == 1
            assert sound.getsampwidth() == 2
            assert 1 <= sound.getnframes()/sound.getframerate() <= 1.5
        hashes.add(hashlib.sha256(path.read_bytes()).digest())
    assert len(hashes) == 6


def test_escape_shutdown_exits_real_process(tmp_path):
    import subprocess
    import sys
    script = '''
import time
from PySide6.QtWidgets import QApplication
from fnaf_desktop.app import Controller
app = QApplication([])
app.setQuitOnLastWindowClosed(False)
c = Controller(app)
c.settings['silent'] = True
c.image_popup()
c.scare(c.pets[0])
c.emergency.key_reader = lambda: True
c.emergency.hold.started = time.monotonic()-5.1
result = app.exec()
assert result == 0 and c.closing
assert not c.timer.isActive() and not c.emergency.timer.isActive()
assert not c.scare_windows and not c.audio.effect.isPlaying()
assert not any(w.isVisible() for w in app.topLevelWidgets())
print('PROCESS_CLOSED')
'''
    environment = dict(os.environ, LOCALAPPDATA=str(tmp_path), QT_QPA_PLATFORM='offscreen')
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, env=environment, timeout=20)
    assert result.returncode == 0, result.stderr
    assert 'PROCESS_CLOSED' in result.stdout
