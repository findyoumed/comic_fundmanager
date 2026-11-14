"""Prepare and export episodes from their reviewed production specification."""
from pathlib import Path
import argparse
import csv
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
COMMON = ('Use case: illustration-story. Finished Korean vertical-scroll educational webtoon, portrait 1024x1536. '
          'Approved reference is character identity and warm hand-drawn ink/watercolor art style ONLY, never copy its text. '
          'Sister: long low ponytail, beige jacket, black top, brown wide pants, NO freckles. '
          'Boy: short stocky body, spiky brown-black hair, thick eyebrows, orange hoodie, dark cargo pants. '
          'Girl: short bob, freckles, half-lidded eyes, cream shirt, teal overalls. '
          '2-4 spacious vertically stacked scenes with clear gutters, large accurate Korean lettering legible at phone width. '
          'No chapter labels, episode IDs, watermarks, speaker name prefixes, production instructions, or invented numbers. '
          'All economic arrows and visual metaphors must agree with labels; no guaranteed returns. ')


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def prepare(folder):
    spec = json.loads((folder/'production.json').read_text(encoding='utf-8-sig'))
    assert not (folder/'chapter.json').exists(), 'Existing episode must be edited explicitly'
    (folder/'scroll').mkdir(exist_ok=True)
    lines = [f'# {spec["id"]} {spec["title"]}', '', '## 학습 목표', '', spec['goal'], '', '## 이야기 갈등', '', spec['conflict'], '', '## 원전 확인', '', spec['sourceDetails'], '']
    board = [f'# {spec["id"]} 세로 스크롤 콘티', '']
    prompts = []
    for i, cut in enumerate(spec['cuts'], 1):
        cut_id = f'{spec["id"]}-{i:03}'
        lines += [f'### {cut_id}.png — {cut["title"]}', '- 원전: '+cut['source'], '- 장면: '+cut['scene']]
        lines += ['- '+d['speaker']+': “'+d['text']+'”' for d in cut.get('dialogue', [])]
        lines += ['- 표시 문구: '+x for x in cut.get('labels', [])]+['']
        board += [f'{i:02}. {cut["title"]}', cut['scene'], '']
        dialogue = ' '.join('Bubble spoken by '+d['speaker']+' (DO NOT render speaker name): '+json.dumps(d['text'],ensure_ascii=False)+'.' for d in cut.get('dialogue', []))
        prompt = COMMON + 'Scene: '+cut['scene']+'. '+dialogue+' Exact caption/diagram labels: '+json.dumps(cut.get('labels',[]),ensure_ascii=False)+'. '
        prompt += ('First cut title: '+json.dumps(cut['title'],ensure_ascii=False)+'. ' if i==1 else 'No episode title banner. ')
        prompt += cut.get('constraints','')
        prompts.append({'cut':cut_id,'prompt':prompt})
    (folder/'script.md').write_text('\n'.join(lines),encoding='utf-8')
    (folder/'storyboard.md').write_text('\n'.join(board),encoding='utf-8')
    (folder/'explanation.md').write_text(spec['explanation']+'\n',encoding='utf-8')
    write_json(folder/'image_prompts.json',prompts)
    (folder/'image_prompts.md').write_text('# 이미지 프롬프트\n\n내장 image_gen 사용. 승인 참조 chapters/14/014.png. 전체 컷별 프롬프트는 image_prompts.json에 보관한다.\n',encoding='utf-8')
    data = {k:spec[k] for k in ['id','title','sourceChapter','sourceTopic','sourcePage','sourceDetails']}
    data.update(sourceStatus='source-verified',format='naver-webtoon-vertical-scroll',episodeGoal=spec['goal'],script='script.md',storyboard='storyboard.md',explanation='explanation.md',imagePrompts='image_prompts.md',status='script-ready-art-pending',plannedCutCount=len(prompts),scrollAssets=[],review='webtoon_review.json',exportDirectory=f'../../upload_ready/naver_challenge/{spec["id"]}',exportManifest='../../upload_ready/NAVER_EXPORT_MANIFEST.csv')
    write_json(folder/'chapter.json',data)
    write_json(folder/'webtoon_review.json',{**{k:'pending' for k in ['mobile_readability','scroll_flow','character_consistency','source_accuracy','naver_export_check']},'notes':'원전 시각 대조와 대본·콘티 확정. 그림 검토 전.'})
    print(f'Prepared {spec["id"]}: {len(prompts)} cuts')


def export(folder):
    data = json.loads((folder/'chapter.json').read_text(encoding='utf-8-sig'))
    ep = data['id']
    files = sorted((folder/'scroll').glob('*.png'))
    assert [p.stem for p in files] == [f'{ep}-{i:03}' for i in range(1,data['plannedCutCount']+1)], 'Incomplete or unordered masters'
    dest = ROOT/'upload_ready/naver_challenge'/ep
    dest.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in files:
        im=Image.open(p).convert('RGB')
        im=im.resize((690,round(im.height*690/im.width)),Image.Resampling.LANCZOS)
        target=dest/(p.stem+'.jpg')
        im.save(target,'JPEG',quality=90,optimize=True,progressive=True)
        rows.append(dict(episode=ep,filename=target.name,width_px=im.width,height_px=im.height,bytes=target.stat().st_size))
    assert all(r['bytes']<5242880 for r in rows) and sum(r['bytes'] for r in rows)<52428800
    manifest=ROOT/'upload_ready/NAVER_EXPORT_MANIFEST.csv'
    old=list(csv.DictReader(manifest.open(encoding='utf-8-sig',newline='')))
    with manifest.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['episode','filename','width_px','height_px','bytes'],quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows([r for r in old if r['episode']!=ep]+rows)
    print(json.dumps({'episode':ep,'files':len(rows),'bytes':sum(r['bytes'] for r in rows)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('operation',choices=['prepare','export'])
    parser.add_argument('episode')
    args=parser.parse_args()
    folder=(ROOT/'chapters'/args.episode).resolve()
    assert folder.parent == (ROOT/'chapters').resolve(), 'Invalid episode path'
    {'prepare':prepare,'export':export}[args.operation](folder)
