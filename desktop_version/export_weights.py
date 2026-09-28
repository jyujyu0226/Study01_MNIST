"""학습된 Keras 모델을 웹 버전용 weights.json으로 내보낸다.

실행:  python export_weights.py
결과:  ../web_version/weights.json  (순수 자바스크립트가 읽는 base64 float32 가중치)
"""
import base64
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from app import build_or_load_model  # 모델이 없으면 학습, 있으면 불러오기


def enc(a):
    return base64.b64encode(np.asarray(a, dtype="<f4").tobytes()).decode()


def main():
    model = build_or_load_model()
    layers = []
    for l in model.layers:
        n = l.__class__.__name__
        if n == "Conv2D":
            k, b = l.get_weights()
            layers.append({"type": "conv", "shape": list(k.shape), "kernel": enc(k), "bias": enc(b),
                           "activation": l.activation.__name__})
        elif n == "Dense":
            k, b = l.get_weights()
            layers.append({"type": "dense", "shape": list(k.shape), "kernel": enc(k), "bias": enc(b),
                           "activation": l.activation.__name__})
        elif n == "MaxPooling2D":
            layers.append({"type": "pool"})
        elif n == "Flatten":
            layers.append({"type": "flatten"})
        elif n in ("Dropout", "InputLayer"):
            continue
        else:
            raise ValueError("지원하지 않는 레이어: " + n)
    out = os.path.join(HERE, "..", "web_version", "weights.json")
    with open(out, "w") as f:
        json.dump({"format": "mnist-cnn-v1", "layers": layers}, f)
    print("저장 완료:", os.path.abspath(out), f"({os.path.getsize(out) / 1e6:.1f} MB)")
    try:
        from tensorflow import keras
        _, (xt, yt) = keras.datasets.mnist.load_data()
        acc = (model.predict(xt[..., None].astype("float32") / 255, verbose=0).argmax(1) == yt).mean()
        print(f"MNIST 테스트 정확도: {acc * 100:.2f}%")
    except Exception as e:
        print("정확도 확인 생략:", e)


if __name__ == "__main__":
    try:
        main()
    except BaseException:  # 더블클릭으로 실행해도 오류 문구를 읽을 수 있게 창을 붙잡아 둔다
        import traceback
        traceback.print_exc()
    try:
        input("\n끝났습니다. Enter를 누르면 창이 닫힙니다.")
    except Exception:
        pass
