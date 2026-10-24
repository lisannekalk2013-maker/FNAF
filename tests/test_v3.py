import hashlib
from pathlib import Path
import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QSystemTrayIcon
from fnaf_desktop.motion import Motion
from fnaf_desktop.world import Surface, physical_rect
from fnaf_desktop.desktop_images import candidates
from fnaf_desktop.core import normalize
from test_app import controller, advance_jobs


def test_acceleration_braking_and_no_overshoot():
    m=Motion()
    x,y,_=m.advance(0,0,(100,0),100,.1)
    assert 0<x<10
    for _ in range(200):
        x,y,arrived=m.advance(x,y,(100,0),100,.016)
        assert 0<=x<=100
        if arrived:break
    assert arrived and x==100 and m.vx==0


def test_interface_is_opt_in_no_tray_and_no_persistence(controller):
    c=controller
    assert not c.dialog.isVisible()
    assert not c.app.findChildren(QSystemTrayIcon)
    settings=normalize({'startup':True,'system_volume':True})
    assert 'startup' not in settings and 'system_volume' not in settings
    c.open_settings()
    assert c.dialog.isVisible()
    c.dialog.close()
    c.app.processEvents()
    assert not c.dialog.isVisible()


def test_window_climb_tracks_geometry_and_close_recovers(controller):
    c=controller;pet=c.pets[1]
    r=pet.screen.availableGeometry()
    surface=Surface(99,QRect(r.left()+150,r.top()+250,400,300))
    c.world.surfaces={99:surface}
    assert c.director.interactions.window_job(pet,'climb')
    c.settings['speed']=3
    for _ in range(700):
        advance_jobs(c,.1)
        job=c.director.jobs.get(pet)
        if job and job.phase=='perch':break
    assert job.phase=='perch'
    surface.rect.translate(20,10)
    advance_jobs(c,.1)
    assert pet.posy == surface.rect.top()-pet.height()+5
    c.world.surfaces.clear()
    advance_jobs(c,.1)
    assert pet not in c.director.jobs


def test_golden_behind_window_reveals_after_close(controller):
    c=controller;gold=c.pets[4]
    c.world.surfaces={88:Surface(88,QRect(100,200,400,350))}
    assert c.director.interactions.window_job(gold,'behind')
    advance_jobs(c,.1)
    assert not gold.isVisible()
    c.world.surfaces.clear()
    advance_jobs(c,.1)
    assert gold.isVisible() and c.director.jobs[gold].phase=='reveal'
    advance_jobs(c,2)
    assert not gold.isVisible()


def test_simulated_window_drag_does_not_change_surface(controller):
    c=controller;pet=c.pets[0]
    surface=Surface(3,QRect(200,250,300,300));c.world.surfaces={3:surface}
    old=surface.rect.getRect()
    job=c.director.interactions.new(pet,'fake_drag',surface=3,until=c.director.clock+1)
    advance_jobs(c,.1)
    assert pet in c.director.interactions.outlines
    assert surface.rect.getRect()==old
    advance_jobs(c,2)
    assert not c.director.interactions.outlines


def test_desktop_copy_does_not_write_source(controller,tmp_path):
    c=controller;pet=c.pets[3]
    desktop=tmp_path/'Desktop';desktop.mkdir()
    path=desktop/'photo.png';path.write_bytes(c.image_paths[0].read_bytes())
    before=hashlib.sha256(path.read_bytes()).hexdigest()
    assert candidates(desktop)==[path]
    job=c.director.interactions.new(pet,'desktop_inspect',entry={'path':path},target=(200,200),until=0)
    advance_jobs(c,.1)
    assert job.card.owner is pet
    c.clear_images()
    assert hashlib.sha256(path.read_bytes()).hexdigest()==before
    assert list(desktop.iterdir())==[path]


def test_groups_and_flash_switch(controller):
    c=controller;c.settings['window_interactions']=False
    assert c.director.interactions.meeting()
    assert len(c.director.jobs)>=2
    assert not c.events.trigger('golden')
    assert not c.events.trigger('blackout')
    advance_jobs(c,20)
    assert not c.director.jobs


def test_individual_jumpscare_cooldowns(controller):
    c=controller
    c.scare(c.pets[0]);c.end_scare()
    assert 'Freddy' in c.character_cooldowns and 'Bonnie' not in c.character_cooldowns
    c.cooldown_until=0
    c.scare(c.pets[0]);assert not c.scaring
    c.scare(c.pets[1]);assert c.scaring


def test_long_simulation_keeps_bounded_ownership(controller):
    import random
    random.seed(55)
    c=controller
    c.settings.update(desktop_theft=False,window_interactions=False)
    for tick in range(12000):
        c.director.tick(.1)
        for pet in c.pets:c.director.tick_pet(pet,.1)
        c.images.tick(.1)
        if tick%100==0:
            owners=[card.owner for card in c.images.cards if card.owner is not None]
            assert len(owners)==len(set(owners))
            assert len(c.images.cards)<=c.settings['max_images']
            c.app.processEvents()
    c.clear_images()
    assert not c.images.cards and not c.director.jobs


def test_desktop_helper_terminated_on_cleanup(controller):
    import sys
    from PySide6.QtCore import QProcess
    process=controller.desktop.process
    process.start(sys.executable,['-c','import time; time.sleep(60)'])
    assert process.waitForStarted(2000)
    controller.cleanup()
    assert process.state()==QProcess.ProcessState.NotRunning
    assert not controller.desktop.timeout.isActive()


def test_sheet_frames_idle_animation_and_invalid_manifest(controller,tmp_path):
    import json
    from PySide6.QtGui import QPixmap,QPainter,QColor
    from fnaf_desktop.animation import Animator
    pet=controller.pets[0]
    folder=tmp_path/'animations'/'freddy';folder.mkdir(parents=True)
    sheet=QPixmap(32,16);sheet.fill(QColor('red'))
    p=QPainter(sheet);p.fillRect(16,0,16,16,QColor('blue'));p.end()
    sheet.save(str(folder/'sheet.png'))
    manifest=folder/'sheet.json'
    manifest.write_text(json.dumps(dict(file='sheet.png',width=16,height=16,clips={'idle':[0,1],'walk':[0,1]})))
    animator=Animator(tmp_path,'Freddy',pet.frames)
    assert len(animator.clips['idle'])==2
    pet.state='idle';pet.motion.facing=pet.direction=1
    renders=[]
    for clock in (0,.1):
        pet.animation_clock=clock
        frame=QPixmap(pet.size());frame.fill(QColor('transparent'))
        painter=QPainter(frame);animator.draw(painter,pet);painter.end()
        renders.append(frame.toImage())
    assert renders[0]!=renders[1]
    manifest.write_text('{"file":"../outside.png"}')
    assert Animator(tmp_path,'Freddy',pet.frames).clips['walk']==pet.frames


def test_mixed_dpi_negative_monitor_and_golden_frequency(controller,monkeypatch):
    class Monitor:
        def geometry(self):return QRect(-2560,0,1280,720)
        def devicePixelRatio(self):return 2
    assert physical_rect((-2360,100,800,600),[Monitor()])==QRect(-2460,50,400,300)
    c=controller;gold=c.pets[4]
    monkeypatch.setattr('fnaf_desktop.behaviour.random.uniform',lambda a,b:(a+b)/2)
    c.settings['golden_minutes']=15
    first=c.director.golden_delay(gold)
    c.settings['golden_minutes']=30
    assert c.director.golden_delay(gold)==2*first


def test_native_windows_enumeration_lifecycle(tmp_path):
    import sys, subprocess, time
    if sys.platform!='win32':pytest.skip('Requires native Windows window enumeration')
    from fnaf_desktop.world import enumerate_windows
    from PySide6.QtWidgets import QApplication
    marker=tmp_path/'window-id.txt'
    script=r'''
import ctypes,time,sys
from ctypes import wintypes as w
from pathlib import Path
u=ctypes.windll.user32
u.CreateWindowExW.argtypes=[w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,w.HWND,w.HMENU,w.HINSTANCE,ctypes.c_void_p]
u.CreateWindowExW.restype=w.HWND
hwnd=u.CreateWindowExW(0,'STATIC','FNAF test window',0x10CF0000,200,250,400,300,None,None,None,None)
assert hwnd
Path(sys.argv[1]).write_text(str(hwnd))
msg=w.MSG()
while u.GetMessageW(ctypes.byref(msg),None,0,0)>0:
    u.TranslateMessage(ctypes.byref(msg));u.DispatchMessageW(ctypes.byref(msg))
'''
    process=subprocess.Popen([sys.executable,'-c',script,str(marker)])
    try:
        for _ in range(100):
            if marker.exists() or process.poll() is not None:break
            time.sleep(.05)
        assert marker.exists()
        handle=int(marker.read_text())
        found={s.handle:s for s in enumerate_windows(QApplication.instance().screens())}
        assert handle in found
        assert found[handle].rect.width()>150
    finally:
        process.terminate();process.wait(timeout=5)
    assert handle not in {s.handle for s in enumerate_windows(QApplication.instance().screens())}
