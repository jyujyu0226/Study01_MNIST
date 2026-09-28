/* 순수 자바스크립트 CNN 추론 엔진 (외부 라이브러리 없음)
 * weights.json(레이어 목록 + base64 float32 가중치)을 읽어 conv → pool → flatten → dense 순서로 계산한다. */
(function (root) {
  function b64f32(s) {
    const bin = atob(s), u = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return new Float32Array(u.buffer);
  }
  function load(spec) {
    return spec.layers.map(l => {
      const o = Object.assign({}, l);
      if (l.kernel) o.kernel = b64f32(l.kernel);
      if (l.bias) o.bias = b64f32(l.bias);
      return o;
    });
  }
  function conv(t, L) {                       // valid padding, stride 1, 커널 모양 (kh,kw,cin,cout)
    const [kh, kw, cin, cout] = L.shape, oh = t.h - kh + 1, ow = t.w - kw + 1;
    const out = new Float32Array(oh * ow * cout), K = L.kernel;
    for (let y = 0; y < oh; y++) for (let x = 0; x < ow; x++) {
      const base = (y * ow + x) * cout;
      for (let o = 0; o < cout; o++) out[base + o] = L.bias[o];
      for (let ky = 0; ky < kh; ky++) for (let kx = 0; kx < kw; kx++) for (let ci = 0; ci < cin; ci++) {
        const v = t.data[((y + ky) * t.w + (x + kx)) * cin + ci], kb = ((ky * kw + kx) * cin + ci) * cout;
        for (let o = 0; o < cout; o++) out[base + o] += v * K[kb + o];
      }
    }
    if (L.activation === 'relu') for (let i = 0; i < out.length; i++) if (out[i] < 0) out[i] = 0;
    return { data: out, h: oh, w: ow, c: cout };
  }
  function pool(t) {                          // 2x2 max pooling, stride 2
    const oh = t.h >> 1, ow = t.w >> 1, out = new Float32Array(oh * ow * t.c);
    for (let y = 0; y < oh; y++) for (let x = 0; x < ow; x++) for (let c = 0; c < t.c; c++) {
      let m = -Infinity;
      for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
        const v = t.data[((2 * y + dy) * t.w + (2 * x + dx)) * t.c + c];
        if (v > m) m = v;
      }
      out[(y * ow + x) * t.c + c] = m;
    }
    return { data: out, h: oh, w: ow, c: t.c };
  }
  function dense(t, L) {
    const [nin, nout] = L.shape, out = new Float32Array(nout), x = t.data;
    for (let j = 0; j < nout; j++) out[j] = L.bias[j];
    for (let i = 0; i < nin; i++) { const v = x[i], b = i * nout; if (v !== 0) for (let j = 0; j < nout; j++) out[j] += v * L.kernel[b + j]; }
    if (L.activation === 'relu') for (let j = 0; j < nout; j++) if (out[j] < 0) out[j] = 0;
    if (L.activation === 'softmax') {
      let m = -Infinity; for (const v of out) if (v > m) m = v;
      let s = 0; for (let j = 0; j < nout; j++) { out[j] = Math.exp(out[j] - m); s += out[j]; }
      for (let j = 0; j < nout; j++) out[j] /= s;
    }
    return { data: out, h: 1, w: 1, c: nout };
  }
  function predict(net, pixels) {             // pixels: 길이 784, 0~1, 흰 글씨(검은 배경)
    let t = { data: pixels, h: 28, w: 28, c: 1 };
    for (const L of net) {
      if (L.type === 'conv') t = conv(t, L);
      else if (L.type === 'pool') t = pool(t);
      else if (L.type === 'flatten') t = { data: t.data, h: 1, w: 1, c: t.data.length };
      else if (L.type === 'dense') t = dense(t, L);
    }
    return t.data;
  }
  const api = { load, predict };
  if (typeof module !== 'undefined') module.exports = api; else root.MNISTNet = api;
})(this);
