"""Discover replaceable media; bundled defaults and user additions share one route."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QImageReader, QPixmap

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}

def image_files(root):
    roots = [root/'images'/'random', root/'images'/'memes', root/'popups']
    return sorted({p for folder in roots if folder.exists() for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS})


def safe_pixmap(path, maximum=1600):
    """Decode to a bounded size instead of caching giant user photos at full size."""
    reader = QImageReader(str(path))
    size = reader.size()
    if size.isValid() and max(size.width(), size.height()) > maximum:
        size.scale(maximum, maximum, Qt.AspectRatioMode.KeepAspectRatio)
        reader.setScaledSize(size)
    return QPixmap.fromImage(reader.read())


def scare_source(root, name):
    slug = name.lower().replace(' ', '_')
    folder = root/'images'/'jumpscares'/slug
    video = next((p for p in [folder/'jumpscare.mp4', folder/'jumpscare.webm'] if p.is_file()), None)
    frames = sorted(p for p in folder.glob('frame_*') if p.suffix.lower() in IMAGE_EXTENSIONS) if folder.exists() else []
    return video, frames, root/slug/'scare.png'
