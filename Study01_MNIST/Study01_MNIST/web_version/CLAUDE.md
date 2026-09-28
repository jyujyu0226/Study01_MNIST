# web_version
GitHub Pages에 정적으로 올리는 손글씨 인식 웹앱.

## 제약
- 외부 라이브러리·CDN·서버 금지. 순수 HTML/CSS/JavaScript만 사용한다.
- 추론은 `infer.js`(순수 JS CNN 엔진)가 `weights.json`을 읽어 수행한다. 학습은 하지 않는다.
- 빌드 과정이 없어야 하며, 파일은 모두 상대 경로로 참조한다.

## 파일
- `index.html`: UI(캔버스, 전처리, 결과 막대). 맨 위에 학번·이름 표시.
- `infer.js`: conv → maxpool → flatten → dense 추론. 브라우저와 Node 양쪽에서 동작.
- `weights.json`: `desktop_version/export_weights.py`가 생성하는 가중치(base64 float32). 없으면 앱이 동작하지 않는다.

## 확인 방법
- 파일 더블클릭(`file://`)으로는 `fetch`가 막히므로, 배포 주소나 `python -m http.server`로 연다.
- 모델 구조를 바꾸면 `export_weights.py`를 다시 실행하고, `infer.js`가 그 레이어를 지원하는지 확인한다.
