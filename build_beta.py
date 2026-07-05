import os
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / 'dist'
EXCLUDE_DIRS = {'dist', '__pycache__', 'outputs', 'saved'}


def get_version():
    init_path = ROOT / 'src' / '__init__.py'
    text = init_path.read_text(encoding='utf-8')
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
    return match.group(1) if match else '0.1.0-beta'


def make_zip():
    version = get_version()
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f'research-matcher-{version}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in ROOT.rglob('*'):
            if path.is_dir():
                continue
            if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):
                continue
            if path.suffix == '.pyc':
                continue
            z.write(path, path.relative_to(ROOT))
    print(f'Created {zip_path}')


if __name__ == '__main__':
    make_zip()
