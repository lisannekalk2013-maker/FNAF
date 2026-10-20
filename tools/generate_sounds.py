"""Original character-inspired sounds, not recordings from the FNAF games."""
import math
from pathlib import Path
import random
import struct
import wave

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
PROFILES = {
    'freddy': (78, 1.8, .12, 5.5),
    'bonnie': (125, 3.1, .17, 9),
    'chica': (215, 2.6, .22, 13),
    'foxy': (105, 4.8, .30, 20),
    'golden_freddy': (56, 1.3, .14, 7),
    'springtrap': (68, 3.7, .35, 11),
}

def generate(path, profile, seed, laugh=False):
    rate = 22050
    duration = 1.3 if not laugh else .7
    rng = random.Random(seed)
    base, ratio, noise, modulation = profile
    samples = []
    filtered = 0.0
    for i in range(int(rate*duration)):
        t = i/rate
        filtered = .78*filtered + .22*rng.uniform(-1, 1)
        phase = 2*math.pi*(base*t + 20*t*t)
        growl = math.sin(phase + .8*math.sin(2*math.pi*modulation*t))
        metal = math.sin(phase*ratio)*.27 + math.sin(phase*5.13)*.10
        envelope = min(1, t/.06)*min(1, (duration-t)/.15)
        pulse = .6+.4*math.sin(2*math.pi*(6 if laugh else modulation)*t)**2
        if laugh:
            pulse *= max(0, math.sin(2*math.pi*5*t))
        samples.append((growl*.45+metal+filtered*noise)*envelope*pulse)
    peak = max(abs(s) for s in samples) or 1
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        out.writeframes(b''.join(struct.pack('<h', round(s/peak*14000)) for s in samples))

if __name__ == '__main__':
    for index, (name, profile) in enumerate(PROFILES.items()):
        generate(ASSETS/(name+'_scare.wav'), profile, index)
    generate(ASSETS/'freddy.wav', PROFILES['freddy'], 10, laugh=True)
    for index, name in enumerate(['foxy_sprint', 'camera_static', 'golden_glitch', 'theft', 'ambient', 'chica']):
        generate(ASSETS/(name+'.wav'), (90+index*27, 2.1+index*.3, .25, 8+index*2), 30+index)
    print('Generated character sounds and six separate event/ambient effects.')
