import json, sys
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def check(root=ROOT):
    errors=[]
    webtoon_warnings=[]
    legacy_page_drafts=[]
    for f in [root/'GOAL.md', root/'CHARACTER_SHEET.md']:
        if not f.is_file(): errors.append(f'missing {f.name}')
    if not (root/'SOURCE_TOC_MAP.md').is_file():
        errors.append('missing SOURCE_TOC_MAP.md: source-aligned table of contents is not confirmed')
    else:
        toc = (root/'SOURCE_TOC_MAP.md').read_text(encoding='utf-8-sig')
        if '확인 필요' not in toc:
            # The map may be fully verified; otherwise keep the advisory state explicit.
            pass
        if '각색 회차 연결표' not in toc:
            errors.append('SOURCE_TOC_MAP.md: missing adaptation episode map')
    chapters=sorted((root/'chapters').glob('*/chapter.json'))
    for f in chapters:
        try:
            d=json.loads(f.read_text(encoding='utf-8-sig'))
            if not d.get('id'): errors.append(f'{f}: missing id')
            if not d.get('title'): errors.append(f'{f}: missing title')
            if not (d.get('source_pages') or d.get('sourcePage')):
                errors.append(f'{f}: missing source page mapping')
            for k in ('script','storyboard','explanation'):
                filename=d.get(k, f'{k}.md')
                if not (f.parent/filename).is_file(): errors.append(f'{f}: missing file {filename}')
        except Exception as e: errors.append(f'{f}: {e}')
    # Existing fixed-page art stays available as reference material, but cannot count as a final episode.
    for image in sorted((root/'chapters').glob('*/*.png')):
        try:
            with image.open('rb') as stream:
                header=stream.read(24)
            if header[:8] != b'\x89PNG\r\n\x1a\n':
                legacy_page_drafts.append(f'{image}: invalid PNG header')
                continue
            width,height=struct.unpack('>II',header[16:24])
            legacy_page_drafts.append(f'{image}: {width}x{height} preserved as a legacy page draft')
        except Exception as e:
            legacy_page_drafts.append(f'{image}: image dimension check failed: {e}')

    # Every episode needs ordered scroll slices and a recorded mobile/source/character review.
    for manifest in chapters:
        try:
            data=json.loads(manifest.read_text(encoding='utf-8-sig'))
        except Exception:
            continue
        scroll_dir=manifest.parent/'scroll'
        segments=sorted(p for p in scroll_dir.iterdir() if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp')) if scroll_dir.is_dir() else []
        if len(segments) < 2:
            webtoon_warnings.append(f'{manifest.parent}: needs at least two sequential images in scroll/')
        else:
            expected=[f'{i:03d}' for i in range(1,len(segments)+1)]
            actual=[p.stem for p in segments]
            if actual != expected:
                webtoon_warnings.append(f'{manifest.parent}: scroll images must be named 001, 002, ... without gaps')
        review_file=manifest.parent/'webtoon_review.json'
        try:
            review=json.loads(review_file.read_text(encoding='utf-8-sig'))
            for key in ('mobile_readability','scroll_flow','character_consistency','source_accuracy','naver_export_check'):
                if review.get(key) != 'passed':
                    webtoon_warnings.append(f'{review_file}: {key} review is not passed')
        except Exception:
            webtoon_warnings.append(f'{manifest.parent}: missing valid webtoon_review.json')
        if data.get('format') != 'naver-webtoon-vertical-scroll':
            webtoon_warnings.append(f'{manifest}: format must be naver-webtoon-vertical-scroll')
    return chapters, errors, webtoon_warnings, legacy_page_drafts

if __name__=='__main__':
    chapters, errors, webtoon_warnings, legacy_page_drafts=check()
    ready=not errors and not webtoon_warnings
    print(json.dumps({'chapters':len(chapters),'errors':errors,'format':'Naver Webtoon only','webtoon_ready':ready,'webtoon_warnings':webtoon_warnings,'preserved_draft_assets':legacy_page_drafts,'note':'Legacy art is preserved as draft/reference material; episode completion requires ordered scroll slices and passed reviews. Verify current Naver creator upload requirements before publication.'},ensure_ascii=False))
    raise SystemExit(0 if ready else 1)
