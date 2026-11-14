from pathlib import Path
from PIL import Image
import csv

root = Path(__file__).resolve().parents[1]
ep = '05-06'
source = root / 'chapters' / ep / 'scroll'
files = sorted(source.glob('*.png'))
assert len(files) == 10, f'Expected 10 cuts, found {len(files)}'
dest = root / 'upload_ready/naver_challenge' / ep
dest.mkdir(parents=True, exist_ok=True)
rows = []
for p in files:
    im = Image.open(p).convert('RGB')
    im = im.resize((690, round(im.height * 690 / im.width)), Image.Resampling.LANCZOS)
    out = dest / (p.stem + '.jpg')
    im.save(out, 'JPEG', quality=90, optimize=True, progressive=True)
    rows.append(dict(episode=ep, filename=out.name, width_px=im.width, height_px=im.height, bytes=out.stat().st_size))
assert all(r['bytes'] < 5 * 1024 * 1024 for r in rows)
assert sum(r['bytes'] for r in rows) < 50 * 1024 * 1024
manifest = root / 'upload_ready/NAVER_EXPORT_MANIFEST.csv'
old = list(csv.DictReader(manifest.open(encoding='utf-8-sig', newline='')))
with manifest.open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['episode', 'filename', 'width_px', 'height_px', 'bytes'], quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows([r for r in old if r['episode'] != ep] + rows)
print(f'Exported {len(rows)} JPGs, {sum(r["bytes"] for r in rows)} bytes')
