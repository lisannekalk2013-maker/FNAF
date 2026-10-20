import ctypes
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

from PySide6.QtCore import Qt, QTimer, QPoint, QAbstractNativeEventFilter, QLockFile
from PySide6.QtGui import QColor, QPainter, QPen, QCursor, QPixmap, QIcon, QAction
from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QVBoxLayout, QLabel,
    QCheckBox, QSlider, QSpinBox, QComboBox, QPushButton, QSystemTrayIcon, QMenu, QMessageBox, QScrollArea)
from .core import NAMES, load, save, settings_path
from .audio import Audio

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
        self.setFixedSize(110, 150)
        self.frame = 0
        self.direction = random.choice((-1, 1))
        self.state = 'walk'
        self.watch_cursor = QCursor.pos()
        self.until = 0
        self.deadline = time.monotonic() + random.uniform(3, 10)
        self.frames = [QPixmap(str(p)) for p in sorted((ASSETS / name.lower().replace(' ', '_')).glob('walk_*.png'))]
        self.frames = [p for p in self.frames if not p.isNull()]
        r = screen.availableGeometry()
        self.posx = float(random.randint(r.left(), max(r.left(), r.right()-110)))
        self.posy = float(random.randint(r.top(), max(r.top(), r.bottom()-150)))
        self.move(int(self.posx), int(self.posy))
        silhouette = QPixmap(self.size())
        silhouette.fill(Qt.GlobalColor.transparent)
        painter = QPainter(silhouette)
        if self.frames:
            painter.drawPixmap(self.rect(), self.frames[0])
        else:
            draw_character(painter, name)
        painter.end()
        self.setMask(silhouette.mask())
        self.show()

    def paintEvent(self, event):
        p = QPainter(self)
        if self.frames:
            p.drawPixmap(self.rect(), self.frames[(self.frame//4) % len(self.frames)])
        else:
            draw_character(p, self.name, self.frame if self.state not in ('watch', 'hide') else 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.c.menu.popup(QCursor.pos())
        elif event.button() == Qt.MouseButton.LeftButton:
            self.c.scare(self)

    def tick(self, dt, now):
        if self.c.scaring:
            return
        self.frame += 1
        r = self.screen.availableGeometry()
        cursor = QCursor.pos()
        if self.state == 'hide':
            if now >= self.until:
                self.state = 'walk'
                self.posx = float(random.choice((r.left(), max(r.left(), r.right()-110))))
                self.show()
            return
        if now >= self.deadline:
            self.deadline = now + random.uniform(3, 10)
            chance = self.c.settings['event_chance'] * {'calm': .25, 'normal': 1, 'chaos': 2}[self.c.settings['mode']]
            if random.random() < chance:
                self.random_event(now)
            else:
                self.direction *= -1
                self.state = random.choice(('walk', 'follow', 'watch'))
                self.until = now + random.uniform(1, 3)
        if self.state == 'watch':
            if now < self.until or (self.name == 'Bonnie' and (cursor-self.watch_cursor).manhattanLength() < 20):
                self.update()
                return
            self.state = 'walk'
        if self.state == 'run' and now > self.until:
            self.state = 'walk'
        speed = {'Freddy': 45, 'Bonnie': 60, 'Chica': 50, 'Foxy': 110, 'Golden Freddy': 35, 'Springtrap': 27}[self.name]
        speed *= self.c.settings['speed'] * (2.5 if self.state == 'run' else 1)
        if self.c.settings['mode'] == 'calm':
            speed *= .6
        if self.state == 'follow':
            self.direction = 1 if cursor.x() > self.posx+55 else -1
            if abs(cursor.x()-self.posx-55) < 35:
                self.state = 'watch'
                self.until = now + 2
                self.watch_cursor = cursor
            self.posy += max(-speed*dt, min(speed*dt, cursor.y()-self.posy-75))
        self.posx += self.direction * speed * dt
        if self.posx < r.left() or self.posx > r.right()-110:
            self.direction *= -1
        self.posx = max(r.left(), min(max(r.left(), r.right()-110), self.posx))
        self.posy = max(r.top(), min(max(r.top(), r.bottom()-150), self.posy))
        self.move(round(self.posx), round(self.posy))
        self.update()

    def random_event(self, now):
        if self.name in ('Golden Freddy', 'Springtrap') or random.random() < .15:
            self.state = 'hide'
            self.until = now + random.uniform(2, 7)
            self.posx = float(self.screen.availableGeometry().left())
            self.move(round(self.posx), round(self.posy))
            self.hide()
        elif self.name == 'Foxy':
            self.state, self.until = 'run', now+2
        elif self.name == 'Bonnie':
            self.state, self.until, self.watch_cursor = 'watch', now+1, QCursor.pos()
        elif self.name == 'Chica':
            self.c.popup('🧁  Chica heeft een cupcake achtergelaten!', self.pos())
        elif self.name == 'Freddy':
            self.c.audio.play('freddy', self.c.settings)
        else:
            self.c.popup('IT’S ME — de nachtdienst roept…', self.pos())


class Scare(QWidget):
    def __init__(self, c, name, screen):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.c, self.name, self.started = c, name, time.monotonic()
        self.setGeometry(screen.geometry())
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.image = QPixmap(str(ASSETS / name.lower().replace(' ', '_') / 'scare.png'))
        self.show()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor('#080609'))
        elapsed = time.monotonic()-self.started
        if elapsed < .2:
            return
        # Zoom and sway; no strobe or flashing background.
        size = min(self.height()*.85, 600) * (1 + .09*math.sin(elapsed*15))
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

    def nativeEventFilter(self, kind, message):
        if sys.platform == 'win32':
            from ctypes.wintypes import MSG
            msg = MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == 18021:
                self.c.app.quit()
                return True, 0
        return False, 0

    def close(self):
        if self.registered:
            ctypes.windll.user32.UnregisterHotKey(None, 18021)


def startup(enabled):
    if sys.platform != 'win32':
        if enabled:
            raise RuntimeError('Opstarten met Windows werkt uitsluitend op Windows.')
        return
    import winreg
    command = subprocess.list2cmdline([sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, str(ROOT / 'run.py')])
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
        if enabled:
            winreg.SetValueEx(key, 'FNAFDesktop', 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, 'FNAFDesktop')
            except FileNotFoundError:
                pass


class Settings(QDialog):
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.setWindowTitle('FNAF Desktop — instellingen')
        self.setMinimumWidth(400)
        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        panel = QWidget()
        panel.setObjectName('SettingsPanel')
        layout = QVBoxLayout(panel)
        scroll.setWidget(panel)
        outer.addWidget(scroll)
        self.resize(460, min(740, c.app.primaryScreen().availableGeometry().height()-60))
        layout.addWidget(QLabel('Alleen gebruiken met toestemming van de eigenaar.\nStop altijd met Ctrl+Shift+Q of de knop Afsluiten.'))
        self.characters = {}
        for name in NAMES:
            box = QCheckBox(name)
            box.setChecked(name in c.settings['characters'])
            layout.addWidget(box)
            self.characters[name] = box
        self.count = QSpinBox()
        self.count.setRange(1, 12)
        self.count.setValue(c.settings['count'])
        layout.addWidget(QLabel('Aantal animatronics'))
        layout.addWidget(self.count)
        self.sliders = {}
        for key, label, lo, hi in [('speed', 'Bewegingssnelheid', 20, 300), ('event_chance', 'Kans op gebeurtenissen (%)', 0, 100), ('volume', 'Maximaal audiovolume (0–50%, standaard 15%)', 0, 50)]:
            layout.addWidget(QLabel(label))
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(lo, hi)
            slider.setValue(round(c.settings[key]*100))
            layout.addWidget(slider)
            value_label = QLabel(str(slider.value()) + '%')
            slider.valueChanged.connect(lambda value, label=value_label: label.setText(str(value) + '%'))
            layout.addWidget(value_label)
            self.sliders[key] = slider
        self.checks = {}
        for key, label in [('jumpscares', 'Jumpscares bij klikken'), ('silent', 'Volledig stil'), ('system_volume', 'Systeemvolume tijdelijk begrenzen (Windows)'), ('startup', 'Opstarten met Windows (alleen na bevestiging)')]:
            box = QCheckBox(label)
            box.setChecked(c.settings[key])
            if sys.platform != 'win32' and key in ('startup', 'system_volume'):
                box.setEnabled(False)
            self.checks[key] = box
            layout.addWidget(box)
        self.audio_status = QLabel()
        self.audio_status.setWordWrap(True)
        layout.addWidget(self.audio_status)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(lambda: self.audio_status.setText(c.audio.error))
        self.status_timer.start(1000)
        self.mode = QComboBox()
        self.mode.addItems(['normal', 'calm', 'chaos'])
        self.mode.setCurrentText(c.settings['mode'])
        layout.addWidget(QLabel('Modus: normal / calm (rustig) / chaos'))
        layout.addWidget(self.mode)
        for label, callback in [('Volume testen', self.test), ('Instellingen toepassen', self.apply)]:
            b = QPushButton(label)
            b.clicked.connect(callback)
            layout.addWidget(b)
        quit_button = QPushButton('Afsluiten (Ctrl+Shift+Q)')
        quit_button.clicked.connect(c.app.quit)
        outer.addWidget(quit_button)

    def values(self):
        return dict(characters=[n for n, b in self.characters.items() if b.isChecked()], count=self.count.value(),
                    mode=self.mode.currentText(), **{k: s.value()/100 for k, s in self.sliders.items()},
                    **{k: b.isChecked() for k, b in self.checks.items()})

    def test(self):
        self.c.audio.play('scare', self.values(), True)
        QTimer.singleShot(1500, self.c.audio.stop)

    def apply(self):
        values = self.values()
        try:
            if values['startup'] != self.c.settings['startup']:
                if values['startup'] and QMessageBox.question(self, 'Windows opstarten', 'Mag FNAF Desktop zichtbaar starten wanneer je inlogt?') != QMessageBox.StandardButton.Yes:
                    self.checks['startup'].setChecked(False)
                    values['startup'] = False
                startup(values['startup'])
            save(settings_path(), values)
            self.c.settings = values
            self.c.audio.stop()
            self.c.rebuild()
        except Exception as exc:
            QMessageBox.warning(self, 'Instellingen niet opgeslagen', str(exc))


class Controller:
    def __init__(self, app):
        self.app = app
        self.settings = load(settings_path())
        self.pets, self.scare_windows, self.popups = [], [], []
        self.scaring = False
        self.audio = Audio(app, settings_path().parent / 'audio', ASSETS)
        self.menu = QMenu()
        self.menu.addAction('Instellingen', self.open_settings)
        self.menu.addAction('Alles pauzeren / hervatten', self.pause)
        self.menu.addAction('Afsluiten (Ctrl+Shift+Q)', app.quit)
        icon = QPixmap(110, 150)
        icon.fill(Qt.GlobalColor.transparent)
        p = QPainter(icon)
        draw_character(p, 'Freddy')
        p.end()
        self.tray = QSystemTrayIcon(QIcon(icon), app)
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip('FNAF Desktop — Ctrl+Shift+Q om af te sluiten')
        self.tray.show()
        self.dialog = Settings(self)
        self.dialog.finished.connect(lambda _: QTimer.singleShot(0, self.dialog.show) if not QSystemTrayIcon.isSystemTrayAvailable() else None)
        self.hotkey = Hotkey(self)
        app.installNativeEventFilter(self.hotkey)
        self.paused = False
        self.last = time.monotonic()
        self.timer = QTimer(app)
        self.timer.timeout.connect(self.tick)
        self.timer.start(33)
        self.scare_timer = QTimer(app)
        self.scare_timer.setSingleShot(True)
        self.scare_timer.timeout.connect(self.end_scare)
        app.aboutToQuit.connect(self.cleanup)
        app.screenRemoved.connect(lambda _: self.rebuild())
        app.screenAdded.connect(lambda _: self.rebuild())
        self.rebuild()
        self.open_settings()
        if sys.platform == 'win32' and not self.hotkey.registered:
            self.settings['jumpscares'] = False
            self.dialog.checks['jumpscares'].setChecked(False)
            QMessageBox.warning(self.dialog, 'Sneltoets niet beschikbaar', 'Ctrl+Shift+Q kon niet worden geregistreerd. Jumpscares zijn uitgeschakeld. Sluit af via instellingen of systeemvak.')

    def open_settings(self):
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def rebuild(self):
        self.end_scare()
        for pet in self.pets:
            pet.close()
            pet.deleteLater()
        self.pets = []
        names = self.settings['characters']
        screens = self.app.screens()
        if names and screens:
            for i in range(self.settings['count']):
                self.pets.append(Pet(self, names[i % len(names)], screens[i % len(screens)]))

    def pause(self):
        self.paused = not self.paused
        if self.paused:
            self.end_scare()
        for pet in self.pets:
            pet.setVisible(not self.paused and pet.state != 'hide')

    def tick(self):
        now = time.monotonic()
        dt, self.last = min(.1, now-self.last), now
        if not self.paused:
            for pet in self.pets:
                pet.tick(dt, now)
        for window in self.scare_windows:
            window.update()

    def scare(self, pet):
        if self.scaring or self.paused or not self.settings['jumpscares'] or self.settings['mode'] == 'calm':
            return
        if sys.platform == 'win32' and not self.hotkey.registered:
            return
        self.scaring = True
        self.scare_windows = [Scare(self, pet.name, screen) for screen in self.app.screens()]
        active_windows = self.scare_windows
        QTimer.singleShot(200, lambda: self.audio.play(pet.name.lower().replace(' ', '_')+'_scare', self.settings, True) if self.scaring and self.scare_windows is active_windows else None)
        self.scare_timer.start(1700)

    def end_scare(self):
        if hasattr(self, 'scare_timer'):
            self.scare_timer.stop()
        self.scaring = False
        self.audio.stop()
        for window in self.scare_windows:
            window.close()
            window.deleteLater()
        self.scare_windows = []

    def popup(self, text, pos):
        if len(self.popups) >= 3:
            return
        label = QLabel(text, None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
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

    def cleanup(self):
        self.timer.stop()
        self.end_scare()
        self.hotkey.close()
        self.app.removeNativeEventFilter(self.hotkey)
        self.tray.hide()
        for window in [*self.pets, *self.popups, self.dialog]:
            window.close()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName('FNAF Desktop')
    app.setStyleSheet('QDialog,QMenu,QScrollArea,QWidget#SettingsPanel {background:#1c1923;color:#eee} QLabel,QCheckBox {color:#eee} QPushButton {padding:7px;background:#4a354b;color:white} QComboBox,QSpinBox {background:#332b3b;color:white}')
    try:
        settings_path().parent.mkdir(parents=True, exist_ok=True)
        lock = QLockFile(str(settings_path().parent / 'app.lock'))
        if not lock.tryLock(100):
            QMessageBox.information(None, 'FNAF Desktop', 'Er draait al een instantie, of de instellingenmap is niet beschrijfbaar. Controleer het systeemvak.')
            return 1
        controller = Controller(app)
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
