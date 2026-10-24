"""Validate and ZIP the complete Windows onedir build, never a lone EXE."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def package():
    folder = ROOT/'dist'/'FNAFDesktop'
    required = ['FNAFDesktop.exe', '_internal/assets/freddy_scare.wav',
        '_internal/assets/images/golden_freddy/golden_freddy_flicker.png', '_internal/config.json']
    for name in required:
        if not (folder/name).is_file():
            raise FileNotFoundError('Windows-build onvolledig: '+name)
    (folder/'START_HIER.txt').write_text('Start FNAFDesktop.exe. Bewaar de hele map inclusief _internal.\nESC stopt een effect. ESC 5 seconden of Ctrl+Shift+Q sluit de app volledig.\nInstellingen: Ctrl+Shift+S, rechtsklik op een personage of Instellingen.bat. Geen Python-installatie nodig voor deze EXE.\nEigen media: _internal/assets; instructies staan in _internal/assets/README.md.\n', encoding='utf8')
    (folder/'Instellingen.bat').write_text('@echo off\ncd /d "%~dp0"\nstart "" "FNAFDesktop.exe" --settings\n',encoding='utf8')
    output = ROOT/'dist'/'FNAFDesktop-V3.0-Windows.zip'
    files = sorted(p for p in folder.rglob('*') if p.is_file())
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(folder.parent))
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        for name in required:
            assert 'FNAFDesktop/'+name in archive.namelist()
    print('Windows-ZIP geverifieerd:', output)


if __name__ == '__main__':
    package()
