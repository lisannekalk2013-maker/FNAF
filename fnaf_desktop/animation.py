"""State animations, optional sheets, mirroring, shadows and pose fallbacks."""
import json
import math
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QImageReader
from .media import safe_pixmap

class Animator:
    def __init__(self, root, name, legacy):
        self.clips={'walk':legacy}
        folder=root/'animations'/name.lower().replace(' ','_')
        for state in ('walk','idle','run','turn','sit','climb','jump','trip','watch','knock','interact'):
            frames=[safe_pixmap(p,512) for p in sorted(folder.glob(state+'_*.png'))[:60]]
            valid=[p for p in frames if not p.isNull()]
            if valid or state!='walk': self.clips[state]=valid
        manifest=folder/'sheet.json'
        if manifest.is_file():
            try:
                data=json.loads(manifest.read_text())
                path=(folder/data['file']).resolve()
                if not path.is_relative_to(folder.resolve()): raise ValueError('sheet outside folder')
                reader=QImageReader(str(path))
                size=reader.size()
                if not size.isValid() or size.width()*size.height()>16_777_216:raise ValueError('sheet too large')
                sheet=QPixmap.fromImage(reader.read())
                w,h=int(data['width']),int(data['height'])
                if not (0<w<=1024 and 0<h<=1024): raise ValueError('frame size')
                columns=sheet.width()//w
                total=columns*(sheet.height()//h)
                for state, indices in data['clips'].items():
                    self.clips[state]=[sheet.copy(i%columns*w,i//columns*h,w,h) for i in indices[:60] if isinstance(i,int) and 0<=i<total]
            except (OSError,ValueError,KeyError,TypeError,ZeroDivisionError):
                pass

    def draw(self, painter, pet):
        state=pet.state
        turning=abs(pet.motion.facing-pet.direction)>.25
        clip='turn' if turning and self.clips.get('turn') else state
        frames=self.clips.get(clip) or self.clips['walk']
        if not frames: return
        phase=pet.frame
        frame_time=pet.animation_clock*10*pet.c.settings['animationspeed']
        if clip in ('walk','run','carry','follow'):frame_time=phase/3
        index=int(frame_time)%len(frames) if self.clips.get(clip) or state not in ('idle','watch','sit') else 0
        image=frames[index]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale=pet.width()/110
        painter.scale(scale,scale)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0,0,0,65))
        painter.drawEllipse(22,173,66,7)
        painter.translate(55,174)
        facing=pet.motion.facing
        painter.scale(max(.16,abs(facing))*(1 if facing>=0 else -1),1)
        if state=='sit': painter.scale(1,.76)
        if state=='trip': painter.rotate(65*math.sin(min(1,pet.pose_progress)*math.pi))
        if state=='jump': painter.translate(0,-math.sin(min(1,pet.pose_progress)*math.pi)*35)
        if state=='climb': painter.rotate(-12+5*math.sin(phase))
        if state in ('watch','idle'): painter.rotate(pet.look*.04)
        if state=='knock': painter.translate(math.sin(phase*2)*4,0)
        painter.drawPixmap(QRect(-53,-143,106,143),image)
        painter.restore()
