# 네이버웹툰 도전만화 업로드용 내보내기

원본 PNG 세로 컷은 `chapters/<episode-id>/scroll/`에 보존하고, 업로드용 JPG는 이 폴더 아래 회차별 폴더에 만든다.

- 가로 690px, JPG 형식
- 파일당 5MB 이하, 회차별 총 용량 50MB 이하
- 컷 파일명은 `장-토픽-순번` 형식을 유지한다.
- 원본 그림은 업로드용 파일로 덮어쓰지 않는다.

2026-11-12 확인한 [네이버웹툰 고객센터: 도전만화 등록 방법](https://help.naver.com/service/5635/contents/18779?osType=COMMONOS&ostype=commonos)에 따른다. 컷별 크기와 용량은 `NAVER_EXPORT_MANIFEST.csv`에 기록한다. 이 패키지는 파일 규격 검토를 마친 상태이며, 플랫폼에 실제 게시한 것은 아니다.
