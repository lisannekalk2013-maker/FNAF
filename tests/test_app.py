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
