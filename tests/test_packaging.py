"""Package structure tests use dummy files; they do not claim a Windows build."""
import importlib.util
from pathlib import Path
from zipfile import ZipFile
import pytest


def load_packager(tmp_path):
    source=Path(__file__).resolve().parents[1]/'tools'/'package_windows.py'
    spec=importlib.util.spec_from_file_location('package_windows_test',source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT=tmp_path
    return module


def test_windows_zip_contains_whole_directory(tmp_path):
    packager=load_packager(tmp_path)
    required=['FNAFDesktop.exe','_internal/assets/freddy_scare.wav',
        '_internal/assets/images/golden_freddy/golden_freddy_flicker.png','_internal/config.json']
    for name in required:
        path=tmp_path/'dist'/'FNAFDesktop'/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(b'test fixture, not a real executable')
    packager.package()
    with ZipFile(tmp_path/'dist'/'FNAFDesktop-Chaos-2.0-Windows.zip') as archive:
        assert archive.testzip() is None
        assert all('FNAFDesktop/'+name in archive.namelist() for name in required)
        assert 'FNAFDesktop/START_HIER.txt' in archive.namelist()


def test_incomplete_windows_folder_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_packager(tmp_path).package()
