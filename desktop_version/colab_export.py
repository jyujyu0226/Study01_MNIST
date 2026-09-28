# 구글 코랩(https://colab.research.google.com)에서 실행하는 셀: 학습 후 weights.json 다운로드
# 새 노트북을 만들고 이 전체를 한 셀에 붙여넣어 실행하세요. (내 컴퓨터에 설치할 것이 없습니다)
import base64, json
import numpy as np
from tensorflow import keras

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
print("MNIST 테스트 정확도:", model.evaluate(xt, yt, verbose=0)[1])

enc = lambda a: base64.b64encode(np.asarray(a, dtype="<f4").tobytes()).decode()
layers = []
for l in model.layers:
    n = l.__class__.__name__
    if n in ("Conv2D", "Dense"):
        k, b = l.get_weights()
        layers.append({"type": "conv" if n == "Conv2D" else "dense", "shape": list(k.shape),
                       "kernel": enc(k), "bias": enc(b), "activation": l.activation.__name__})
    elif n == "MaxPooling2D":
        layers.append({"type": "pool"})
    elif n == "Flatten":
        layers.append({"type": "flatten"})
json.dump({"format": "mnist-cnn-v1", "layers": layers}, open("weights.json", "w"))

from google.colab import files
files.download("weights.json")
