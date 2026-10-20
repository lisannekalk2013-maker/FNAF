"""Generate original transparent placeholder PNGs; no downloaded game assets."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from fnaf_desktop.app import draw_character, ASSETS
from fnaf_desktop.core import NAMES

app = QApplication.instance() or QApplication([])
for name in NAMES:
    folder = ASSETS / name.lower().replace(' ', '_')
    folder.mkdir(parents=True, exist_ok=True)
    for frame in range(8):
        image = QPixmap(110, 150)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        draw_character(painter, name, frame)
        painter.end()
        image.save(str(folder / f'walk_{frame:02}.png'))
    image = QPixmap(110, 150)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    draw_character(painter, name, 0, True)
    painter.end()
    image.save(str(folder / 'scare.png'))
print('Generated 54 original PNG sprites.')
