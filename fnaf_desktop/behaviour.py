"""Time-based movement tasks for fetching, investigating, stealing and chasing."""
from dataclasses import dataclass
import math
import random
from PySide6.QtGui import QCursor


@dataclass
class Job:
    phase: str
    target: tuple = (0, 0)
    card: object = None
    until: float = 0
    timeout: float = 0
    victim: object = None


class BehaviourDirector:
    def __init__(self, controller):
        self.c = controller
        self.jobs = {}
        self.clock = 0.0
        self.next_decision = 2.0

    def destination(self, pet):
        r = pet.screen.availableGeometry()
        return (random.uniform(r.left()+20, max(r.left()+20, r.right()-130)), random.uniform(r.top()+20, max(r.top()+20, r.bottom()-170)))

    def start_fetch(self, pet):
        if pet in self.jobs or pet.name == 'Golden Freddy' or len(self.c.images.cards) >= self.c.settings['max_images']:
            return False
        r = pet.screen.availableGeometry()
        edge = random.choice((r.left()-30, r.right()-80))
        self.jobs[pet] = Job('edge', (edge, random.uniform(r.top(), max(r.top(), r.bottom()-150))), timeout=self.clock+100)
        return True

    def attempt_theft(self, pet, card=None, direct=False):
        if pet in self.jobs or pet.name == 'Golden Freddy':
            return False
        choices = [c for c in self.c.images.cards if c.screen is pet.screen and not c.hidden_for and (c.owner is None or direct and c.owner is not pet)]
        if card is None and choices:
            if pet.name == 'Chica':
                choices = [c for c in choices if any(word in c.path.stem.lower() for word in ('chica', 'cupcake', 'food', 'pizza'))] or choices
            if pet.name == 'Freddy':
                choices = [c for c in choices if c.origin is pet] or choices
            card = random.choice(choices)
        if card not in choices:
            return False
        self.jobs[pet] = Job('seek', card=card, timeout=self.clock+90)
        return True

    def tick(self, dt):
        self.clock += dt
        if self.clock < self.next_decision:
            return
        self.next_decision = self.clock+2
        for pet in self.c.pets:
            level = self.c.settings['activity'][pet.name]/20
            if pet in self.jobs or not pet.isVisible() or pet.name == 'Golden Freddy':
                continue
            theft = {'Foxy': 1.8, 'Freddy': .35, 'Bonnie': .9, 'Chica': 1.1, 'Springtrap': .3}[pet.name]
            if random.random() < self.c.settings['theft_chance']*level*theft:
                if self.attempt_theft(pet, direct=pet.name == 'Foxy' and random.random() < .08):
                    continue
            if random.random() < self.c.settings['drag_chance']*level:
                self.start_fetch(pet)

    def move(self, pet, target, dt, sprint=False):
        dx, dy = target[0]-pet.posx, target[1]-pet.posy
        distance = math.hypot(dx, dy)
        speed = {'Freddy': 45, 'Bonnie': 70, 'Chica': 55, 'Foxy': 110, 'Springtrap': 30, 'Golden Freddy': 20}[pet.name]
        speed *= self.c.settings['speed'] * (2.4 if sprint else 1) * (.65 if self.c.settings['mode'] == 'calm' else 1)
        step = min(distance, speed*dt)
        if distance > .01:
            pet.posx += dx/distance*step
            pet.posy += dy/distance*step
            pet.direction = 1 if dx >= 0 else -1
        pet.frame += self.c.settings['animationspeed']*dt*30*(2 if sprint else 1)
        pet.state = 'run' if sprint else 'walk'
        pet.move(round(pet.posx), round(pet.posy))
        pet.show()
        pet.update()
        return distance <= max(3, step)

    def cancel(self, pet):
        self.c.images.release_pet(pet)
        self.jobs.pop(pet, None)
        pet.state = 'walk'

    def acquired(self, pet, job):
        previous = job.card.owner
        if not self.c.images.claim(job.card, pet, steal=True):
            self.cancel(pet)
            return
        if previous is not None and previous is not pet:
            self.jobs.pop(previous, None)
            if previous.name == 'Freddy' and pet.name == 'Foxy' and random.random() < self.c.settings['chase_chance']:
                self.jobs[previous] = Job('chase', card=job.card, victim=pet, timeout=self.clock+14)
        job.phase, job.target = 'carry', self.destination(pet)
        job.timeout = self.clock+100
        self.c.audio.play('theft', self.c.settings)

    def tick_pet(self, pet, dt):
        if pet.name == 'Golden Freddy':
            if not hasattr(pet, 'gold_next'):
                pet.gold_next = self.clock+random.uniform(100, 220)
                pet.gold_until = 0
            if self.clock >= pet.gold_next:
                r = pet.screen.availableGeometry()
                cursor = QCursor.pos()
                pet.posx = max(r.left(), min(r.right()-110, cursor.x()+35))
                pet.posy = max(r.top(), min(r.bottom()-150, cursor.y()+25))
                pet.move(round(pet.posx), round(pet.posy))
                pet.gold_until = self.clock+1.6
                level = self.c.settings['activity'][pet.name]
                pet.gold_next = self.clock+random.uniform(100, 220)*10/max(1, level)
                pet.state = 'watch'
                pet.show()
            if self.clock >= pet.gold_until:
                pet.state = 'hide'
                pet.hide()
            return True
        if any(job.phase == 'tug' and job.card is not None and job.card.owner is pet for actor, job in self.jobs.items() if actor is not pet):
            pet.state = 'watch'
            return True
        job = self.jobs.get(pet)
        if job is None:
            return False
        if self.clock > job.timeout or job.card is not None and job.card not in self.c.images.cards:
            self.cancel(pet)
            return False
        if job.phase == 'edge':
            if self.move(pet, job.target, dt):
                job.card = self.c.images.create(screen=pet.screen, origin=pet, position=(pet.posx, pet.posy+65))
                if job.card is None:
                    self.cancel(pet)
                else:
                    self.acquired(pet, job)
        elif job.phase in ('seek', 'chase'):
            card = job.card
            r = pet.screen.availableGeometry()
            target = (max(r.left(), min(r.right()-110, card.xf+card.width()/2-55)), max(r.top(), min(r.bottom()-150, card.yf-45)))
            if self.move(pet, target, dt, sprint=job.phase == 'chase'):
                if card.owner not in (None, pet):
                    # One logical owner during the visual tug; transfer atomically afterwards.
                    card.tug = 1.1
                    job.phase, job.until = 'tug', self.clock+1.1
                else:
                    job.phase, job.until = 'inspect', self.clock+(2 if pet.name == 'Bonnie' else .4)
        elif job.phase in ('inspect', 'tug'):
            pet.state = 'watch'
            if self.clock >= job.until:
                if job.phase == 'inspect' and pet.name == 'Bonnie' and random.random() < .3:
                    self.cancel(pet)
                else:
                    self.acquired(pet, job)
        elif job.phase == 'carry':
            if job.card.owner is not pet:
                self.cancel(pet)
                return False
            sprint = pet.name == 'Foxy'
            if self.move(pet, job.target, dt, sprint=sprint) or sprint and random.random() < dt*.08:
                self.c.images.drop(job.card)
                self.jobs.pop(pet, None)
                pet.state = 'walk'
        return True

    def clear(self):
        for pet in list(self.jobs):
            self.cancel(pet)
        for pet in self.c.pets:
            self.c.images.release_pet(pet)
