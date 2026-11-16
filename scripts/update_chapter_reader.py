"""Render chapters 06/07 with the existing reader's design and completed art only."""
from pathlib import Path
from html import escape
import argparse
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = {'06': ('파생상품투자운용/투자전략', 19), '07': ('투자운용결과분석', 11)}


def render(chapter):
    title, total = CHAPTERS[chapter]
    plan = (ROOT / f'CHAPTER_{chapter}_PLAN.md').read_text(encoding='utf-8')
    topics = []
    for line in plan.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 5 and re.fullmatch(rf'{chapter}-\d{{2}}', cells[4]):
            topics.append((cells[4], cells[1]))
    assert [ep for ep, _ in topics] == [f'{chapter}-{n:02}' for n in range(1, total + 1)]
    completed = []
    for p in sorted((ROOT / 'chapters').glob(f'{chapter}-*/chapter.json')):
        data = json.loads(p.read_text(encoding='utf-8-sig'))
        if data.get('status') == 'complete':
            completed.append(data)
    assert [d['id'] for d in completed] == [ep for ep, _ in topics[:len(completed)]]
    done = {d['id']: d for d in completed}
    toc, articles = [], []
    for ep, topic in topics:
        text = f'<span class="toc-number">{ep}</span><span>{escape(topic)}</span>'
        if ep in done:
            toc.append(f'<li class="toc-item is-done"><a class="toc-link" href="#episode-{ep}">{text}<span class="toc-status">완성 · 읽기</span></a></li>')
        else:
            toc.append(f'<li class="toc-item"><span class="toc-link">{text}<span class="toc-status">제작 예정</span></span></li>')
    for data in completed:
        ep = data['id']
        folder = ROOT / 'chapters' / ep
        images = []
        for i, asset in enumerate(data['scrollAssets'], 1):
            resolved = (folder / asset).resolve()
            assert resolved.is_relative_to(folder.resolve()) and resolved.is_file(), asset
            with Image.open(resolved) as im: width,height=im.size
            images.append(f'<img src="chapters/{ep}/{escape(asset, quote=True)}" alt="{escape(data["title"], quote=True)} · {i}번째 세로 컷" loading="lazy" width="{width}" height="{height}">')
        prose = (folder / data['explanation']).read_text(encoding='utf-8')
        paragraphs = [p.strip() for p in prose.split('\n\n') if p.strip() and not p.startswith('#')]
        explanation = ''.join('<p>' + escape(p.replace('`', '')) + '</p>' for p in paragraphs)
        articles.append(f'<article class="episode" id="episode-{ep}"><header class="episode-head"><p class="episode-overline">TOPIC {ep[-2:]} · 완성</p><h2>{escape(data["title"])}</h2><p class="source">원전 연결: {escape(data["sourcePage"])}</p></header><div class="comic">' + '\n'.join(images) + f'</div><section class="explanation"><h3>개념 해설</h3>{explanation}</section></article>')
    if len(completed) < total:
        ep = topics[len(completed)][0]
        articles.append(f'<section class="upcoming" id="episode-{ep}"><h2>다음 회차 · {ep}</h2><p>그림과 검토를 마친 회차를 순서대로 추가합니다.</p></section>')
    template = (ROOT / 'book_reader.html').read_text(encoding='utf-8')
    style = re.search(r'<style>(.*?)</style>', template, re.S).group(1)
    style = re.sub(r'(\.progress span\s*\{[^}]*?width:)\s*[^;]+;', rf'\g<1> {len(completed)/total*100:.2f}%;', style)
    page = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} · 만화교과서</title><style>{style}</style></head><body>
<div class="reader"><header class="masthead"><div class="brand">살면서 써먹는 경제 · 투자 만화교과서</div><div class="edition">투자자산운용사 · 제3과목 제{int(chapter)}장</div></header>
<div class="layout"><nav class="toc" aria-label="제{int(chapter)}장 목차"><h2>제{int(chapter)}장 목차</h2><p class="toc-intro">원전 Topic 순서 · 완성 회차만 열립니다</p><ol class="toc-list">{''.join(toc)}</ol></nav>
<main class="book"><header class="cover"><p class="cover-kicker">제{int(chapter)}장 · 세로 스크롤 학습만화</p><h1>{escape(title)}</h1><div class="cover-mark"><div class="progress" aria-label="{total}개 중 {len(completed)}개 완성"><span></span></div><strong>{len(completed)} / {total} 회차</strong></div></header>{''.join(articles)}<footer class="footer">원전과 연결한 세로 스크롤 학습만화</footer></main></div></div></body></html>'''
    ids = re.findall(r'\bid="([^"]+)"', page)
    assert len(ids) == len(set(ids)), 'Duplicate page anchors'
    assert all(anchor in ids for anchor in re.findall(r'href="#([^"]+)"', page))
    return page, len(completed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('chapter', choices=CHAPTERS)
    parser.add_argument('--check', action='store_true', help='Validate without writing a reader')
    args = parser.parse_args()
    page, count = render(args.chapter)
    if not args.check:
        target = ROOT / f'book_reader_{args.chapter}.html'
        target.write_text(page, encoding='utf-8')
        # Keep chapter navigation in the existing design; do not replace chapter 5 art.
        readers = [('05', ROOT / 'book_reader.html')] + [(c, ROOT / f'book_reader_{c}.html') for c in CHAPTERS]
        links = ' · '.join(f'<a href="{p.name}">제{int(c)}장</a>' for c, p in readers if p.is_file())
        nav = f'<p id="chapter-navigation">{links}</p>'
        for _, path in readers:
            if not path.is_file():
                continue
            text = path.read_text(encoding='utf-8')
            if 'id="chapter-navigation"' in text:
                text = re.sub(r'<p id="chapter-navigation">.*?</p>', nav, text)
            else:
                text = text.replace('<div class="reader">', '<div class="reader">' + nav, 1)
            path.write_text(text, encoding='utf-8')
    print(f'Chapter {args.chapter} reader validated: {count}/{CHAPTERS[args.chapter][1]} complete; write={not args.check}')
