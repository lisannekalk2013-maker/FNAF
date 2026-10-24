"""Read-only Win32 window geometry. No window movement, titles or contents read."""
from dataclasses import dataclass
import ctypes
import os
import sys
from PySide6.QtCore import QRect, QPoint
from PySide6.QtGui import QRegion

@dataclass
class Surface:
    handle: int
    rect: QRect


def physical_rect(rect, screens):
    # Qt screen origins remain in native virtual-desktop coordinates on Windows;
    # sizes and offsets within each screen are device-independent.
    x, y, w, h = rect
    for screen in screens:
        g = screen.geometry()
        scale = screen.devicePixelRatio()
        if g.x() <= x+w/2 < g.x()+g.width()*scale and g.y() <= y+h/2 < g.y()+g.height()*scale:
            return QRect(round(g.x()+(x-g.x())/scale), round(g.y()+(y-g.y())/scale), round(w/scale), round(h/scale))
    return QRect(x,y,w,h)


def enumerate_windows(screens):
    if sys.platform != 'win32':
        return []
    from ctypes import wintypes as w
    user = ctypes.windll.user32
    user.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
    user.GetWindowRect.argtypes=[w.HWND,ctypes.POINTER(w.RECT)]
    user.IsWindowVisible.argtypes=[w.HWND]
    user.IsIconic.argtypes=[w.HWND]
    user.GetClassNameW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
    callback_type=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
    result=[]
    @callback_type
    def visit(hwnd, _):
        pid=w.DWORD()
        user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if pid.value == os.getpid() or not user.IsWindowVisible(hwnd) or user.IsIconic(hwnd):
            return True
        name=ctypes.create_unicode_buffer(128)
        user.GetClassNameW(hwnd,name,128)
        if name.value in ('Progman','WorkerW','Shell_TrayWnd','Shell_SecondaryTrayWnd','tooltips_class32'):
            return True
        rect=w.RECT()
        if not user.GetWindowRect(hwnd,ctypes.byref(rect)):
            return True
        try:
            cloaked=w.DWORD()
            dwm=ctypes.windll.dwmapi.DwmGetWindowAttribute
            dwm.argtypes=[w.HWND,w.DWORD,ctypes.c_void_p,w.DWORD]
            dwm(hwnd,14,ctypes.byref(cloaked),ctypes.sizeof(cloaked))
            if cloaked.value: return True
            dwm(hwnd,9,ctypes.byref(rect),ctypes.sizeof(rect))
        except OSError:
            pass
        if rect.right-rect.left >= 180 and rect.bottom-rect.top >= 100:
            result.append(Surface(int(hwnd), physical_rect((rect.left,rect.top,rect.right-rect.left,rect.bottom-rect.top),screens)))
        return len(result)<80
    user.EnumWindows.argtypes=[callback_type,w.LPARAM]
    user.EnumWindows(visit,0)
    return result


class WindowWorld:
    def __init__(self, controller, provider=None):
        self.c=controller
        self.provider=provider or enumerate_windows
        self.surfaces={}
        self.new_handles=[]
        self.clock=0
        self.next_scan=0

    def tick(self, dt):
        self.clock+=dt
        if self.clock < self.next_scan: return
        self.next_scan=self.clock+.5
        if not self.c.settings['window_interactions']:
            self.surfaces={}
            return
        try:
            previous=self.surfaces
            self.surfaces={s.handle:s for s in self.provider(self.c.app.screens())}
            self.new_handles=list(self.surfaces.keys()-previous.keys())
        except (OSError, ValueError):
            self.surfaces={}

    def on_screen(self, screen):
        return [s for s in self.surfaces.values() if screen.availableGeometry().intersects(s.rect)]

    def occlude(self, pet, handle):
        surface=self.surfaces.get(handle)
        if surface is None:
            pet.setMask(pet.base_mask)
            return
        local=surface.rect.translated(-round(pet.posx),-round(pet.posy))
        mask=pet.base_mask.subtracted(QRegion(local))
        # Empty QWidget masks mean no mask, so explicitly hide completely occluded pets.
        if mask.isEmpty(): pet.hide()
        else:
            pet.setMask(mask)
            pet.show()
