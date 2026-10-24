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
    monkeypatch.setattr("fnaf_desktop.app.QCursor.pos", lambda: QPoint(-20000, -20000))
    c = controller
    assert [p.name for p in c.pets] == list(NAMES)
    for p in c.pets:
        p.deadline = time.monotonic()+10
        before = p.posx
        p.direction = 1 if p.posx < p.screen.availableGeometry().center().x() else -1
        p.tick(.1, time.monotonic())
        if p.name == 'Golden Freddy':
            assert p.posx == before and not p.isVisible()
        else:
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
    assert all(p.isVisible() for p in c.pets if p.name != 'Golden Freddy')
    assert not next(p for p in c.pets if p.name == 'Golden Freddy').isVisible()

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
def test_audio_uses_only_app_volume(controller, fail):
    c=controller
    sound=FakeSound();sound.fail=fail
    c.audio.effect=sound
    c.audio.play('freddy_scare',dict(c.settings,silent=False,volume=.15,jumpscare_full_volume=False),True)
    assert sound.volume == .15
    assert not hasattr(c.audio,'guard')
    if fail: assert not sound.active and c.audio.error
    else:
        assert sound.active
        c.audio.stop()
        assert not sound.active


def test_full_volume_jumpscare_then_ambient_and_mute(controller):
    c=controller
    c.audio.effect=FakeSound()
    c.settings.update(silent=False,jumpscare_full_volume=True,volume=.15,ambient_volume=.08)
    c.scare(c.pets[0])
    QTest.qWait(250)
    assert c.scaring and c.audio.effect.active and c.audio.effect.volume==1
    c.end_scare()
    assert not c.audio.effect.active and c.settings['volume']==.15
    c.audio.play('ambient',c.settings)
    assert c.audio.effect.active and c.audio.effect.volume==.08
    c.settings['silent']=True
    c.audio.play('freddy_scare',c.settings,True)
    assert not c.audio.effect.active


@pytest.mark.parametrize('boost,silent,expected', [(True,False,1), (False,False,.15), (True,True,0)])
def test_video_uses_same_jumpscare_volume(controller,tmp_path,boost,silent,expected):
    from fnaf_desktop.app import Scare
    c=controller
    c.settings.update(jumpscare_full_volume=boost,silent=silent,volume=.15)
    c.scare_media=(tmp_path/'not-playing.mp4',[],c.assets/'freddy'/'scare.png')
    c.scare_wav=None
    window=Scare(c,'Freddy',c.app.primaryScreen(),primary=True)
    try:
        output=window.player.audioOutput()
        assert output.volume()==pytest.approx(expected)
        assert output.isMuted()==silent
    finally:
        window.close()
        window.deleteLater()


def test_full_volume_setting_migration_and_roundtrip(controller):
    from fnaf_desktop.core import normalize,load,settings_path
    c=controller
    assert normalize({'volume':.15})['jumpscare_full_volume'] is True
    assert c.dialog.checks['jumpscare_full_volume'].isChecked()
    assert not c.dialog.controls['volume'].isEnabled()
    c.dialog.checks['jumpscare_full_volume'].setChecked(False)
    assert c.dialog.controls['volume'].isEnabled()
    c.dialog.controls['volume'].setValue(.8)
    c.dialog.apply()
    saved=load(settings_path())
    assert saved['jumpscare_full_volume'] is False and saved['volume']==.8


def test_random_image_popups_close_and_limit(controller, monkeypatch):
    c = controller
    assert len(c.image_paths) >= 6
    c.settings['image_chance'] = 1
    c.settings['max_images'] = 3
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


def advance_jobs(c, seconds):
    for _ in range(round(seconds/.1)):
        c.director.clock += .1
        for pet in c.pets:
            c.director.tick_pet(pet, .1)
        c.images.tick(.1)


def test_fetch_moves_continuously_then_drops(controller, monkeypatch):
    c = controller
    pet = c.pets[0]
    c.settings['speed'] = 3
    assert c.director.start_fetch(pet)
    last = (pet.posx, pet.posy)
    saw_carry = False
    for _ in range(1400):
        advance_jobs(c, .1)
        assert abs(pet.posx-last[0]) < 36 and abs(pet.posy-last[1]) < 36
        last = (pet.posx, pet.posy)
        saw_carry |= any(card.owner is pet for card in c.images.cards)
        if pet not in c.director.jobs:
            break
    assert saw_carry
    assert len(c.images.cards) == 1
    assert c.images.cards[0].owner is None
    assert c.images.cards[0].origin is pet


def test_atomic_theft_chase_and_reclaim(controller, monkeypatch):
    c = controller
    freddy, foxy = c.pets[0], c.pets[3]
    c.settings['speed'] = 3
    card = c.images.create(origin=freddy)
    assert c.images.claim(card, freddy)
    assert not c.images.claim(card, foxy)
    monkeypatch.setattr('fnaf_desktop.behaviour.random.random', lambda: 0)
    assert c.director.attempt_theft(foxy, card, direct=True)
    for _ in range(1000):
        advance_jobs(c, .1)
        if card.owner is foxy:
            break
    assert card.owner is foxy
    assert c.director.jobs[freddy].phase == 'chase'
    for _ in range(1000):
        advance_jobs(c, .1)
        if card.owner is freddy:
            break
    assert card.owner is freddy
    assert len([item for item in c.images.cards if item.owner is freddy]) == 1


def test_removed_or_glitched_cards_do_not_leave_stuck_jobs(controller):
    c = controller
    pet = c.pets[1]
    card = c.images.create()
    assert c.director.attempt_theft(pet, card)
    card.close()
    advance_jobs(c, .1)
    assert pet not in c.director.jobs
    card = c.images.create()
    assert c.images.glitch(card)
    assert not card.isVisible()
    c.images.tick(.7)
    assert card.isVisible() and card in c.images.cards
    card.life = .01
    c.images.tick(.1)
    assert card not in c.images.cards


def test_bonnie_inspects_and_chica_prefers_food(controller):
    c = controller
    bonnie, chica = c.pets[1], c.pets[2]
    plain = c.images.create(path=c.image_paths[0])
    foodpath = next(path for path in c.image_paths if 'chica' in path.stem)
    food = c.images.create(path=foodpath)
    assert c.director.attempt_theft(chica)
    assert c.director.jobs[chica].card is food
    assert c.director.attempt_theft(bonnie, plain)
    bonnie.posx, bonnie.posy = plain.xf+plain.width()/2-55, plain.yf-45
    for _ in range(40):
        advance_jobs(c, .1)
        if c.director.jobs[bonnie].phase == 'inspect':
            break
    assert c.director.jobs[bonnie].phase == 'inspect'
    assert plain.owner is None


@pytest.mark.parametrize('kind', ['static','text','laugh','sprint','blackout','taskbar','stare','theft','golden','encounter'])
def test_special_events_exclusive_and_cleanup(controller, kind):
    c = controller
    c.settings['flash_effects']=True
    c.images.create()
    assert c.events.trigger(kind)
    assert not c.events.trigger('static')
    assert c.events.frozen == (kind in ('stare','encounter'))
    c.events.tick(5)
    assert c.events.kind is None and not c.events.windows


def test_escape_interrupts_immediately_and_cooldown(controller):
    c = controller
    c.scare(c.pets[0])
    assert c.scaring
    c.emergency.key_reader = lambda: True
    c.emergency.poll(10)
    assert not c.scaring and not c.scare_windows
    assert not c.closing
    c.scare(c.pets[1])
    assert not c.scaring
    c.emergency.poll(15)
    assert c.closing


def test_custom_night_roundtrip_and_zero_activity(controller):
    from fnaf_desktop.core import load, settings_path
    c = controller
    c.dialog.activity['Bonnie'].setValue(0)
    c.dialog.controls['max_images'].setValue(7)
    c.dialog.controls['fps'].setValue(45)
    c.dialog.controls['drag_chance'].setValue(.8)
    c.dialog.checks['reduced_effects'].setChecked(False)
    c.dialog.apply()
    result = load(settings_path())
    assert result['max_images'] == 7 and result['fps'] == 45
    assert result['drag_chance'] == .8 and not result['reduced_effects']
    assert all(p.name != 'Bonnie' for p in c.pets)
    assert c.timer.interval() == round(1000/45)
    c.timer.stop()


def test_pause_freezes_lifetime_and_hide_releases_images(controller):
    c = controller
    card = c.images.create()
    c.images.claim(card,c.pets[0])
    c.toggle_pets()
    assert card.owner is None and all(not p.isVisible() for p in c.pets)
    c.toggle_pets()
    life = card.life
    c.pause()
    for _ in range(10): c.tick()
    assert card.life == life and not card.isVisible()
    c.pause()
    assert card.isVisible()
    c.clear_images()
    assert not c.images.cards and not c.director.jobs


def test_media_discovery_and_corrupt_files(controller, tmp_path):
    from fnaf_desktop.media import image_files, scare_source
    from PySide6.QtGui import QImage, QColor
    image = QImage(50,50,QImage.Format.Format_ARGB32)
    image.fill(QColor('red'))
    folder=tmp_path/'images'/'random'
    folder.mkdir(parents=True)
    assert image.save(str(folder/'pizza.JPG'))
    assert image.save(str(folder/'meme.webp'))
    (folder/'ignored.txt').write_text('no')
    assert len(image_files(tmp_path)) == 2
    assert scare_source(tmp_path,'Bonnie')[0] is None
    c=controller
    bad=tmp_path/'bad.png'
    bad.write_bytes(b'not an image')
    assert c.images.create(path=bad) is None


def test_user_jumpscare_frames_and_audio_override(controller, monkeypatch, tmp_path):
    from PySide6.QtGui import QImage, QColor
    import shutil
    c=controller
    folder=tmp_path/'images'/'jumpscares'/'bonnie'
    folder.mkdir(parents=True)
    image=QImage(30,30,QImage.Format.Format_ARGB32)
    image.fill(QColor('blue'))
    for i in range(3): assert image.save(str(folder/f'frame_{i:03}.png'))
    audiofolder=tmp_path/'audio'
    audiofolder.mkdir()
    shutil.copy(c.assets/'bonnie_scare.wav',audiofolder/'bonnie_scare.wav')
    monkeypatch.setattr('fnaf_desktop.app.ASSETS',tmp_path)
    c.audio.assets=tmp_path
    assert c.audio.resolve('bonnie_scare') == audiofolder/'bonnie_scare.wav'
    c.scare(c.pets[1])
    assert len(c.active_frames) == 3
    assert c.scare_timer.interval() == 300
    c.end_scare()
    assert not c.active_frames


def test_golden_frequency_and_disabled_events(controller):
    c=controller
    delay=c.events.next_golden
    assert 15*60 <= delay <= 30*60
    c.settings['activity']['Golden Freddy']=0
    assert not c.events.trigger('encounter')
    c.settings['special_events']=False
    assert not c.events.trigger('blackout')


def test_negative_monitor_coordinates_and_image_clamping(controller):
    from PySide6.QtCore import QRect
    c=controller
    class LeftMonitor:
        def availableGeometry(self): return QRect(-1280, -200, 1280, 720)
    pet=c.pets[0]
    pet.screen=LeftMonitor()
    c.settings['image_lifetime']=300
    pet.posx, pet.posy=-1200,-150
    card=c.images.create(screen=pet.screen, origin=pet,position=(-1500,-300))
    assert c.images.claim(card,pet)
    c.images.tick(.1)
    rect=pet.screen.availableGeometry()
    assert rect.left() <= card.xf <= rect.right()-card.width()
    assert rect.top() <= card.yf <= rect.bottom()-card.height()
    c.images.drop(card)
    assert c.director.attempt_theft(c.pets[0],card)
    advance_jobs(c,60)
    assert card in c.images.cards


def test_closing_during_effect_removes_all_windows(controller):
    c=controller
    c.images.create()
    assert c.events.trigger('encounter')
    windows=list(c.events.windows)
    c.cleanup()
    assert not c.events.windows and not c.images.cards
    assert all(not w.isVisible() for w in windows)


def test_corrupt_video_returns_to_placeholder(controller, monkeypatch, tmp_path):
    c=controller
    folder=tmp_path/'images'/'jumpscares'/'freddy'
    folder.mkdir(parents=True)
    (folder/'jumpscare.mp4').write_bytes(b'not an actual video')
    monkeypatch.setattr('fnaf_desktop.app.ASSETS',tmp_path)
    c.scare(c.pets[0])
    QTest.qWait(350)
    assert c.scare_windows[0].failed
    assert c.scare_timer.interval() == 1700
    c.end_scare()
    assert not c.scare_windows
