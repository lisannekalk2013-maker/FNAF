import json
import os
import math
from pathlib import Path

NAMES = ('Freddy', 'Bonnie', 'Chica', 'Foxy', 'Golden Freddy', 'Springtrap')
DEFAULT = dict(characters=list(NAMES), count=6, speed=1.0, event_chance=.3,
    jumpscares=True, volume=.15, ambient_volume=.08, silent=False, mode='normal',
    startup=False, system_volume=False, image_popups=True, activity={name: 10 for name in NAMES},
    image_chance=.35, drag_chance=.45, theft_chance=.35, chase_chance=.4,
    golden_minutes=22, special_events=True, reduced_effects=True, fullscreen=True,
    max_images=5, image_lifetime=45, fps=30, jumpscare_cooldown=8, animationspeed=1.0)


def normalize(raw):
    if not isinstance(raw, dict):
        raw = {}
    s = {**DEFAULT, **{k: v for k, v in raw.items() if k in DEFAULT}}
    s['characters'] = [n for n in s['characters'] if n in NAMES] if isinstance(s['characters'], list) else list(NAMES)
    limits = dict(count=(1, 12), speed=(.2, 3), event_chance=(0, 1), volume=(0, .5), ambient_volume=(0, .5),
        image_chance=(0, 1), drag_chance=(0, 1), theft_chance=(0, 1), chase_chance=(0, 1),
        golden_minutes=(15, 60), max_images=(1, 12), image_lifetime=(10, 300), fps=(15, 60),
        jumpscare_cooldown=(2, 60), animationspeed=(.25, 3))
    for key, (low, high) in limits.items():
        try:
            value = float(s[key])
            if not math.isfinite(value):
                raise ValueError()
            s[key] = max(low, min(high, value))
        except (ValueError, TypeError, OverflowError):
            s[key] = DEFAULT[key]
    for key in ('count', 'fps', 'max_images'):
        s[key] = int(s[key])
    for key, default in DEFAULT.items():
        if isinstance(default, bool):
            s[key] = s[key] if type(s[key]) is bool else default
    if s['mode'] not in ('normal', 'calm', 'chaos'):
        s['mode'] = 'normal'
    levels = s['activity'] if isinstance(s['activity'], dict) else {}
    def activity(name):
        try:
            return max(0, min(20, int(levels.get(name, 10))))
        except (TypeError, ValueError, OverflowError):
            return 10
    s['activity'] = {n: activity(n) for n in NAMES}
    return s


def settings_path():
    return Path(os.getenv('LOCALAPPDATA', str(Path.home() / '.config'))) / 'FNAFDesktop' / 'config.json'


def load(path):
    try:
        source = path
        if not path.exists() and path.name == 'config.json':
            source = path.with_name('settings.json')
        return normalize(json.loads(source.read_text(encoding='utf8')))
    except (OSError, ValueError, TypeError, AttributeError):
        return normalize({})

def save(path, settings):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(normalize(settings), indent=2), encoding='utf8')
    temp.replace(path)

class VolumeGuard:
    """Only lower endpoint volume; restore it even after playback failure."""
    def __init__(self, endpoint=None):
        self.endpoint = endpoint
        self.original = None

    def begin(self, maximum):
        self.restore()
        if self.endpoint is not None:
            self.original = self.endpoint.GetMasterVolumeLevelScalar()
            self.endpoint.SetMasterVolumeLevelScalar(min(self.original, max(0, min(.5, maximum))), None)

    def restore(self):
        if self.original is not None:
            self.endpoint.SetMasterVolumeLevelScalar(self.original, None)
            self.original = None


class HoldToQuit:
    """Track a continuous hold without counting key-repeat events."""
    def __init__(self, seconds=5.0):
        self.seconds = seconds
        self.started = None

    def update(self, pressed, now):
        if not pressed:
            self.started = None
            return False
        if self.started is None:
            self.started = now
        return now - self.started >= self.seconds
