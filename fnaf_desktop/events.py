"""Bounded, non-blocking visual events. No real monitor or taskbar changes."""
import math
import random
import time
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget
from .media import safe_pixmap


class EffectOverlay(QWidget):
    def __init__(self, manager, kind, screen):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowDoesNotAcceptFocus | Qt.WindowType.WindowTransparentForInput)
        self.manager, self.kind = manager, kind
        self.setGeometry(screen.geometry())
        if kind == 'taskbar':
            g, a = screen.geometry(), screen.availableGeometry()
            if a.bottom() < g.bottom():
                self.setGeometry(g.left(), a.bottom()+1, g.width(), g.bottom()-a.bottom())
            elif a.top() > g.top():
                self.setGeometry(g.left(), g.top(), g.width(), a.top()-g.top())
            elif a.left() > g.left():
                self.setGeometry(g.left(), g.top(), a.left()-g.left(), g.height())
            elif a.right() < g.right():
                self.setGeometry(a.right()+1, g.top(), g.right()-a.right(), g.height())
            else:
                self.setGeometry(g.left(), g.bottom()-44, g.width(), 45)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.face = safe_pixmap(manager.c.assets/'images'/'golden_freddy'/'golden_freddy_flicker.png', 700)
        self.show()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        m = self.manager
        progress = 1-m.remaining/m.duration if m.duration else 1
        fade = min(1, progress*6, (1-progress)*6)
        reduced = m.c.settings['reduced_effects']
        if self.kind == 'blackout':
            p.fillRect(self.rect(), QColor(0, 0, 0, round((95 if reduced else 180)*max(0, fade))))
        elif self.kind in ('static', 'taskbar'):
            p.fillRect(self.rect(), QColor(20, 27, 23, round(28*max(0, fade))))
            p.setPen(QPen(QColor(171, 190, 170, round(35*max(0, fade))), 1))
            # A slowly drifting scan texture, no alternating light/dark flashes.
            offset = int(m.clock*12) % 11
            for y in range(offset, self.height(), 11):
                p.drawLine(0, y, self.width(), y)
        elif self.kind in ('golden', 'encounter'):
            if not self.face.isNull():
                image = self.face.scaled(min(480, self.width()//2), min(480, self.height()//2), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                p.setOpacity(max(0, fade)*(.65 if reduced else .9))
                p.drawPixmap((self.width()-image.width())//2, (self.height()-image.height())//2, image)
            p.setOpacity(1)
        if self.kind in ('text', 'encounter', 'golden'):
            p.setPen(QColor(210, 204, 177, round(210*max(0, fade))))
            p.setFont(QFont('Monospace', 32, QFont.Weight.Bold))
            p.drawText(self.rect().adjusted(0, self.height()//2, 0, 0), Qt.AlignmentFlag.AlignCenter, "IT'S ME")


class EventManager:
    FREEZE = {'encounter', 'stare'}
    KINDS = ('static', 'text', 'laugh', 'sprint', 'blackout', 'taskbar', 'stare', 'theft', 'golden')

    def __init__(self, controller):
        self.c = controller
        self.clock = 0.0
        self.next_event = random.uniform(20, 40)
        self.next_golden = self.golden_delay()
        self.kind = None
        self.windows = []
        self.duration = self.remaining = 0.0

    def golden_delay(self):
        return self.c.settings['golden_minutes']*60*random.uniform(.7, 1.3)

    @property
    def frozen(self):
        return self.kind in self.FREEZE

    def trigger(self, kind):
        if self.kind or self.c.pets_hidden or self.c.closing or self.c.paused or self.c.scaring or not self.c.settings['special_events']:
            return False
        if kind in ('golden','blackout','static','taskbar') and not self.c.settings['flash_effects']:return False
        if kind not in (*self.KINDS, 'encounter'):
            return False
        if kind in ('golden', 'encounter') and (self.c.settings['activity']['Golden Freddy'] == 0 or 'Golden Freddy' not in self.c.settings['characters']):
            return False
        self.kind = kind
        self.duration = self.remaining = {'golden': 1.2, 'encounter': 2.4, 'blackout': 1.0, 'stare': 2.5}.get(kind, 2.0)
        if kind in ('static', 'text', 'blackout', 'taskbar', 'golden', 'encounter'):
            self.windows = [EffectOverlay(self, kind, s) for s in self.c.app.screens()]
        if kind in ('golden', 'encounter'):
            if self.c.settings['window_interactions']:
                pet=next((p for p in self.c.pets if p.name=='Golden Freddy'),None)
                if pet and pet not in self.c.director.jobs:self.c.director.interactions.window_job(pet,'behind')
            if self.c.images.cards:
                self.c.images.glitch(random.choice(self.c.images.cards))
            self.c.audio.play('golden_glitch', self.c.settings)
        elif kind in ('static', 'taskbar'):
            self.c.audio.play('camera_static', self.c.settings)
        elif kind == 'laugh':
            pet = next((p for p in self.c.pets if p.name == 'Freddy'), None)
            if pet:
                self.c.director.cancel(pet)
                pet.state, pet.until, pet.watch_cursor = 'watch', time.monotonic()+1.2, pet.pos()
                pet.direction *= -1
                self.c.audio.play('freddy', self.c.settings)
        elif kind == 'sprint':
            pet = next((p for p in self.c.pets if p.name == 'Foxy'), None)
            if pet:
                self.c.director.cancel(pet)
                pet.state, pet.until = 'run', time.monotonic()+3
                self.c.audio.play('foxy_sprint', self.c.settings)
        elif kind == 'theft':
            pet = next((p for p in self.c.pets if p.name == 'Foxy'), None)
            if pet:
                self.c.director.attempt_theft(pet, direct=True)
        return True

    def tick(self, dt):
        self.clock += dt
        if self.kind:
            self.remaining -= dt
            for window in self.windows:
                window.update()
            if self.remaining <= 0:
                self.clear()
            return
        if not self.c.settings['special_events'] or not self.c.pets:
            return
        if self.clock >= self.next_golden:
            self.next_golden = self.clock+self.golden_delay()
            self.trigger('encounter')
        elif self.clock >= self.next_event:
            self.next_event = self.clock+random.uniform(15, 35)*(2 if self.c.settings['mode'] == 'calm' else 1)
            if random.random() < self.c.settings['event_chance']:
                kind=random.choice(self.KINDS)
                if kind!='golden' or random.random()<min(1,22/self.c.settings['golden_minutes']):self.trigger(kind)

    def clear(self):
        for window in self.windows:
            window.close()
            window.deleteLater()
        self.windows = []
        self.kind = None
        self.remaining = 0.0
