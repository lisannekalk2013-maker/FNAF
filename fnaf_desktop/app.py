import ctypes
import math
from pathlib import Path
import random
import sys
import time

from PySide6.QtCore import Qt, QTimer, QPoint, QAbstractNativeEventFilter, QLockFile, QUrl
from PySide6.QtGui import QColor, QPainter, QPen, QCursor, QPixmap, QIcon, QAction
from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QVBoxLayout, QLabel,
    QCheckBox, QSlider, QSpinBox, QComboBox, QPushButton, QMenu, QMessageBox, QScrollArea)
from .core import NAMES, load, save, settings_path, normalize
from .audio import Audio
from .emergency import EscapeExit
from .images import ImageManager
from .behaviour import BehaviourDirector
from .media import image_files, scare_source, safe_pixmap, IMAGE_EXTENSIONS
from .events import EventManager
from .settings_ui import Settings
from .motion import Motion, steer
from .animation import Animator
from .world import WindowWorld
from .desktop_images import DesktopImages
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

COLORS = ['#986331', '#7954ad', '#e4c144', '#b44c38', '#c7a63f', '#79834d']
ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
ASSETS = ROOT / 'assets'


def draw_character(p, name, frame=0, scary=False):
    """Original vector art, also used as the no-assets fallback."""
    color = QColor(COLORS[NAMES.index(name)])
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor('#221c23'), 3))
    p.setBrush(color)
    bunny = name in ('Bonnie', 'Springtrap')
    if bunny:
        p.drawRoundedRect(27, 0, 16, 44, 7, 7)
        p.drawRoundedRect(65, 4, 16, 40, 7, 7)
    else:
        p.drawEllipse(15, 24, 25, 26)
        p.drawEllipse(70, 24, 25, 26)
    stride = math.sin(frame * .6) * 7
    p.drawRoundedRect(29, int(113+stride), 20, 30, 5, 5)
    p.drawRoundedRect(61, int(113-stride), 20, 30, 5, 5)
    p.drawRoundedRect(25, 79, 60, 48, 14, 14)
    p.drawRoundedRect(10, int(82-stride), 16, 37, 6, 6)
    p.drawRoundedRect(84, int(82+stride), 16, 37, 6, 6)
    p.drawRoundedRect(20, 34, 70, 59, 19, 19)
    p.setBrush(QColor('#e5c997'))
    p.drawEllipse(35, 64, 42, 23)
    p.setBrush(QColor('black'))
    p.drawEllipse(48, 61, 15, 10)
    p.setBrush(QColor('#ff3333' if scary else '#f4f4d9'))
    p.drawEllipse(33, 48, 16, 17)
    p.drawEllipse(62, 48, 16, 17)
    p.setBrush(QColor('black'))
    for x in (40, 69):
        p.drawEllipse(x, 52, 6, 10)
    if name in ('Freddy', 'Golden Freddy'):
        p.setBrush(QColor('#17151c'))
        p.drawRect(35, 18, 40, 7)
        p.drawRect(41, 3, 28, 18)
    if name == 'Foxy':
        p.setBrush(QColor('#15131a'))
        p.drawRect(60, 46, 23, 20)
        p.drawLine(22, 43, 83, 69)
    if name == 'Chica':
        p.setBrush(QColor('#ff9c28'))
        p.drawPolygon([QPoint(38, 68), QPoint(76, 68), QPoint(56, 83)])
        p.setPen(QColor('white'))
        p.drawText(35, 105, 'EAT!')
    if name == 'Springtrap':
        p.setPen(QPen(QColor('#272d1e'), 3))
        for x, y in ((30, 43), (67, 80), (38, 110)):
            p.drawLine(x, y, x+14, y+7)
    if name == 'Bonnie':
        p.setBrush(QColor('#a92842'))
        p.drawEllipse(40, 89, 30, 10)
    if scary:
        p.setBrush(QColor('#160b13'))
        p.drawRoundedRect(32, 70, 48, 21, 5, 5)
        p.setPen(QPen(QColor('ivory'), 3))
        for x in range(36, 79, 7):
            p.drawLine(x, 71, x, 79)
            p.drawLine(x, 84, x, 90)


class Pet(QWidget):
    def __init__(self, controller, name, screen):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.c, self.name, self.screen = controller, name, screen
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        scale=controller.settings['sprite_scale']*max(.8,min(1.4,screen.availableGeometry().height()/1080))
        self.setFixedSize(round(110*scale),round(180*scale))
        self.motion=Motion()
        self.look=0
        self.pose_progress=0
        self.confused_until=0
        self.roam_target=None
        self.frame = 0
        self.animation_clock = 0
        self.direction = random.choice((-1, 1))
        self.state = 'walk'
        self.watch_cursor = QCursor.pos()
        self.until = 0
        self.deadline = time.monotonic() + random.uniform(3, 10)
        self.frames = [QPixmap(str(p)) for p in sorted((ASSETS / name.lower().replace(' ', '_')).glob('walk_*.png'))]
        self.frames = [p for p in self.frames if not p.isNull()]
        slug = name.lower().replace(' ', '_')
        custom = next((p for p in sorted((ASSETS/'images'/'characters').glob(slug+'.*')) if p.suffix.lower() in IMAGE_EXTENSIONS), None)
        if custom:
            image = safe_pixmap(custom, 512)
            if not image.isNull():
                self.frames = [image]
        self.animator=Animator(ASSETS,name,self.frames)
        r = screen.availableGeometry()
        self.posx = float(random.randint(r.left(), max(r.left(), r.right()-self.width())))
        self.posy = float(random.randint(r.top(), max(r.top(), r.bottom()-self.height())))
        self.move(int(self.posx), int(self.posy))
        # Union masks for both directions and poses; transparent pixels stay pass-through.
        silhouette=QPixmap(self.size())
        silhouette.fill(Qt.GlobalColor.transparent)
        painter=QPainter(silhouette)
        for direction in (-1,1):
            self.motion.facing=direction
            for state in ('walk','sit','jump','trip','climb'):
                self.state=state
                for phase in (0,.5,1):
                    self.pose_progress=phase
                    self.animator.draw(painter,self)
        painter.end()
        from PySide6.QtGui import QRegion
        self.base_mask=QRegion(silhouette.mask()) if self.frames else QRegion(self.rect())
        for dx,dy in ((4,0),(-4,0),(0,4),(0,-4)):
            self.base_mask=self.base_mask.united(self.base_mask.translated(dx,dy))
        self.base_mask=self.base_mask.intersected(QRegion(self.rect()))
        self.setMask(self.base_mask)
        self.motion.facing=self.direction
        self.state='walk'
        self.show()

    def paintEvent(self, event):
        p=QPainter(self)
        if self.frames:
            self.animator.draw(p,self)
        else:
            p.scale(self.width()/110,self.width()/110)
            p.translate(0,30)
            draw_character(p,self.name,self.frame)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.c.menu.popup(QCursor.pos())
        elif event.button() == Qt.MouseButton.LeftButton:
            self.c.scare(self)

    def tick(self, dt, now):
        if self.c.scaring:return
        self.animation_clock+=dt
        cursor=QCursor.pos()
        if self.c.settings['cursor_interactions']:
            self.look=max(-25,min(25,(cursor.x()-self.posx-self.width()/2)/12))
        else:self.look=0
        if self.c.director.tick_pet(self,dt):
            self.update()
            return
        r=self.screen.availableGeometry()
        if self.c.settings['cursor_interactions']:
            if self.name=='Chica' and self.c.director.interactions.cursor_speed>1800 and now>self.confused_until:
                self.confused_until=now+15
                self.c.director.interactions.new(self,'trip',until=self.c.director.clock+1.5)
                return
        if self.state=='hide':
            if now>=self.until:self.state='walk';self.show()
            else:return
        if now>=self.deadline:
            self.deadline=now+random.uniform(3,9)
            choices=['walk','walk','watch','idle','run' if self.name=='Foxy' else 'walk']
            if self.c.settings['cursor_interactions']:choices+=['follow' if self.name in ('Bonnie','Foxy') else 'watch']
            self.state=random.choice(choices)
            self.until=now+random.uniform(.8,2.5)
            self.roam_target=self.c.director.destination(self)
            if self.c.settings['special_events'] and random.random()<.06:
                self.random_event(now)
                if self.state=='hide':return
        if self.state in ('watch','idle') and now<self.until:
            self.motion.stop();self.update();return
        if self.state in ('watch','idle'):self.state='walk'
        speed={'Freddy':45,'Bonnie':70,'Chica':55,'Foxy':140,'Springtrap':30}[self.name]*self.c.settings['speed']
        if self.state=='run':speed*=2.4
        if self.c.settings['mode']=='calm':speed*=.6
        if self.state=='follow' and self.c.settings['cursor_interactions']:
            dx,dy=self.posx+self.width()/2-cursor.x(),self.posy+self.height()/2-cursor.y()
            length=max(1,math.hypot(dx,dy))
            target=(cursor.x()+dx/length*70-self.width()/2,cursor.y()+dy/length*70-self.height()/2)
            if self.name=='Foxy':speed*=2
        else:
            target=self.roam_target or (self.posx+self.direction*180,self.posy+random.uniform(-40,40))
            self.roam_target=target
        target=self.c.director.interactions.target(self,target)
        if steer(self,target,dt,speed,self.state):
            self.state='idle';self.until=now+random.uniform(.5,1.5);self.deadline=self.until;self.roam_target=None
        self.posx=max(r.left(),min(r.right()-self.width(),self.posx))
        self.posy=max(r.top(),min(r.bottom()-self.height(),self.posy))
        self.move(round(self.posx),round(self.posy))

    def random_event(self, now):
        if self.name in ('Golden Freddy', 'Springtrap') or random.random() < .15:
            self.state = 'hide'
            self.until = now + random.uniform(2, 7)
            self.posx = float(self.screen.availableGeometry().left())
            self.move(round(self.posx), round(self.posy))
            self.hide()
        elif self.name == 'Foxy':
            self.state, self.until = 'run', now+2
            if random.random() < .3:
                self.direction = 1 if QCursor.pos().x() > self.posx else -1
            self.c.audio.play('foxy_sprint', self.c.settings)
        elif self.name == 'Bonnie':
            self.state, self.until, self.watch_cursor = 'watch', now+1, QCursor.pos()
        elif self.name == 'Chica':
            self.c.audio.play('chica', self.c.settings)
            self.c.popup('🧁  Chica heeft een cupcake achtergelaten!', self.pos())
        elif self.name == 'Freddy':
            self.c.audio.play('freddy', self.c.settings)
        else:
            self.c.audio.play('ambient', self.c.settings)
            self.c.popup('IT’S ME — de nachtdienst roept…', self.pos())


class Scare(QWidget):
    def __init__(self, c, name, screen, primary=False):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus | Qt.WindowType.WindowTransparentForInput)
        self.c, self.name, self.started = c, name, time.monotonic()
        rect = screen.geometry()
        if not c.settings['fullscreen']:
            rect = screen.availableGeometry()
            rect.setWidth(min(640, rect.width()))
            rect.setHeight(min(480, rect.height()))
            rect.moveCenter(screen.availableGeometry().center())
        self.setGeometry(rect)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        video, _, fallback = c.scare_media
        self.image = safe_pixmap(fallback, 1000)
        self.player = None
        self.failed = False
        self.primary = primary
        self.video_widget = None
        if video:
            self.video_widget = QVideoWidget(self)
            self.video_widget.setGeometry(self.rect())
            self.video_widget.hide()
            self.player = QMediaPlayer(self)
            self.player.setVideoOutput(self.video_widget)
            if primary and not c.scare_wav:
                output = QAudioOutput(self)
                output.setVolume(min(.5, c.settings['volume']))
                output.setMuted(c.settings['silent'])
                self.player.setAudioOutput(output)
            self.player.setSource(QUrl.fromLocalFile(str(video.resolve())))
            self.player.errorOccurred.connect(self.video_failed)
            if primary:
                self.player.mediaStatusChanged.connect(lambda status: c.end_scare() if status == QMediaPlayer.MediaStatus.EndOfMedia else None)
                self.player.durationChanged.connect(lambda duration: c.scare_timer.start(min(10200, max(1200, duration+200))) if duration and c.scaring else None)
        self.show()

    def start_video(self):
        if self.player and not self.failed:
            self.video_widget.show()
            self.player.play()

    def video_failed(self, *_):
        self.failed = True
        if self.player:
            self.player.stop()
            self.video_widget.hide()
        if self.primary and self.c.scaring:
            self.c.scare_timer.start(1700)
            self.c.audio.play(self.name.lower().replace(' ', '_')+'_scare', self.c.settings, True)
        self.update()

    def closeEvent(self, event):
        if self.player:
            self.player.stop()
        super().closeEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor('#080609'))
        elapsed = time.monotonic()-self.started
        if elapsed < .2:
            return
        p.translate(math.sin(elapsed*41)*3,math.cos(elapsed*37)*2)
        if self.video_widget is not None:
            self.video_widget.move(round(math.sin(elapsed*41)*3),round(math.cos(elapsed*37)*2))
        if self.c.active_frames:
            index = min(len(self.c.active_frames)-1, int((elapsed-.2)*30))
            image = self.c.active_frames[index]
            scaled = image.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((self.width()-scaled.width())//2, (self.height()-scaled.height())//2, scaled)
            return
        # Different character rhythms, smooth zoom; no strobe.
        frequency = {'Freddy': 9, 'Bonnie': 13, 'Chica': 11, 'Foxy': 17, 'Golden Freddy': 5, 'Springtrap': 7}[self.name]
        size = min(self.height()*.85, 600) * (1+.07*math.sin(elapsed*frequency))
        p.translate(self.width()/2-size*.37, self.height()/2-size*.5)
        p.scale(size/150, size/150)
        if not self.image.isNull():
            p.drawPixmap(0, 0, 110, 150, self.image)
        else:
            draw_character(p, self.name, int(elapsed*30), True)


class Hotkey(QAbstractNativeEventFilter):
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.registered = False
        if sys.platform == 'win32':
            self.registered = bool(ctypes.windll.user32.RegisterHotKey(None, 18021, 0x4006, ord('Q')))
            self.settings_registered=bool(ctypes.windll.user32.RegisterHotKey(None,18022,0x4006,ord('S')))

    def nativeEventFilter(self, kind, message):
        if sys.platform == 'win32':
            from ctypes.wintypes import MSG
            msg = MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == 18022:
                self.c.open_settings()
                return True,0
            if msg.message == 0x0312 and msg.wParam == 18021:
                self.c.app.quit()
                return True, 0
        return False, 0

    def close(self):
        if self.registered:
            ctypes.windll.user32.UnregisterHotKey(None, 18021)
        if getattr(self,'settings_registered',False):
            ctypes.windll.user32.UnregisterHotKey(None,18022)


class Controller:
    def __init__(self, app):
        self.app = app
        self.assets = ASSETS
        self.settings = load(settings_path())
        self.pets, self.scare_windows, self.popups = [], [], []
        self.scaring = False
        self.active_frames = []
        self.cooldown_until = 0.0
        self.character_cooldowns={}
        self.scare_character=None
        self.next_auto_scare=time.monotonic()+30
        self.closing = False
        self.next_scan = time.monotonic()+10
        self.next_image = time.monotonic() + random.uniform(12, 25)
        self.image_paths = image_files(ASSETS)
        self.images = ImageManager(self)
        self.world=WindowWorld(self)
        self.desktop=DesktopImages(self)
        self.director = BehaviourDirector(self)
        self.events = EventManager(self)
        self.audio = Audio(app, settings_path().parent / 'audio', ASSETS)
        self.menu = QMenu()
        self.menu.addAction('Instellingen', self.open_settings)
        self.menu.addAction('FNAF-afbeelding tonen', self.image_popup)
        self.menu.addAction('Alles pauzeren / hervatten', self.pause)
        self.menu.addAction('Afbeeldingen opruimen', self.clear_images)
        self.menu.addAction('Personages verbergen / tonen', self.toggle_pets)
        self.menu.addAction('Afsluiten (Ctrl+Shift+Q)', app.quit)
        self.dialog = Settings(self)
        self.emergency = EscapeExit(app, self.quit, interrupt_callback=self.interrupt_effects)
        self.hotkey = Hotkey(self)
        app.installNativeEventFilter(self.hotkey)
        self.paused = False
        self.pets_hidden = False
        self.last = time.monotonic()
        self.timer = QTimer(app)
        self.timer.timeout.connect(self.tick)
        self.timer.start(round(1000/(min(30,self.settings['fps']) if self.settings['performance_mode'] else self.settings['fps'])))
        self.scare_timer = QTimer(app)
        self.scare_timer.setSingleShot(True)
        self.scare_timer.timeout.connect(self.end_scare)
        app.aboutToQuit.connect(self.cleanup)
        app.screenRemoved.connect(lambda _: self.rebuild())
        app.screenAdded.connect(lambda _: self.rebuild())
        self.rebuild()
        if sys.platform == 'win32' and not self.hotkey.registered:
            self.settings['jumpscares'] = False
            self.dialog.checks['jumpscares'].setChecked(False)
            QMessageBox.warning(self.dialog, 'Sneltoets niet beschikbaar', 'Ctrl+Shift+Q kon niet worden geregistreerd. Jumpscares zijn uitgeschakeld. Sluit af met ESC 5 seconden of rechtsklik op een personage.')

    def interrupt_effects(self):
        self.events.clear()
        self.end_scare()

    def quit(self):
        self.cleanup()
        self.app.quit()

    def open_settings(self):
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def rebuild(self):
        self.end_scare()
        self.events.clear()
        self.director.clear()
        self.images.clear()
        for pet in self.pets:
            pet.close()
            pet.deleteLater()
        self.pets = []
        names = [n for n in self.settings['characters'] if self.settings['activity'][n] > 0]
        screens = self.app.screens()
        if names and screens:
            for i in range(self.settings['count']):
                pet = Pet(self, names[i % len(names)], screens[i % len(screens)])
                self.pets.append(pet)
                if pet.name == 'Golden Freddy':
                    self.director.tick_pet(pet, 0)
                if getattr(self, 'pets_hidden', False) or getattr(self, 'paused', False):
                    pet.hide()

    def clear_images(self):
        self.director.clear()
        self.images.clear()

    def toggle_pets(self):
        self.pets_hidden = not self.pets_hidden
        if self.pets_hidden:
            self.events.clear()
            self.director.clear()
        for pet in self.pets:
            pet.setVisible(not self.pets_hidden and not self.paused and pet.state != 'hide')

    def pause(self):
        self.paused = not self.paused
        if self.paused:
            self.end_scare()
        self.events.clear()
        self.images.visibility(not self.paused)
        for outline in self.director.interactions.outlines.values():outline.setVisible(not self.paused)
        for pet in self.pets:
            pet.setVisible(not self.paused and not self.pets_hidden and pet.state != 'hide')

    def tick(self):
        now = time.monotonic()
        dt, self.last = min(.1, now-self.last), now
        self.world.tick(dt)
        if not self.paused:self.desktop.tick(now)
        if now>=self.next_auto_scare:
            self.next_auto_scare=now+random.uniform(20,40)
            if self.settings['auto_jumpscares'] and self.pets and not self.pets_hidden and random.random()<self.settings['auto_scare_chance']:
                self.scare(random.choice(self.pets))
        if now >= self.next_scan:
            self.next_scan = now+10
            self.image_paths = image_files(ASSETS)
        if not self.paused and not self.scaring and not self.events.frozen and now >= self.next_image:
            self.next_image = now + random.uniform(12, 25) * (2 if self.settings['mode'] == 'calm' else .5 if self.settings['mode'] == 'chaos' else 1)
            if self.settings['image_popups'] and random.random() < self.settings['image_chance']:
                self.image_popup()
        if not self.paused and not self.scaring:
            self.events.tick(dt)
        if not self.paused and not self.scaring and not self.events.frozen:
            if not self.pets_hidden:
                self.director.tick(dt)
                for pet in self.pets:
                    pet.tick(dt, now)
            self.images.tick(dt)
        for window in self.scare_windows:
            window.update()

    def scare(self, pet):
        if self.scaring or self.paused or self.emergency.was_pressed or time.monotonic() < self.cooldown_until or time.monotonic()<self.character_cooldowns.get(pet.name,0) or not self.settings['jumpscares'] or self.settings['mode'] == 'calm':
            return
        if sys.platform == 'win32' and not self.hotkey.registered:
            return
        self.events.clear()
        self.audio.stop()
        self.scaring = True
        self.scare_character=pet.name
        self.scare_media = scare_source(ASSETS, pet.name)
        video, frame_paths, _ = self.scare_media
        self.active_frames = [safe_pixmap(path, 512) for path in frame_paths[:120]]
        self.active_frames = [frame for frame in self.active_frames if not frame.isNull()]
        slug = pet.name.lower().replace(' ', '_')
        self.scare_wav = self.audio.resolve(slug+'_scare')
        if video and not (ASSETS/'audio'/(slug+'_scare.wav')).is_file():
            self.scare_wav = None
        if not video or self.scare_wav:
            self.audio.prepare(slug+'_scare',self.settings,True)
        self.scare_windows = [Scare(self, pet.name, screen, i == 0) for i, screen in enumerate(self.app.screens())]
        active_windows = self.scare_windows
        def start():
            if not self.scaring or self.scare_windows is not active_windows:
                return
            if not video or self.scare_wav:
                self.audio.play(slug+'_scare', self.settings, True)
            for window in active_windows:
                window.start_video()
        QTimer.singleShot(200, start)
        self.scare_timer.start(10200 if video else round(len(self.active_frames)/30*1000+200) if self.active_frames else 1700)

    def end_scare(self):
        if hasattr(self, 'scare_timer'):
            self.scare_timer.stop()
        if self.scaring:
            self.cooldown_until = time.monotonic()+2
            self.character_cooldowns[self.scare_character]=time.monotonic()+self.settings['jumpscare_cooldown']
        self.scaring = False
        self.audio.stop()
        for window in self.scare_windows:
            window.close()
            window.deleteLater()
        self.scare_windows = []
        self.active_frames = []

    def popup(self, text, pos):
        if len(self.popups) >= 3:
            return
        label = QLabel(text, None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowDoesNotAcceptFocus)
        label.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        label.setStyleSheet('background:#261d2e;color:#eed6a3;padding:15px;border:1px solid #a4804c')
        label.adjustSize()
        screen = self.app.screenAt(pos) or self.app.primaryScreen()
        r = screen.availableGeometry()
        label.move(max(r.left(), min(pos.x(), r.right()-label.width())), max(r.top(), min(pos.y(), r.bottom()-label.height())))
        label.show()
        self.popups.append(label)
        def remove():
            if label in self.popups:
                self.popups.remove(label)
                label.close()
                label.deleteLater()
        QTimer.singleShot(3000, remove)

    def image_popup(self):
        if not self.closing and not self.paused and not self.scaring:
            return self.images.create(screen=random.choice(self.app.screens()))

    def cleanup(self):
        if self.closing:
            return
        self.closing = True
        self.emergency.close()
        self.dialog.status_timer.stop()
        self.timer.stop()
        self.events.clear()
        self.director.clear()
        self.images.clear()
        self.end_scare()
        self.hotkey.close()
        self.app.removeNativeEventFilter(self.hotkey)
        self.desktop.close()
        for window in [*self.pets, *self.popups, self.dialog]:
            window.close()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName('FNAF Desktop')
    app.setStyleSheet('QDialog,QMenu,QScrollArea,QWidget#SettingsPanel {background:#1c1923;color:#eee} QLabel,QCheckBox {color:#eee} QPushButton {padding:7px;background:#4a354b;color:white} QComboBox,QSpinBox,QDoubleSpinBox {background:#332b3b;color:white} QTabBar::tab {background:#302735;color:#eee;padding:7px} QTabBar::tab:selected {background:#604569} QTabWidget::pane {border:1px solid #51465a}')
    try:
        settings_path().parent.mkdir(parents=True, exist_ok=True)
        from PySide6.QtNetwork import QLocalServer, QLocalSocket
        import hashlib
        server_name='FNAFDesktop-'+hashlib.sha256(str(settings_path()).encode()).hexdigest()[:16]
        lock = QLockFile(str(settings_path().parent / 'app.lock'))
        if not lock.tryLock(100):
            if '--settings' in sys.argv:
                socket=QLocalSocket()
                socket.connectToServer(server_name)
                if socket.waitForConnected(1500):
                    socket.write(b'settings');socket.waitForBytesWritten(1000);socket.disconnectFromServer()
                    return 0
            QMessageBox.information(None, 'FNAF Desktop', 'Er draait al een instantie. Gebruik Ctrl+Shift+S of rechtsklik op een personage voor instellingen.')
            return 1
        controller = Controller(app)
        server=QLocalServer(app)
        server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        QLocalServer.removeServer(server_name)
        server.listen(server_name)
        def accept_settings():
            client=server.nextPendingConnection()
            def read_command():
                if bytes(client.readAll()).strip()==b'settings':controller.open_settings()
                client.disconnectFromServer()
            client.readyRead.connect(read_command)
            client.disconnected.connect(client.deleteLater)
            if client.bytesAvailable():read_command()
        server.newConnection.connect(accept_settings)
        if '--settings' in sys.argv:controller.open_settings()
    except Exception as exc:
        QMessageBox.critical(None, 'FNAF Desktop kan niet starten', str(exc))
        return 1
    def exception_hook(kind, value, traceback):
        controller.cleanup()
        sys.__excepthook__(kind, value, traceback)
        app.exit(1)
    sys.excepthook = exception_hook
    # Also useful for headless automated validation, never enabled implicitly.
    if '--smoke' in sys.argv:
        controller.settings.update(silent=True, characters=['Freddy'], count=1, jumpscares=True, mode='normal')
        controller.rebuild()
        def check():
            assert len(controller.pets) == controller.settings['count']
            controller.scare(controller.pets[0])
            assert controller.scaring
            def finished():
                assert not controller.scaring and not controller.scare_windows
                app.quit()
            QTimer.singleShot(2100, finished)
        QTimer.singleShot(100, check)
    return app.exec()
