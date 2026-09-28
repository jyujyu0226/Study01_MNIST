# Study01_MNIST
MNIST 손글씨 숫자 인식 프로젝트. 웹 버전과 데스크톱 버전으로 나누어 개발한다.

## 구조
- `index.html`: GitHub Pages 루트 진입 페이지. `web_version/`으로 이동시킨다 (학번·이름 표시).
- `web_version/`: 순수 자바스크립트 추론, GitHub Pages 정적 배포용. 자세한 규칙은 `web_version/CLAUDE.md`.
- `desktop_version/`: tkinter + TensorFlow/Keras 데스크톱 앱과 학습·내보내기 코드. 자세한 규칙은 `desktop_version/CLAUDE.md`.
- `CLAUDE_전역.md`: 공통 작업 지침.

## 규칙
- 웹 페이지 화면 맨 위에 `학번 2601965 이름 이승주`가 보여야 한다 (README·주석만으로는 안 됨).
- 모델은 `desktop_version`에서 학습하고, `export_weights.py`로 `web_version/weights.json`을 만든다.
- 제출 마감 후에는 푸시하지 않는다.
