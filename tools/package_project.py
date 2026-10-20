"""Make a source-only ZIP without virtual environments, secrets or recursive ZIPs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ['.github', '.gitignore', 'README.md', 'VALIDATIE.md', 'assets', 'build_windows.bat',
         'fnaf_desktop', 'generated_audio', 'requirements.txt', 'run.py', 'settings.json', 'tests', 'tools']
SKIP = {'__pycache__', '.pytest_cache', '.venv', '.venv-windows'}

def package():
    output = ROOT / 'downloads' / 'FNAF-project.zip'
    output.parent.mkdir(exist_ok=True)
    files = []
    for item in ITEMS:
        path = ROOT / item
        if not path.exists():
            raise FileNotFoundError(path)
        files.extend([path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts)))
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path('FNAF')/path.relative_to(ROOT))
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        for path in files:
            assert archive.read(str(Path('FNAF')/path.relative_to(ROOT))) == path.read_bytes()
    print(f'Verified {output}: {len(files)} files, {output.stat().st_size} bytes')
    return output

if __name__ == '__main__':
    package()
