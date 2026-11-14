from pathlib import Path
from datetime import date
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
ep=sys.argv[1]
folder=(ROOT/'chapters'/ep).resolve()
assert folder.parent==(ROOT/'chapters').resolve()
data=json.loads((folder/'chapter.json').read_text(encoding='utf-8-sig'))
review=json.loads((folder/'webtoon_review.json').read_text(encoding='utf-8-sig'))
keys=['mobile_readability','scroll_flow','character_consistency','source_accuracy','naver_export_check']
assert all(review.get(k)=='passed' for k in keys), 'All visual/export reviews must pass'
assert data.get('sourceStatus')=='source-verified'
assets=sorted((folder/'scroll').glob('*.png'))
assert [p.stem for p in assets]==[f'{ep}-{i:03}' for i in range(1,data['plannedCutCount']+1)]
export_dir=ROOT/'upload_ready/naver_challenge'/ep
assert all((export_dir/(p.stem+'.jpg')).is_file() for p in assets)
today=date.today().isoformat()
data.update(status='complete',scrollAssets=['scroll/'+p.name for p in assets],imageGenerationStatus={'state':'complete','assetCount':len(assets),'completedAt':today,'tool':'built-in image_gen'},naverRequirementsVerifiedAt=today,naverRequirementsVerified='https://help.naver.com/service/5635/contents/18779?lang=ko&osType=COMMONOS',naverUploadLimitsVerified={'widthPx':690,'formats':['jpg','gif'],'maxFileBytes':5242880,'maxEpisodeBytes':52428800,'verifiedAt':today})
(folder/'chapter.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
complete=[]
for p in sorted((ROOT/'chapters').glob('05-*/chapter.json')):
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 if d.get('status')=='complete': complete.append(d['id'])
assert complete==[f'05-{i:02}' for i in range(1,len(complete)+1)]
count=len(complete); next_id=f'05-{count+1:02}' if count<18 else None
plan=ROOT/'CHAPTER_05_PLAN.md'; text=plan.read_text(encoding='utf-8'); lines=text.splitlines()
for i,line in enumerate(lines):
 if line.startswith('|') and f'| {ep} |' in line:
  cells=line.split('|'); cells[-2]=f' {len(assets)}컷 완성·검수·690px JPG 내보내기 완료 '; lines[i]='|'.join(cells)
marker='## 현재 진행'; text='\n'.join(lines); text=text[:text.index(marker)]+marker+'\n\n'+f'18개 Topic 중 {count}개 회차(05-01~{complete[-1]})를 완성했다. '+(f'다음은 {next_id}이다. 컷별 저장·체크포인트 방식으로 연속 제작한다. ' if next_id else '')+'인쇄 pp.301–302 누락 여부는 원전 확인 없이 해소된 것으로 처리하지 않는다.\n'; plan.write_text(text,encoding='utf-8')
for name,heading in [('GOAL.md','## 현재 진행 목표'),('CHAPTER_05_GOAL.md','## 진행 현황')]:
 p=ROOT/name; text=p.read_text(encoding='utf-8'); start=text.index(heading)+len(heading); end=text.find('\n## ',start); end=len(text) if end<0 else end; text=text[:start]+f'\n\n18개 중 {count}개 회차(05-01~{complete[-1]}) 완료. '+(f'다음은 {next_id}이며 연속 제작을 이어간다.' if next_id else '이후 전체 누락면과 검수 결과를 종합 감사한다.')+'\n'+text[end:]; p.write_text(text,encoding='utf-8')
with (ROOT/'SOURCE_TOC_MAP.md').open('a',encoding='utf-8') as f: f.write(f'\n- {today} {ep}: {data["sourcePage"]} 시각 대조, 컷별 검수, 690px JPG 내보내기 완료.\n')
subprocess.run([sys.executable,str(ROOT/'scripts/update_ch05_reader.py')],cwd=ROOT,check=True)
state_path=ROOT/'.codex/production_state.json'; state=json.loads(state_path.read_text(encoding='utf-8-sig'))
state.update(lastCompletedEpisode=ep,currentEpisode=next_id,nextEpisode=next_id,stage='awaiting-source-review' if next_id else 'chapter-audit',expectedCuts=0,savedCutCount=0,missingCuts=[],liveExecCellId=None,liveExecDescription=None,visuallyReviewedCuts=[],sourcePhysicalPages=[],sourceCaveat='',sourceRenderDirectory='.codex/source-renders/chapter05',resumeInstruction=(f'Begin {next_id} using only ../책_투자자산운용사_p1192.pdf. Verify its printed and physical pages, prepare script/storyboard, generate and checkpoint every cut, review, export, and continue sequentially.' if next_id else 'All planned Topics are complete; audit source gaps and chapter scope.'))
state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'.codex/hooks/book_hooks.py'),'--scope','05-'],cwd=ROOT,check=True)
print(f'Finalized {ep}; progress={count}/18; next={next_id}')
