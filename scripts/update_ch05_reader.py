from pathlib import Path
from html import escape
import json
import re

root = Path(__file__).resolve().parents[1]
path = root / 'book_reader.html'
text = path.read_text(encoding='utf-8')
completed = []
for p in sorted((root / 'chapters').glob('05-*/chapter.json')):
    data = json.loads(p.read_text(encoding='utf-8-sig'))
    if data.get('status') == 'complete':
        completed.append(data)
for data in completed:
    ep = data['id']
    pattern = r'<li class="toc-item[^\"]*">.*?<span class="toc-number">' + re.escape(ep) + r'</span>.*?</li>'
    item = f'<li class="toc-item is-done"><a class="toc-link" href="#episode-{ep}"><span class="toc-number">{ep}</span><span>{escape(data["title"])}</span><span class="toc-status">완성 · 읽기</span></a></li>'
    text = re.sub(pattern, item, text)
articles = []
for data in completed:
    ep = data['id']
    if ep == '05-01':
        continue  # Preserve the original edited first episode.
    folder = root / 'chapters' / ep
    images = '\n'.join(f'<img src="chapters/{ep}/{escape(asset)}" alt="{escape(data["title"])} · {i}번째 세로 컷" loading="lazy">' for i, asset in enumerate(data['scrollAssets'], 1))
    explanation = (folder / 'explanation.md').read_text(encoding='utf-8')
    paragraphs = [p.strip() for p in explanation.split('\n\n') if p.strip() and not p.startswith('#')]
    prose = '\n'.join('<p>' + escape(p.replace('`', '')) + '</p>' for p in paragraphs)
    articles.append(f'''<article class="episode" id="episode-{ep}">
<header class="episode-head"><p class="episode-overline">TOPIC {ep[-2:]} · 完成</p><h2>{escape(data['title'])}</h2><p class="source">원전 연결: {escape(data['sourcePage'])}</p></header>
<div class="comic" aria-label="{ep} 세로 스크롤 만화">{images}</div>
<section class="explanation"><h3>개념 해설</h3>{prose}</section></article>'''.replace('完成', '완성'))
start = text.index('<article class="episode" id="episode-05-02">') if '<article class="episode" id="episode-05-02">' in text else text.index('<section class="upcoming"')
end = text.index('<footer class="footer">', start)
next_number = len(completed) + 1
next_id = f'05-{next_number:02}'
upcoming = f'<section class="upcoming" id="episode-{next_id}"><h2>다음 회차 · {next_id}</h2><p>원전 순서대로 제작하고 있습니다. 그림과 검토를 마친 회차를 이 화면에 추가합니다.</p></section>' if len(completed) < 18 else ''
text = text[:start] + '\n'.join(articles) + upcoming + '\n' + text[end:]
text = re.sub(r'aria-label="18개 중 \d+개 완성"', f'aria-label="18개 중 {len(completed)}개 완성"', text)
text = re.sub(r'<strong>\d+ / 18 회차</strong>', f'<strong>{len(completed)} / 18 회차</strong>', text)
text = re.sub(r'(\.progress span\s*\{[^}]*?width:)\s*[^;]+;', rf'\g<1> {len(completed)/18*100:.2f}%;', text)
path.write_text(text, encoding='utf-8')
# Validate all locally referenced images and in-page links.
for asset in re.findall(r'<img[^>]+src="([^"]+)"', text):
    assert (root / asset).is_file(), asset
ids = re.findall(r'\bid="([^"]+)"', text)
assert len(ids) == len(set(ids)), 'Duplicate page anchor'
for anchor in re.findall(r'href="#([^"]+)"', text):
    assert anchor in ids, anchor
print(f'Reader contains {len(completed)} complete episodes with valid image paths and anchors')
