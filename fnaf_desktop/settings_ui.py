"""Custom Night controls. All displayed values round-trip through config.json."""
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QWidget, QTabWidget,
    QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QMessageBox, QScrollArea)
from .core import NAMES, save, settings_path, normalize
from .media import image_files


class Settings(QDialog):
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.setWindowTitle('FNAF Desktop V3.0 — Custom Night')
        self.resize(540, min(760, c.app.primaryScreen().availableGeometry().height()-60))
        outer = QVBoxLayout(self)
        helptext = QLabel('ESC: effect/jumpscare stoppen · ESC 5 seconden: volledig afsluiten\nNoodstop: Ctrl+Shift+Q · Alleen gebruiken met toestemming.')
        helptext.setWordWrap(True)
        outer.addWidget(helptext)
        tabs = QTabWidget()
        outer.addWidget(tabs)
        forms = {}
        for name in ('Custom Night', 'Afbeeldingen', 'Effecten', 'Geluid & systeem'):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            panel = QWidget()
            panel.setObjectName('SettingsPanel')
            forms[name] = QFormLayout(panel)
            scroll.setWidget(panel)
            tabs.addTab(scroll, name)
        self.characters, self.activity, self.checks, self.controls = {}, {}, {}, {}
        for name in NAMES:
            checkbox = QCheckBox(name)
            checkbox.setChecked(name in c.settings['characters'])
            level = QSpinBox()
            level.setRange(0, 20)
            level.setValue(c.settings['activity'][name])
            forms['Custom Night'].addRow(checkbox, level)
            self.characters[name], self.activity[name] = checkbox, level
        self.count = self.add_number(forms['Custom Night'], 'count', 'Aantal personages', 1, 12, integer=True)
        self.mode = QComboBox()
        self.mode.addItems(['normal', 'calm', 'chaos'])
        self.mode.setCurrentText(c.settings['mode'])
        forms['Custom Night'].addRow('Modus', self.mode)
        for key, text, low, high, integer in [
            ('speed', 'Bewegingssnelheid', .2, 3, False),
            ('animationspeed', 'Animatiesnelheid', .25, 3, False),
            ('sprite_scale', 'Personagegrootte', .7, 1.8, False),
            ('fps', 'FPS-limiet', 15, 60, True)]:
            self.add_number(forms['Custom Night'], key, text, low, high, integer)
        for key, text, low, high, integer in [
            ('image_chance', 'Kans op losse afbeeldingen (0–1)', 0, 1, False),
            ('drag_chance', 'Frequentie meeslepen (0–1)', 0, 1, False),
            ('theft_chance', 'Kans op stelen (0–1)', 0, 1, False),
            ('chase_chance', 'Kans op achtervolgen (0–1)', 0, 1, False),
            ('max_images', 'Maximaal aantal afbeeldingen', 1, 12, True),
            ('image_lifetime', 'Levensduur na neerleggen (seconden)', 10, 300, True)]:
            self.add_number(forms['Afbeeldingen'], key, text, low, high, integer)
        for key, text, low, high, integer in [
            ('event_chance', 'Kans speciale gebeurtenissen (0–1)', 0, 1, False),
            ('auto_scare_chance', 'Automatische jumpscarekans per 20–40 s', 0, .3, False),
            ('golden_minutes', 'Golden-ontmoeting gemiddeld (minuten)', 15, 60, True),
            ('jumpscare_cooldown', 'Cooldown jumpscares (seconden)', 2, 60, True)]:
            self.add_number(forms['Effecten'], key, text, low, high, integer)
        for group, key, text in [
            ('Afbeeldingen', 'image_popups', 'Willekeurige losse afbeeldingen'),
            ('Effecten', 'special_events', 'Speciale gebeurtenissen'),
            ('Effecten', 'reduced_effects', 'Verminderde lichteffecten'),
            ('Effecten', 'jumpscares', 'Jumpscares bij klikken'),
            ('Effecten', 'fullscreen', 'Fullscreen jumpscares (uit = kleiner venster)'),
            ('Geluid & systeem', 'silent', 'Volledig stil'),
            ('Custom Night', 'window_interactions', 'Interactie met Windows-vensters'),
            ('Custom Night', 'cursor_interactions', 'Cursorinteracties'),
            ('Custom Night', 'group_activities', 'Samenwerken / groepsactiviteiten'),
            ('Custom Night', 'performance_mode', 'Prestatiemodus (maximaal 30 FPS)'),
            ('Afbeeldingen', 'desktop_theft', 'Visuele kopieën van bureaubladafbeeldingen'),
            ('Effecten', 'auto_jumpscares', 'Automatische jumpscares (standaard uit)'),
            ('Effecten', 'flash_effects', 'Korte flits-, ruis- en verduisteringseffecten')]:
            box = QCheckBox(text)
            box.setChecked(c.settings[key])
            forms[group].addRow(box)
            self.checks[key] = box
        for key, label in [('volume', 'Jumpscarevolume (0–0,50)'), ('ambient_volume', 'Overig geluid (0–0,50)')]:
            self.add_number(forms['Geluid & systeem'], key, label, 0, .5)
        self.sound_choice = QComboBox()
        self.sound_choice.addItems(NAMES)
        forms['Geluid & systeem'].addRow('Personage voor geluidstest', self.sound_choice)
        test = QPushButton('Volume testen')
        test.clicked.connect(self.test)
        forms['Geluid & systeem'].addRow(test)
        self.audio_status = QLabel()
        self.audio_status.setWordWrap(True)
        outer.addWidget(self.audio_status)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(lambda: self.audio_status.setText(c.audio.error))
        self.status_timer.start(1000)
        for text, callback in [('Toepassen en opslaan', self.apply), ('Afsluiten', c.quit)]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            outer.addWidget(button)

    def add_number(self, form, key, text, low, high, integer=False):
        control = QSpinBox() if integer else QDoubleSpinBox()
        control.setRange(low, high)
        if not integer:
            control.setSingleStep(.05)
            control.setDecimals(2)
        control.setValue(int(self.c.settings[key]) if integer else self.c.settings[key])
        form.addRow(text, control)
        self.controls[key] = control
        return control

    def values(self):
        return normalize(dict(self.c.settings, characters=[n for n, box in self.characters.items() if box.isChecked()],
            activity={n: box.value() for n, box in self.activity.items()}, mode=self.mode.currentText(),
            **{k: box.isChecked() for k, box in self.checks.items()}, **{k: box.value() for k, box in self.controls.items()}))

    def test(self):
        self.c.interrupt_effects()
        self.c.audio.play(self.sound_choice.currentText().lower().replace(' ', '_')+'_scare', self.values(), True)
        QTimer.singleShot(1500, self.c.audio.stop)

    def apply(self):
        values = self.values()
        try:
            save(settings_path(), values)
            self.c.settings = values
            self.c.audio.stop()
            self.c.rebuild()
            self.c.timer.setInterval(round(1000/(min(30,values['fps']) if values['performance_mode'] else values['fps'])))
            self.c.image_paths = image_files(self.c.assets)
            self.c.events.next_golden = self.c.events.clock+self.c.events.golden_delay()
        except Exception as exc:
            QMessageBox.warning(self, 'Instellingen niet opgeslagen', str(exc))
