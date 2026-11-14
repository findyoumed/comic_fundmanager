import argparse
import csv
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp'}
NAVER_WIDTH = 690
NAVER_FILE_LIMIT = 5 * 1024 * 1024
NAVER_EPISODE_LIMIT = 50 * 1024 * 1024
REVIEW_KEYS = (
    'mobile_readability',
    'scroll_flow',
    'character_consistency',
    'source_accuracy',
    'naver_export_check',
)
CHAPTER_SCOPES = {
    '04-': {'plan': 'CHAPTER_04_PLAN.md', 'topics': 19, 'chapter_label': 'Chapter 4'},
    '05-': {'plan': 'CHAPTER_05_PLAN.md', 'topics': 18, 'chapter_label': 'Chapter 5'},
}


def jpeg_dimensions(path):
    """Return dimensions from a JPEG SOF marker without external dependencies."""
    with path.open('rb') as stream:
        data = stream.read()
    if not data.startswith(b'\xff\xd8'):
        return None
    index = 2
    while index < len(data):
        while index < len(data) and data[index] != 0xff:
            index += 1
        while index < len(data) and data[index] == 0xff:
            index += 1
        if index >= len(data):
            return None
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            return None
        length = int.from_bytes(data[index:index + 2], 'big')
        if length < 2 or index + length > len(data):
            return None
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height = int.from_bytes(data[index + 3:index + 5], 'big')
            width = int.from_bytes(data[index + 5:index + 7], 'big')
            return width, height
        index += length
    return None


def validate_chapter_scope(root, scope, manifests):
    config = CHAPTER_SCOPES.get(scope)
    if not config:
        return None, []

    errors = []
    plan_path = root / config['plan']
    expected_count = config['topics']
    episode_prefix = scope.rstrip('-')
    chapter_label = config['chapter_label']
    expected_ids = [f"{episode_prefix}-{n:02d}" for n in range(1, expected_count + 1)]
    planned = []
    if not plan_path.is_file():
        errors.append(f'missing {config["plan"]} for {chapter_label} scope')
    else:
        for line in plan_path.read_text(encoding='utf-8-sig').splitlines():
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            if len(cells) >= 5 and cells[0].isdigit() and re.fullmatch(rf'{re.escape(episode_prefix)}-\d{{2}}', cells[4]):
                planned.append((cells[0], cells[1], cells[4]))
        if len(planned) != expected_count:
            errors.append(f'{config["plan"]}: expected {expected_count} planned Topics, found {len(planned)}')
        if [row[2] for row in planned] != expected_ids:
            errors.append(f'{config["plan"]}: {chapter_label} episodes must map Topic 01 through Topic {expected_count:02d} in order')

    planned_by_id = {episode_id: (topic_number, title) for topic_number, title, episode_id in planned}
    found_ids = [manifest.parent.name for manifest in manifests]
    if found_ids != expected_ids[:len(found_ids)]:
        errors.append(f'{chapter_label} episode manifests must be produced sequentially from {expected_ids[0]} without gaps')

    complete_count = 0
    export_manifest_path = root / 'upload_ready' / 'NAVER_EXPORT_MANIFEST.csv'
    export_rows = {}
    if export_manifest_path.is_file():
        try:
            with export_manifest_path.open(encoding='utf-8-sig', newline='') as stream:
                for row in csv.DictReader(stream):
                    export_rows[(row.get('episode'), row.get('filename'))] = row
        except Exception as exc:
            errors.append(f'{export_manifest_path}: {exc}')
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding='utf-8-sig'))
        except Exception:
            continue
        episode_id = data.get('id', manifest.parent.name)
        planned_row = planned_by_id.get(episode_id)
        if planned_row:
            topic_number, title = planned_row
            source_topic = data.get('sourceTopic', '')
            topic_number_int = int(topic_number)
            topic_marker = re.search(r'Topic\s+0*' + str(topic_number_int) + r'\b', source_topic)
            if not topic_marker or title not in source_topic:
                errors.append(f'{manifest}: sourceTopic does not match {config["plan"]} Topic {topic_number_int:02d}')
        if data.get('status') == 'complete':
            complete_count += 1
            episode_id = data.get('id', manifest.parent.name)
            png_assets = data.get('scrollAssets', [])
            if not png_assets:
                errors.append(f'{manifest}: complete episode has no scrollAssets list')
            export_dir_value = data.get('exportDirectory')
            if not export_dir_value:
                errors.append(f'{manifest}: complete episode has no exportDirectory')
                continue
            export_dir = (manifest.parent / export_dir_value).resolve()
            total_bytes = 0
            for asset in png_assets:
                png_path = manifest.parent / asset
                if not png_path.is_file():
                    errors.append(f'{manifest}: missing scroll asset {asset}')
                    continue
                jpg_path = export_dir / (png_path.stem + '.jpg')
                if not jpg_path.is_file():
                    errors.append(f'{manifest}: missing Naver JPG {jpg_path}')
                    continue
                file_size = jpg_path.stat().st_size
                total_bytes += file_size
                dimensions = jpeg_dimensions(jpg_path)
                if dimensions is None:
                    errors.append(f'{jpg_path}: invalid JPEG image')
                elif dimensions[0] != NAVER_WIDTH:
                    errors.append(f'{jpg_path}: width must be {NAVER_WIDTH}px, found {dimensions[0]}px')
                if file_size > NAVER_FILE_LIMIT:
                    errors.append(f'{jpg_path}: exceeds the 5MB Naver per-file limit')
                row = export_rows.get((episode_id, jpg_path.name))
                if row is None:
                    errors.append(f'{export_manifest_path}: missing row for {episode_id}/{jpg_path.name}')
                else:
                    try:
                        if int(row.get('width_px', 0)) != NAVER_WIDTH or int(row.get('bytes', 0)) != file_size:
                            errors.append(f'{export_manifest_path}: dimensions/bytes do not match {jpg_path}')
                    except (TypeError, ValueError):
                        errors.append(f'{export_manifest_path}: invalid dimensions/bytes for {episode_id}/{jpg_path.name}')
            if total_bytes > NAVER_EPISODE_LIMIT:
                errors.append(f'{manifest}: exported episode exceeds the 50MB Naver limit')

    progress = {
        'planned_topics': expected_count,
        'episodes_found': len(manifests),
        'episodes_complete': complete_count,
        'topics_remaining': expected_count - complete_count,
    }
    return progress, errors


def check(root=ROOT, scope=None):
    errors = []
    warnings = []
    draft_assets = []

    for filename in ('GOAL.md', 'CHARACTER_SHEET.md', 'SOURCE_TOC_MAP.md'):
        if not (root / filename).is_file():
            errors.append(f'missing {filename}')
    toc_path = root / 'SOURCE_TOC_MAP.md'
    if toc_path.is_file() and '각색 회차 연결표' not in toc_path.read_text(encoding='utf-8-sig'):
        errors.append('SOURCE_TOC_MAP.md: missing adaptation episode map')

    all_manifests = sorted((root / 'chapters').glob('*/chapter.json'))
    manifests = [m for m in all_manifests if scope is None or m.parent.name.startswith(scope)]
    if scope is not None and not manifests:
        errors.append(f'no episode manifests matched scope {scope!r}')

    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding='utf-8-sig'))
            if not data.get('id'):
                errors.append(f'{manifest}: missing id')
            if not data.get('title'):
                errors.append(f'{manifest}: missing title')
            if not (data.get('source_pages') or data.get('sourcePage')):
                errors.append(f'{manifest}: missing source page mapping')
            for key in ('script', 'storyboard', 'explanation'):
                filename = data.get(key, f'{key}.md')
                if not (manifest.parent / filename).is_file():
                    errors.append(f'{manifest}: missing file {filename}')
        except Exception as exc:
            errors.append(f'{manifest}: {exc}')
            continue

        scroll_dir = manifest.parent / 'scroll'
        segments = sorted(
            p for p in scroll_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES
        ) if scroll_dir.is_dir() else []
        episode_id = data.get('id', manifest.parent.name)
        actual_scroll_assets = [f'scroll/{p.name}' for p in segments if p.suffix.lower() == '.png']
        declared_scroll_assets = data.get('scrollAssets', [])
        if data.get('status') == 'complete' and sorted(declared_scroll_assets) != sorted(actual_scroll_assets):
            errors.append(f'{manifest}: scrollAssets must match the PNG files in scroll/')
        if len(segments) < 2:
            warnings.append(f'{manifest.parent}: needs at least two sequential images in scroll/')
        else:
            expected = [f'{episode_id}-{i:03d}' for i in range(1, len(segments) + 1)]
            actual = [p.stem for p in segments]
            if actual != expected:
                warnings.append(f'{manifest.parent}: scroll images must be named 001, 002, ... without gaps')

        review_file = manifest.parent / 'webtoon_review.json'
        try:
            review = json.loads(review_file.read_text(encoding='utf-8-sig'))
            for key in REVIEW_KEYS:
                if review.get(key) != 'passed':
                    warnings.append(f'{review_file}: {key} review is not passed')
        except Exception:
            warnings.append(f'{manifest.parent}: missing valid webtoon_review.json')
        if data.get('format') != 'naver-webtoon-vertical-scroll':
            warnings.append(f'{manifest}: format must be naver-webtoon-vertical-scroll')

    for image in sorted((root / 'chapters').glob('*/*.png')):
        if scope is not None and not image.parent.name.startswith(scope):
            continue
        try:
            with image.open('rb') as stream:
                header = stream.read(24)
            if header[:8] != b'\x89PNG\r\n\x1a\n':
                draft_assets.append(f'{image}: invalid PNG header')
                continue
            width, height = struct.unpack('>II', header[16:24])
            draft_assets.append(f'{image}: {width}x{height} preserved as a legacy page draft')
        except Exception as exc:
            draft_assets.append(f'{image}: image dimension check failed: {exc}')

    return len(manifests), errors, warnings, draft_assets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check investment comic project assets and reviews.')
    parser.add_argument('--scope', help='Limit episode checks to a folder prefix, e.g. 08- or 09-.')
    args = parser.parse_args()

    count, errors, warnings, draft_assets = check(scope=args.scope)
    chapter_progress, chapter_errors = validate_chapter_scope(
        ROOT,
        args.scope,
        [m for m in sorted((ROOT / 'chapters').glob('*/chapter.json')) if args.scope and m.parent.name.startswith(args.scope)],
    )
    errors.extend(chapter_errors)
    ready = not errors and not warnings
    result = {
        'scope': args.scope or 'all',
        'episodes_checked': count,
        'errors': errors,
        'format': 'Naver Webtoon only',
        'webtoon_ready': ready,
        'webtoon_warnings': warnings,
        'preserved_draft_assets': draft_assets,
        'chapter_progress': chapter_progress,
        'note': 'Scoped checks do not hide warnings from other chapters. Verify current Naver creator upload requirements before publication.',
    }
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if ready else 1)
