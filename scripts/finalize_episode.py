"""Finalize only after the agent records a passed visual review of real PNG/JPG assets."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
ep=sys.argv[1]
assert re.fullmatch(r'(05|06|07)-\d{2}',ep), 'Unsupported episode ID'
chapter=ep.split('-')[0]
total={'05':18,'06':19,'07':11}[chapter]
chapter_label=f'제{int(chapter)}장'
assert 1 <= int(ep[-2:]) <= total
if chapter in {'06','07'}:
    previous=f'{int(chapter)-1:02}'
    previous_total={'05':18,'06':19}[previous]
    previous_done=[]
    for p in sorted((ROOT/'chapters').glob(f'{previous}-*/chapter.json')):
        prior=json.loads(p.read_text(encoding='utf-8-sig'))
        if prior.get('status')=='complete': previous_done.append(prior['id'])
    assert previous_done==[f'{previous}-{n:02}' for n in range(1,previous_total+1)], 'Finish and verify the preceding chapter first'
folder=(ROOT/'chapters'/ep).resolve()
assert folder.parent==(ROOT/'chapters').resolve()
data=json.loads((folder/'chapter.json').read_text(encoding='utf-8-sig'))
review=json.loads((folder/'webtoon_review.json').read_text(encoding='utf-8-sig'))
keys=['mobile_readability','scroll_flow','character_consistency','source_accuracy','naver_export_check']
assert all(review.get(k)=='passed' for k in keys), 'Visual/export reviews must be recorded before completion'
review_date=review.get('reviewedAt')
assert review_date and re.fullmatch(r'\d{4}-\d{2}-\d{2}',review_date), 'Review date is required'
assert data['sourceStatus']=='source-verified'
assets=sorted((folder/'scroll').glob('*.png'))
assert [p.stem for p in assets]==[f'{ep}-{i:03}' for i in range(1,data['plannedCutCount']+1)]
assert all((ROOT/'upload_ready/naver_challenge'/ep/(p.stem+'.jpg')).is_file() for p in assets)
complete=[]
for p in sorted((ROOT/'chapters').glob(f'{chapter}-*/chapter.json')):
    d=json.loads(p.read_text(encoding='utf-8-sig'))
    if d.get('status')=='complete' or d['id']==ep: complete.append(d['id'])
assert complete==[f'{chapter}-{i:02}' for i in range(1,len(complete)+1)], 'Completed episodes must be sequential'
data.update(status='complete',scrollAssets=['scroll/'+p.name for p in assets],imageGenerationStatus={'state':'complete','assetCount':len(assets),'completedAt':review_date,'tool':'built-in image_gen'},naverRequirementsVerifiedAt=review_date,naverRequirementsVerified='https://help.naver.com/service/5635/contents/18779?lang=ko&osType=COMMONOS',naverUploadLimitsVerified={'widthPx':690,'formats':['jpg','gif'],'maxFileBytes':5242880,'maxEpisodeBytes':52428800,'verifiedAt':review_date})
(folder/'chapter.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
count=len(complete)
next_id=f'{chapter}-{count+1:02}' if count<total else None
plan=ROOT/f'CHAPTER_{chapter}_PLAN.md'
text=plan.read_text(encoding='utf-8')
lines=text.splitlines()
for i,line in enumerate(lines):
    if line.startswith('|') and f'| {ep} |' in line:
        parts=line.split('|')
        parts[-2]=f' {len(assets)}컷 완성·원전/캐릭터/모바일 검토·690px JPG 내보내기 완료 '
        lines[i]='|'.join(parts)
text='\n'.join(lines)
supplements=ROOT/'sources/supplements/chapter05/manifest.json'
source_note=('사용자 보완 인쇄 pp.301–302는 sources/supplements/chapter05/manifest.json에 별도 출처로 기록했다.' if supplements.is_file() else '인쇄 pp.301–302 누락 의심은 원전 확인 없이 해소된 것으로 처리하지 않는다.') if chapter=='05' else '현재 원전 파일과 물리 쪽수는 각 회차의 출처 기록을 따른다.'
heading='## 현재 진행'
start=text.find(heading)
if start<0:
    text+='\n'+heading+'\n'
    start=text.index(heading)
end=text.find('\n## ',start+len(heading))
if end<0: end=len(text)
text=text[:start]+heading+'\n\n'+f'{total}개 Topic 중 {count}개 회차({chapter}-01~{complete[-1]})를 완성했다. '+(f'다음은 {next_id}이다. ' if next_id else '')+source_note+'\n'+text[end:]
plan.write_text(text,encoding='utf-8')
for name,heading in [('GOAL.md','## 현재 진행 목표'),(f'CHAPTER_{chapter}_GOAL.md','## 진행 현황')]:
    p=ROOT/name
    text=p.read_text(encoding='utf-8')
    if heading not in text: text+='\n'+heading+'\n'
    start=text.index(heading)+len(heading)
    end=text.find('\n## ',start)
    if end<0: end=len(text)
    progress=f'\n\n{chapter_label} {total}개 중 {count}회차({chapter}-01~{complete[-1]}) 완료. '+(f'다음은 {next_id}. 자동 제작 목표를 유지한다.' if next_id else '장 전체 산출물을 감사한 뒤 다음 장으로 이어간다. 제7장까지의 전체 목표는 유지한다.')+'\n'
    text=text[:start]+progress+text[end:]
    if name=='GOAL.md' and chapter=='05':
        text=re.sub(r'원전 18개 Topic;[^\)]*\)',f'원전 18개 Topic; 05-01~{complete[-1]} 완료'+(f', 다음 {next_id})' if next_id else ')'),text)
    p.write_text(text,encoding='utf-8')
with (ROOT/'SOURCE_TOC_MAP.md').open('a',encoding='utf-8') as stream:
    stream.write(f'\n- {review_date} {ep}: {data["sourcePage"]} 시각 대조. 세로 {len(assets)}컷·690px JPG·검토 기록 완성.\n')
reader_args=[str(ROOT/'scripts/update_ch05_reader.py')] if chapter=='05' else [str(ROOT/'scripts/update_chapter_reader.py'),chapter]
subprocess.run([sys.executable,*reader_args],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/'.codex/hooks/book_hooks.py'),'--scope',chapter+'-'],cwd=ROOT,check=True)
print(f'Finalized {ep}; progress={count}/{total}; next={next_id}')
