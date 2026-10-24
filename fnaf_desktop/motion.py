"""Time-based steering shared by roaming, image jobs and window interactions."""
from dataclasses import dataclass
from enum import StrEnum
import math

class State(StrEnum):
    IDLE='idle'; WALKING='walk'; RUNNING='run'; FOLLOWING_CURSOR='follow'
    WATCHING_CURSOR='watch'; INVESTIGATING='inspect'; CLIMBING='climb'
    SITTING='sit'; JUMPING='jump'; CARRYING_IMAGE='carry'; INTERACTING='interact'
    JUMPSCARE='scare'; HIDING='hide'; DISAPPEARING='disappear'; TRIPPING='trip'

@dataclass
class Motion:
    vx: float = 0
    vy: float = 0
    facing: float = 1

    def stop(self):
        self.vx = self.vy = 0

    def advance(self, x, y, target, speed, dt):
        dt = max(0, min(.1, dt))
        dx, dy = target[0]-x, target[1]-y
        distance = math.hypot(dx, dy)
        if distance < 2:
            self.stop()
            return target[0], target[1], True
        acceleration = max(120, speed*3)
        desired = min(speed, math.sqrt(2*acceleration*distance))
        vx, vy = dx/distance*desired, dy/distance*desired
        change = math.hypot(vx-self.vx, vy-self.vy)
        blend = min(1, acceleration*dt/max(.001, change))
        self.vx += (vx-self.vx)*blend
        self.vy += (vy-self.vy)*blend
        step = math.hypot(self.vx, self.vy)*dt
        if step >= distance:
            self.stop()
            return target[0], target[1], True
        return x+self.vx*dt, y+self.vy*dt, False


def steer(pet, target, dt, speed, state='walk'):
    old = (pet.posx, pet.posy)
    pet.posx, pet.posy, arrived = pet.motion.advance(*old, target, speed, dt)
    if abs(pet.motion.vx) > 2:
        pet.direction = 1 if pet.motion.vx > 0 else -1
    blend = min(1, dt*10)
    pet.motion.facing += (pet.direction-pet.motion.facing)*blend
    distance = math.hypot(pet.posx-old[0], pet.posy-old[1])
    pet.frame += distance*.22*pet.c.settings['animationspeed']
    pet.state = state
    pet.move(round(pet.posx), round(pet.posy))
    pet.update()
    return arrived
