"""Window, cursor and social actions using the existing director's job table."""
import math
import random
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor, QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget
from .motion import steer

PHASES={'approach_window','climb','edge_enter','perch','edge_walk','knock','behind','reveal','jump','trip','sit','social','party','desktop_seek','desktop_inspect','give','fake_drag'}

class DragOutline(QWidget):
    def __init__(self, rect):
        super().__init__(None,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.WindowTransparentForInput|Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setGeometry(rect)
        self.show()
    def paintEvent(self,event):
        p=QPainter(self)
        p.setPen(QPen(QColor(180,150,110,180),3,Qt.PenStyle.DashLine))
        p.setBrush(QColor(25,20,30,25))
        p.drawRect(self.rect().adjusted(3,3,-3,-3))

class Interactions:
    def __init__(self,director):
        self.d=director
        self.c=director.c
        self.next_group=40
        self.outlines={}
        self.cursor=QCursor.pos()
        self.cursor_speed=0
        self.next_investigation=0

    def new(self,pet,phase,**kwargs):
        from .behaviour import Job
        self.d.jobs[pet]=Job(phase,timeout=self.d.clock+45,**kwargs)
        return self.d.jobs[pet]

    def clear_pet(self,pet):
        outline=self.outlines.pop(pet,None)
        if outline:
            outline.close(); outline.deleteLater()
        pet.setMask(pet.base_mask)
        pet.motion.stop()

    def window_job(self,pet,kind=None):
        surfaces=self.c.world.on_screen(pet.screen)
        if not self.c.settings['window_interactions'] or not surfaces: return False
        surface=random.choice(surfaces)
        action=kind or random.choice({'Freddy':['sit','knock','fake_drag'], 'Bonnie':['climb','knock','edge_walk'], 'Chica':['trip','jump','sit'], 'Foxy':['behind','edge_walk','jump'], 'Golden Freddy':['behind'], 'Springtrap':['behind','climb']}[pet.name])
        if action in ('sit','climb','edge_walk','trip') and surface.rect.top()<pet.screen.availableGeometry().top()+pet.height():
            action='knock'
        job=self.new(pet,'behind' if action=='behind' else 'approach_window',surface=surface.handle,action=action,until=self.d.clock+random.uniform(3,7))
        if pet.name=='Golden Freddy' and action=='behind':job.until=self.d.clock+40
        return True

    def choose(self,pet):
        if pet in self.d.jobs: return False
        if self.c.settings['desktop_theft'] and self.c.desktop.entries and random.random()<.25:
            entry=random.choice(self.c.desktop.entries)
            screen=self.c.app.screenAt(QPoint(round(entry['x']),round(entry['y'])))
            if screen is pet.screen:
                self.new(pet,'desktop_seek',target=(entry['x'],entry['y']),entry=entry)
                return True
        if self.c.settings['window_interactions'] and random.random()<.6 and self.window_job(pet): return True
        if self.c.settings['group_activities'] and random.random()<.35:
            others=[p for p in self.c.pets if p is not pet and p.screen is pet.screen and p.isVisible()]
            if others:
                self.new(pet,'social',victim=random.choice(others),until=self.d.clock+5)
                return True
        if random.random()<.3:
            self.new(pet,random.choice(['jump','sit','trip'] if pet.name=='Chica' else ['sit','jump']),until=self.d.clock+2)
            return True
        return False

    def tick(self,dt):
        cursor=QCursor.pos()
        self.cursor_speed=(cursor-self.cursor).manhattanLength()/max(dt,.001)
        self.cursor=cursor
        if self.c.settings['window_interactions'] and self.d.clock>=self.next_investigation:
            for handle in self.c.world.new_handles:
                surface=self.c.world.surfaces.get(handle)
                pet=next((p for p in self.c.pets if p.name=='Bonnie' and p not in self.d.jobs and p.isVisible() and surface and p.screen.availableGeometry().intersects(surface.rect)),None)
                if pet and self.window_job(pet,'knock'):
                    self.d.jobs[pet].surface=handle
                    self.next_investigation=self.d.clock+20
                    break
        self.c.world.new_handles=[]
        if self.c.settings['group_activities'] and self.d.clock>=self.next_group:
            self.next_group=self.d.clock+random.uniform(40,100)
            if random.random()<.5: self.meeting()

    def meeting(self):
        participants=[p for p in self.c.pets if p not in self.d.jobs and p.isVisible() and p.name!='Golden Freddy'][:6]
        if len(participants)<2: return False
        leader=participants[0]
        if self.c.settings['window_interactions'] and self.c.world.on_screen(leader.screen) and random.random()<.3:
            handle=self.c.world.on_screen(leader.screen)[0].handle
            for pet in participants[:2]:
                if self.window_job(pet,'sit'):self.d.jobs[pet].surface=handle
            return True
        participants=[p for p in participants if p.screen is leader.screen]
        for index,pet in enumerate(participants):
            self.new(pet,'party',target=(leader.posx+(index%3-1)*pet.width(),leader.posy+(index//3)*pet.height()*.3),until=self.d.clock+18)
        return True

    def target(self,pet,point):
        r=pet.screen.availableGeometry()
        return max(r.left(),min(r.right()-pet.width(),point[0])),max(r.top(),min(r.bottom()-pet.height(),point[1]))

    def step(self,pet,job,dt):
        now=self.d.clock
        if now>job.timeout:
            self.d.cancel(pet); return True
        surface=self.c.world.surfaces.get(job.surface)
        if job.surface and surface is None:
            if job.phase=='behind':
                job.phase='reveal'; job.surface=0; job.until=now+1.2
                pet.setMask(pet.base_mask); pet.show()
            else:
                self.d.cancel(pet); return True
        if job.phase=='behind':
            # The sprite's own mask is cut against the other window. Never change its z-order.
            if job.last_rect is None:
                pet.posx,pet.posy=self.target(pet,(surface.rect.center().x()-pet.width()/2,surface.rect.center().y()-pet.height()/2))
                job.last_rect=surface.rect.getRect()
            moved=job.last_rect!=surface.rect.getRect()
            pet.move(round(pet.posx),round(pet.posy))
            self.c.world.occlude(pet,job.surface)
            pet.state='hide'
            if moved or now>job.until:
                job.phase='reveal'; job.until=now+1.2
                pet.posx,pet.posy=self.target(pet,(surface.rect.right()+8,pet.posy))
                pet.setMask(pet.base_mask);pet.show()
            return True
        if job.phase in ('approach_window','climb','edge_enter','perch','edge_walk','knock','fake_drag'):
            r=surface.rect
            foot=(r.left()-pet.width()*.65,r.bottom()-pet.height())
            top=(r.left()+min(max(0,r.width()-pet.width()),self.c.pets.index(pet)*pet.width()),r.top()-pet.height()+5)
            if job.phase=='approach_window':
                if self.d.move(pet,self.target(pet,foot),dt):
                    job.phase='climb' if job.action in ('climb','sit','edge_walk','trip') else job.action
                    job.until=now+3
                    if job.action=='jump':
                        job.start=(pet.posx,pet.posy);job.target=self.target(pet,top);job.until=now+1.2
            elif job.phase=='climb':
                if self.d.move(pet,self.target(pet,(foot[0],top[1])),dt):job.phase='edge_enter'
                pet.state='climb'
            elif job.phase=='edge_enter':
                if self.d.move(pet,self.target(pet,top),dt):
                    job.phase='edge_walk' if job.action=='edge_walk' else 'perch';job.until=now+4
                pet.state='climb'
            elif job.phase=='edge_walk':
                end=self.target(pet,(r.right()-pet.width(),top[1]))
                if self.d.move(pet,end,dt,sprint=pet.name=='Foxy') or now>job.until:self.d.cancel(pet)
            elif job.phase=='perch':
                pet.posx,pet.posy=self.target(pet,top);pet.move(round(pet.posx),round(pet.posy));pet.state='sit';pet.update()
                if now>job.until:
                    if job.action=='trip':job.phase='trip';job.until=now+1.4
                    else:self.d.cancel(pet)
            elif job.phase=='fake_drag':
                if pet not in self.outlines:self.outlines[pet]=DragOutline(r)
                self.outlines[pet].move(r.x()+round(math.sin(now*2)*18),r.y())
                pet.state='interact';pet.frame+=dt*20;pet.update()
                if now>job.until:self.d.cancel(pet)
            else:
                pet.state='knock';pet.frame+=dt*20;pet.update()
                if now>job.until:self.d.cancel(pet)
        elif job.phase in ('jump','trip','sit','reveal'):
            pet.state='jump' if job.phase=='reveal' else job.phase
            pet.pose_progress=1-max(0,job.until-now)/(1.2 if job.start else 2)
            if job.phase=='jump' and job.start:
                t=max(0,min(1,pet.pose_progress));t=t*t*(3-2*t)
                pet.posx=job.start[0]+(job.target[0]-job.start[0])*t
                pet.posy=job.start[1]+(job.target[1]-job.start[1])*t
                pet.move(round(pet.posx),round(pet.posy))
            elif job.phase=='trip' and job.surface:
                pet.posy=min(pet.screen.availableGeometry().bottom()-pet.height(),pet.posy+180*dt)
                pet.move(round(pet.posx),round(pet.posy))
            pet.frame+=dt*20;pet.update()
            if now>job.until:
                if job.phase=='jump' and job.surface:
                    job.phase='perch';job.until=now+3
                else:
                    if pet.name=='Golden Freddy':pet.hide()
                    self.d.cancel(pet)
        elif job.phase in ('social','party','give'):
            if job.phase=='party':target=job.target
            elif job.victim not in self.c.pets:self.d.cancel(pet);return True
            else:target=(job.victim.posx-pet.width(),job.victim.posy)
            arrived=self.d.move(pet,self.target(pet,target),dt,sprint=pet.name=='Foxy')
            if arrived:
                pet.state='sit' if job.phase=='party' else 'interact'
                if job.phase=='give' and job.card in self.c.images.cards:
                    if self.c.images.claim(job.card,job.victim,steal=True):
                        self.d.jobs.pop(pet,None)
                        from .behaviour import Job
                        self.d.jobs[job.victim]=Job('carry',target=self.d.destination(job.victim),card=job.card,timeout=now+60)
                        return True
            if now>job.until:self.d.cancel(pet)
        elif job.phase in ('desktop_seek','desktop_inspect'):
            if job.phase=='desktop_seek':
                if self.d.move(pet,self.target(pet,job.target),dt):job.phase='desktop_inspect';job.until=now+1.2
            else:
                pet.state='inspect'
                if now>job.until:
                    card=self.c.images.create(path=job.entry['path'],screen=pet.screen,origin=pet,position=job.target)
                    if card:
                        job.card=card;self.d.acquired(pet,job)
                    else:self.d.cancel(pet)
        return True
