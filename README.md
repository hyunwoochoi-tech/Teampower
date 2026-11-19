# 팀파워 레크레이션 (Render 배포용)

포스코 사내망(사회자 PC) + 참여자 휴대폰(LTE/5G) 실시간 멀티플레이어 웹 게임입니다.
외부 CDN 의존성 없이 Render 단일 서버에서 화면, QR 코드, 실시간 WebSocket 통신을 모두 처리합니다.

## 모바일에서 3분 배포 방법
1. GitHub (크롬 데스크톱 사이트 모드)에서 새 저장소 생성 후 이 폴더 안의 파일들을 모두 업로드합니다.
   - `main.py`
   - `index.html`
   - `requirements.txt`
   - `render.yaml`
2. Render Dashboard (`https://dashboard.render.com`) -> `New +` -> `Blueprint` 선택
3. 방금 만든 GitHub 저장소 연결 후 `Apply` 클릭
4. 배포 완료 후 생성된 `https://xxxx.onrender.com` 주소로 회사 PC에서 접속!

## 행사 당일 팁
- Render 무료 플랜은 15분 미사용 시 절전 모드가 됩니다. 행사 시작 5분 전에 미리 접속해 두세요.
