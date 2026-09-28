#!/usr/bin/env python3
"""MNIST 손글씨 숫자 인식 - 데스크톱 버전 (tkinter + TensorFlow/Keras)

학번 2601965 이름 이승주

실행:  pip install tensorflow pillow numpy
       python app.py
처음 실행하면 MNIST로 CNN을 학습해 mnist_model.keras로 저장하고,
이후에는 저장된 모델을 바로 불러옵니다.
"""
import importlib
import os
import subprocess
import sys
import threading
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
for _n in ("stdout", "stderr"):  # pythonw(검은 창 없음)에서는 None이라 대비
    if getattr(sys, _n) is None:
        setattr(sys, _n, open(os.devnull, "w"))


def ensure_packages():
    """필요한 라이브러리가 없으면 자동으로 설치한다 (더블클릭 실행용)."""
    need = {"numpy": "numpy", "PIL": "pillow", "tensorflow": "tensorflow"}
    missing = []
    for mod, pkg in need.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("필요한 라이브러리를 설치합니다:", ", ".join(missing), "(몇 분 걸릴 수 있어요)")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing], creationflags=flags)


def report_error():
    """오류가 나도 창이 그냥 사라지지 않도록 화면과 error.log에 남긴다."""
    msg = traceback.format_exc()
    with open(os.path.join(HERE, "error.log"), "w", encoding="utf-8") as f:
        f.write(msg)
    print(msg)
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk()
        r.withdraw()
        messagebox.showerror("실행 오류", msg[-800:])
    except Exception:
        pass
    try:
        input("오류가 났어요. Enter를 누르면 닫힙니다.")
    except Exception:
        pass


try:
    ensure_packages()
    import tkinter as tk

    import numpy as np
    from PIL import Image, ImageDraw
except Exception:
    report_error()
    sys.exit(1)

MODEL_PATH = os.path.join(HERE, "mnist_model.keras")
SIZE, PEN = 280, 22


def build_or_load_model():
    from tensorflow import keras
    if os.path.exists(MODEL_PATH):
        return keras.models.load_model(MODEL_PATH)
    (x, y), (xt, yt) = keras.datasets.mnist.load_data()
    x = x[..., None].astype("float32") / 255
    xt = xt[..., None].astype("float32") / 255
    model = keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(32, 3, activation="relu"), keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(64, 3, activation="relu"), keras.layers.MaxPooling2D(),
        keras.layers.Flatten(), keras.layers.Dropout(0.3),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
    model.fit(x, y, epochs=6, batch_size=128, validation_data=(xt, yt), verbose=2)
    model.save(MODEL_PATH)
    return model


def preprocess(img):
    """280x280 흑백 이미지(흰 글씨) -> MNIST 형식 (1,28,28,1). 글씨가 없으면 None."""
    a = np.array(img)
    ys, xs = np.where(a > 40)
    if len(xs) == 0:
        return None
    crop = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w, h = crop.size
    s = 20 / max(w, h)
    crop = crop.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    canvas = Image.new("L", (28, 28), 0)
    canvas.paste(crop, ((28 - crop.width) // 2, (28 - crop.height) // 2))
    arr = np.array(canvas, dtype="float32")
    m = arr.sum()
    cy, cx = (np.indices(arr.shape) * arr).sum(axis=(1, 2)) / m
    arr = np.roll(arr, (round(13.5 - cy), round(13.5 - cx)), axis=(0, 1))  # 무게중심을 중앙으로
    return (arr / 255).reshape(1, 28, 28, 1)


class App:
    def __init__(self, root):
        self.root, self.model = root, None
        root.title("MNIST 손글씨 숫자 인식")
        try:
            root.iconbitmap(os.path.join(HERE, "icon.ico"))
        except Exception:
            pass
        tk.Label(root, text="학번 2601965 이름 이승주", bg="#1e3a8a", fg="white",
                 font=("Malgun Gothic", 14, "bold"), pady=8).pack(fill="x")
        self.status = tk.Label(root, text="모델 준비 중... (처음엔 학습 때문에 1~2분 걸려요)")
        self.status.pack(pady=4)
        self.cv = tk.Canvas(root, width=SIZE, height=SIZE, bg="black", cursor="crosshair")
        self.cv.pack(padx=10)
        self.img = Image.new("L", (SIZE, SIZE), 0)
        self.draw = ImageDraw.Draw(self.img)
        self.last = None
        self.cv.bind("<ButtonPress-1>", self.down)
        self.cv.bind("<B1-Motion>", self.move)
        self.cv.bind("<ButtonRelease-1>", self.up)
        bar = tk.Frame(root)
        bar.pack(pady=6)
        tk.Button(bar, text="지우기", command=self.clear).pack(side="left", padx=4)
        tk.Button(bar, text="인식하기", command=self.predict).pack(side="left", padx=4)
        self.result = tk.Label(root, text="?", font=("Arial", 48, "bold"))
        self.result.pack()
        self.detail = tk.Label(root, text="", font=("Consolas", 9), justify="left")
        self.detail.pack(pady=(0, 8))
        threading.Thread(target=self.load, daemon=True).start()

    def load(self):
        try:
            self.model = build_or_load_model()
            self.root.after(0, lambda: self.status.config(text="준비 완료! 숫자를 그려보세요."))
        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"모델 준비 실패: {e}"))

    def down(self, e):
        self.last = (e.x, e.y)
        self.stroke(e.x, e.y, e.x, e.y)

    def move(self, e):
        self.stroke(*self.last, e.x, e.y)
        self.last = (e.x, e.y)

    def up(self, _):
        self.last = None
        self.root.after(150, self.predict)

    def stroke(self, x0, y0, x1, y1):
        r = PEN // 2
        self.cv.create_line(x0, y0, x1, y1, fill="white", width=PEN, capstyle="round")
        self.cv.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, fill="white", outline="white")
        self.draw.line((x0, y0, x1, y1), fill=255, width=PEN)
        self.draw.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=255)

    def clear(self):
        self.cv.delete("all")
        self.draw.rectangle((0, 0, SIZE, SIZE), fill=0)
        self.result.config(text="?")
        self.detail.config(text="")

    def predict(self):
        if self.model is None:
            return
        x = preprocess(self.img)
        if x is None:
            return
        p = self.model.predict(x, verbose=0)[0]
        self.result.config(text=str(int(p.argmax())))
        self.detail.config(text="\n".join(f"{i}: {v * 100:5.1f}%" for i, v in enumerate(p)))


if __name__ == "__main__":
    try:
        if "--prepare" in sys.argv:  # 바로가기 만들 때 모델을 미리 학습해 둔다
            build_or_load_model()
            sys.exit(0)
        if sys.platform == "win32":  # 작업 표시줄에서 파이썬이 아닌 이 앱의 아이콘으로 묶이게 함
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SeungjuLee.MNISTDigit.1")
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        report_error()
