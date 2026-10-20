"""Temporary image windows and atomic ownership; never touch desktop files."""
import math
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QDialog, QPushButton
from .media import safe_pixmap


class ImageCard(QDialog):
    def __init__(self, manager, path, screen, origin=None, position=None):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.manager, self.path, self.screen = manager, path, screen
        self.origin, self.owner, self.last_owner = origin, None, None
        self.pixmap = safe_pixmap(path, 900)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        area = screen.availableGeometry()
        width = min(random.choice((180, 230, 290)), max(80, area.width()-40))
        height = min(round(width*.74), max(80, area.height()-40))
        self.setFixedSize(width, height)
        self.pixmap = self.pixmap.scaled(width-32, height-40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.xf, self.yf = position or (random.uniform(area.left(), max(area.left(), area.right()-width)), random.uniform(area.top(), max(area.top(), area.bottom()-height)))
        self.angle = 0.0
        self.life = manager.c.settings['image_lifetime']
        self.hidden_for = 0.0
        self.pending_position = None
        self.tug = 0.0
        button = QPushButton('×', self)
        button.setGeometry(width-31, 4, 26, 24)
        button.setStyleSheet('background:#33262e;color:white;border:1px solid #ad8d74')
        button.clicked.connect(self.close)
        self.move(round(self.xf), round(self.yf))
        self.show()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.translate(self.width()/2, self.height()/2)
        p.rotate(self.angle)
        w, h = self.width()-22, self.height()-30
        p.setPen(QPen(QColor('#b9a17b'), 2))
        p.setBrush(QColor('#17171e'))
        p.drawRoundedRect(-w//2, -h//2, w, h, 5, 5)
        if not self.pixmap.isNull():
            image = self.pixmap
            p.drawPixmap(-image.width()//2, -image.height()//2, image)

    def closeEvent(self, event):
        self.manager.remove(self)
        super().closeEvent(event)
        self.deleteLater()


class ImageManager:
    def __init__(self, controller):
        self.c = controller
        self.cards = []
        self.clock = 0.0

    def create(self, path=None, screen=None, origin=None, position=None):
        if len(self.cards) >= self.c.settings['max_images']:
            return None
        choices = self.c.image_paths
        if path is None and not choices:
            return None
        path = path or random.choice(choices)
        if safe_pixmap(path, 32).isNull():
            return None
        card = ImageCard(self, path, screen or self.c.app.primaryScreen(), origin, position)
        self.cards.append(card)
        self.c.popups.append(card)
        return card

    def remove(self, card):
        card.owner = None
        if card in self.cards:
            self.cards.remove(card)
        if card in self.c.popups:
            self.c.popups.remove(card)

    def claim(self, card, pet, steal=False):
        if card not in self.cards or card.hidden_for > 0:
            return False
        if card.owner is not None and card.owner is not pet and not steal:
            return False
        if any(other.owner is pet and other is not card for other in self.cards):
            return False
        card.last_owner, card.owner = card.owner or card.last_owner, pet
        card.life = self.c.settings['image_lifetime']
        card.screen = pet.screen
        return True

    def drop(self, card):
        if card in self.cards:
            card.last_owner, card.owner = card.owner or card.last_owner, None
            card.life = self.c.settings['image_lifetime']

    def release_pet(self, pet):
        for card in self.cards:
            if card.owner is pet:
                self.drop(card)

    def glitch(self, card):
        if card not in self.cards or card.hidden_for:
            return False
        self.drop(card)
        area = card.screen.availableGeometry()
        card.pending_position = (random.uniform(area.left(), max(area.left(), area.right()-card.width())), random.uniform(area.top(), max(area.top(), area.bottom()-card.height())))
        card.hidden_for = .65
        card.hide()
        return True

    def tick(self, dt):
        self.clock += dt
        for card in list(self.cards):
            if card.hidden_for:
                card.hidden_for = max(0.0, card.hidden_for-dt)
                if not card.hidden_for:
                    card.xf, card.yf = card.pending_position
                    card.move(round(card.xf), round(card.yf))
                    card.show()
                continue
            was_angle = card.angle
            animated = card.owner is not None or card.tug > 0
            if card.owner is not None:
                pet = card.owner
                if pet not in self.c.pets:
                    self.drop(card)
                    continue
                side = 1 if pet.direction > 0 else -1
                tx = pet.posx + (75 if side > 0 else -card.width()+35)
                ty = pet.posy + 70
                alpha = 1-math.exp(-dt*9)
                card.xf += (tx-card.xf)*alpha
                card.yf += (ty-card.yf)*alpha
                card.angle = math.sin(self.clock*7)*2.2*side
            else:
                card.life -= dt
                card.angle *= max(0, 1-dt*6)
                if card.life <= 0:
                    card.close()
                    continue
            if card.tug > 0:
                card.tug = max(0, card.tug-dt)
                card.angle += math.sin(self.clock*20)*3
            area = card.screen.availableGeometry()
            card.xf = max(area.left(), min(max(area.left(), area.right()-card.width()), card.xf))
            card.yf = max(area.top(), min(max(area.top(), area.bottom()-card.height()), card.yf))
            card.move(round(card.xf), round(card.yf))
            if animated or abs(was_angle-card.angle) > .001:
                card.update()

    def visibility(self, visible):
        for card in self.cards:
            card.setVisible(visible and not card.hidden_for)

    def clear(self):
        for card in list(self.cards):
            card.close()
