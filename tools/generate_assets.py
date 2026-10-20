"""Build animation PNGs and CCTV cards from the generated transparent atlas.

Run from the project root. Existing default assets are overwritten.
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtGui import QPainter, QPixmap, QRegion, QColor, QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from fnaf_desktop.app import draw_character, ASSETS
from fnaf_desktop.core import NAMES

app = QApplication.instance() or QApplication([])
atlas = QPixmap(str(ASSETS / 'character_atlas.png'))
if atlas.isNull():
    raise SystemExit('Missing character_atlas.png; keep the generated source artwork.')
(ASSETS/'popups').mkdir(exist_ok=True)
for index, name in enumerate(NAMES):
    folder = ASSETS / name.lower().replace(' ', '_')
    folder.mkdir(parents=True, exist_ok=True)
    w, h = atlas.width()//3, atlas.height()//2
    source = atlas.copy((index%3)*w, (index//3)*h, w, h)
    bounds = QRegion(source.mask()).boundingRect()
    if bounds.isEmpty():
        raise SystemExit('Empty alpha mask for '+name)
    source = source.copy(bounds)
    sprite = source.scaled(96, 132, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    for frame in range(8):
        image = QPixmap(110, 150)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        phase = frame*math.tau/8
        painter.translate(55, 142-abs(math.sin(phase))*3)
        painter.rotate(math.sin(phase)*1.8)
        painter.drawPixmap(-sprite.width()//2, -sprite.height(), sprite)
        painter.end()
        assert image.save(str(folder / f'walk_{frame:02}.png'))
    face = source.copy(0, 0, source.width(), max(1, round(source.height()*.52)))
    assert face.save(str(folder / 'scare.png'))
    card = QPixmap(600, 420)
    card.fill(QColor('#11161a'))
    painter = QPainter(card)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    poster = source.scaled(420, 345, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    painter.drawPixmap((600-poster.width())//2, 42, poster)
    painter.setPen(QColor('#c9d6c0'))
    painter.setFont(QFont('Sans', 15, QFont.Weight.Bold))
    painter.drawText(20, 29, f'CAM {index+1:02}   /   {name.upper()}')
    painter.setPen(QColor('#a79a7b'))
    painter.setFont(QFont('Sans', 11))
    painter.drawText(20, 405, ['NIGHT SHIFT', 'DID YOU HEAR THAT?', 'LET’S EAT!', 'PIRATE COVE', 'IT’S ME', 'STILL HERE'][index])
    painter.setPen(QColor(160, 185, 170, 25))
    for y in range(0, 420, 5):
        painter.drawLine(0, y, 600, y)
    painter.setPen(QColor('#637064'))
    painter.drawRect(7, 7, 585, 405)
    painter.end()
    assert card.save(str(ASSETS/'popups'/(name.lower().replace(' ', '_')+'.png')))
print('Generated 54 detailed animation/face PNGs and 6 CCTV image cards.')
