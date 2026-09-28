# desktop_version
tkinter + TensorFlow/Keras로 만든 데스크톱 손글씨 인식 앱과 모델 학습 코드.

## 파일
- `app.py`: 앱 본체. 첫 실행 때 CNN을 학습해 `mnist_model.keras`로 저장하고 이후엔 불러온다. 창 맨 위에 학번·이름 표시.
- `export_weights.py`: 학습된 모델을 `../web_version/weights.json`으로 내보낸다 (`python export_weights.py`).
- `make_shortcut.bat` / `make_shortcut.ps1`: 윈도우 바탕 화면 바로가기 생성 (pythonw로 검은 창 없이 실행, `icon.ico` 사용).
- `실행.command`: 맥에서 Finder 더블클릭 실행용.

## 규칙
- 모델 구조를 바꾸면 웹 버전과 호환되도록 Conv2D, MaxPooling2D, Flatten, Dense, Dropout만 사용한다.
- 실행: `pip install tensorflow pillow numpy` 후 `python app.py`.
