"""Opt-in, read-only desktop icon discovery with a killable UI Automation helper."""
import json
import os
from pathlib import Path
import sys
from PySide6.QtCore import QProcess, QTimer
from .world import physical_rect


def desktop_path():
    if sys.platform != 'win32': return Path.home()/'Desktop'
    import ctypes, uuid
    from ctypes import wintypes
    guid=(ctypes.c_byte*16).from_buffer_copy(uuid.UUID('B4BFCC3A-DB2C-424C-B029-7FE99A87C641').bytes_le)
    value=ctypes.c_wchar_p()
    fn=ctypes.windll.shell32.SHGetKnownFolderPath
    fn.argtypes=[ctypes.c_void_p,wintypes.DWORD,wintypes.HANDLE,ctypes.POINTER(ctypes.c_wchar_p)]
    if fn(ctypes.byref(guid),0,None,ctypes.byref(value)) != 0:return None
    result=Path(value.value)
    ctypes.windll.ole32.CoTaskMemFree(value)
    return result


def candidates(folder):
    if folder is None:return []
    result=[]
    try:
        for path in folder.iterdir():
            if len(result)>=100:break
            if path.is_symlink() or path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):continue
            stat=path.stat()
            if stat.st_size>20*1024*1024 or getattr(stat,'st_file_attributes',0)&(0x1000|0x400000):continue
            if path.is_file():result.append(path)
    except OSError:
        pass
    return result


def scan():
    if sys.platform != 'win32':return []
    import comtypes.client
    from .core import settings_path
    cache=settings_path().parent/'comcache'
    cache.mkdir(parents=True,exist_ok=True)
    comtypes.client.gen_dir=str(cache)
    module=comtypes.client.GetModule('UIAutomationCore.dll')
    automation=comtypes.client.CreateObject(module.CUIAutomation,interface=module.IUIAutomation)
    roots=automation.GetRootElement().FindAll(2,automation.CreateOrCondition(automation.CreatePropertyCondition(30012,'Progman'),automation.CreatePropertyCondition(30012,'WorkerW')))
    files=candidates(desktop_path())
    names={}
    for path in files:
        for name in {path.name,path.stem}:names.setdefault(name,[]).append(path)
    result=[]
    for index in range(roots.Length):
        icons=roots.GetElement(index).FindAll(4,automation.CreatePropertyCondition(30003,50007))
        for j in range(min(icons.Length,500)):
            icon=icons.GetElement(j)
            match=names.get(icon.CurrentName,[])
            if len(match)!=1 or icon.CurrentIsOffscreen:continue
            rect=icon.CurrentBoundingRectangle
            if rect.right>rect.left and rect.bottom>rect.top:
                result.append(dict(path=str(match[0]),rect=[rect.left,rect.top,rect.right-rect.left,rect.bottom-rect.top]))
    return result[:100]


class DesktopImages:
    def __init__(self,c):
        self.c=c;self.entries=[];self.next_scan=0;self.error=''
        self.process=QProcess(c.app)
        self.process.finished.connect(self.finished)
        self.timeout=QTimer(c.app);self.timeout.setSingleShot(True)
        self.timeout.timeout.connect(self.process.kill)
        self.output=None

    def tick(self,now):
        if not self.c.settings['desktop_theft']:
            self.entries=[]
            if self.process.state()!=QProcess.ProcessState.NotRunning:self.close()
            return
        if now<self.next_scan or self.process.state()!=QProcess.ProcessState.NotRunning:return
        self.next_scan=now+30
        if sys.platform!='win32':return
        # A bounded result file also works with PyInstaller's windowed stdout=None.
        from .core import settings_path
        self.output=settings_path().parent/'desktop-scan.json'
        args=['--desktop-scan']
        if not getattr(sys,'frozen',False):args=[str(Path(__file__).resolve().parents[1]/'run.py'),*args]
        self.process.start(sys.executable,args)
        self.timeout.start(2500)

    def finished(self,*_):
        self.timeout.stop()
        self.entries=[]
        try:
            if self.process.exitCode()!=0:return
            data=json.loads(self.output.read_text())
            for entry in data[:100]:
                r=physical_rect(entry['rect'],self.c.app.screens())
                self.entries.append(dict(path=Path(entry['path']),x=r.center().x(),y=r.center().y()))
        except (OSError,ValueError,KeyError,TypeError,AttributeError):
            self.error='Bureaubladpictogrammen konden niet worden gelezen.'
        finally:
            if self.output:self.output.unlink(missing_ok=True)

    def close(self):
        self.timeout.stop()
        if self.process.state()!=QProcess.ProcessState.NotRunning:
            self.process.kill();self.process.waitForFinished(1500)
        self.entries=[]
        if self.output:self.output.unlink(missing_ok=True)
