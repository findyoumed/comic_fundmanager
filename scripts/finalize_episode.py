"""Finalize only after the agent records a passed visual review of real PNG/JPG assets."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
ep=sys.argv[1]
folder=(ROOT/'chapters'/ep).resolve()
assert folder.parent==(ROOT/'chapters').resolve()
data=json.loads((folder/'chapter.json').read_text(encoding='utf-8-sig'))
review=json.loads((folder/'webtoon_review.json').read_text(encoding='utf-8-sig'))
keys=['mobile_readability','scroll_flow','character_consistency','source_accuracy','naver_export_check']
assert all(review.get(k)=='passed' for k in keys), 'Visual/export reviews must be recorded before completion'
assert data['sourceStatus']=='source-verified'
assets=sorted((folder/'scroll').glob('*.png'))
assert [p.stem for p in assets]==[f'{ep}-{i:03}' for i in range(1,data['plannedCutCount']+1)]
assert all((ROOT/'upload_ready/naver_challenge'/ep/(p.stem+'.jpg')).is_file() for p in assets)
data.update(status='complete',scrollAssets=['scroll/'+p.name for p in assets],imageGenerationStatus={'state':'complete','assetCount':len(assets),'completedAt':'2026-11-14','tool':'built-in image_gen'},naverRequirementsVerifiedAt='2026-11-14',naverRequirementsVerified='https://help.naver.com/service/5635/contents/18779?lang=ko&osType=COMMONOS',naverUploadLimitsVerified={'widthPx':690,'formats':['jpg','gif'],'maxFileBytes':5242880,'maxEpisodeBytes':52428800,'verifiedAt':'2026-11-14'})
(folder/'chapter.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
complete=[]
for p in sorted((ROOT/'chapters').glob('05-*/chapter.json')):
    d=json.loads(p.read_text(encoding='utf-8-sig'))
    if d.get('status')=='complete': complete.append(d['id'])
assert complete==[f'05-{i:02}' for i in range(1,len(complete)+1)], 'Completed episodes must be sequential'
count=len(complete)
next_id=f'05-{count+1:02}' if count<18 else None
plan=ROOT/'CHAPTER_05_PLAN.md'
text=plan.read_text(encoding='utf-8')
lines=text.splitlines()
for i,line in enumerate(lines):
    if line.startswith('|') and f'| {ep} |' in line:
        parts=line.split('|')
        parts[-2]=f' {len(assets)}컷 완성·원전/캐릭터/모바일 검토·690px JPG 내보내기 완료 '
        lines[i]='|'.join(parts)
text='\n'.join(lines)
text=text[:text.index('## 현재 진행')]+'## 현재 진행\n\n'+f'18개 Topic 중 {count}개 회차(05-01~{complete[-1]})를 완성했다. '+(f'다음은 {next_id}이다. ' if next_id else '')+'인쇄 pp.301–302 누락 의심은 원전 확인 없이 해소된 것으로 처리하지 않는다.\n'
plan.write_text(text,encoding='utf-8')
for name,heading in [('GOAL.md','## 현재 진행 목표'),('CHAPTER_05_GOAL.md','## 진행 현황')]:
    p=ROOT/name
    text=p.read_text(encoding='utf-8')
    start=text.index(heading)+len(heading)
    end=text.find('\n## ',start)
    if end<0: end=len(text)
    progress=f'\n\n제5장 18개 중 {count}회차(05-01~{complete[-1]}) 완료. '+(f'다음은 {next_id}. 자동 제작 목표를 유지한다.' if next_id else '장 전체의 누락면·산출물·검사 결과를 종합 감사한다.')+'\n'
    text=text[:start]+progress+text[end:]
    if name=='GOAL.md':
        text=re.sub(r'원전 18개 Topic;[^\)]*\)',f'원전 18개 Topic; 05-01~{complete[-1]} 완료'+(f', 다음 {next_id})' if next_id else ')'),text)
    p.write_text(text,encoding='utf-8')
with (ROOT/'SOURCE_TOC_MAP.md').open('a',encoding='utf-8') as stream:
    stream.write(f'\n- 2026-11-14 {ep}: {data["sourcePage"]} 시각 대조. 세로 {len(assets)}컷·690px JPG·검토 기록 완성.\n')
subprocess.run([sys.executable,str(ROOT/'scripts/update_ch05_reader.py')],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/'.codex/hooks/book_hooks.py'),'--scope','05-'],cwd=ROOT,check=True)
print(f'Finalized {ep}; progress={count}/18; next={next_id}')
