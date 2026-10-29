// Daily News frame engine: the whole video is one page whose state is a pure function of time.
// window.setTime(t) puts every element into its state at t seconds.
(function () {
  function bez(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = t => ((ax * t + bx) * t + cx) * t, sy = t => ((ay * t + by) * t + cy) * t;
    const dx = t => (3 * ax * t + 2 * bx) * t + cx;
    return x => {
      if (x <= 0) return 0; if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 8; i++) { const e = sx(t) - x; const d = dx(t); if (Math.abs(e) < 1e-6 || !d) break; t -= e / d; }
      return sy(Math.min(1, Math.max(0, t)));
    };
  }
  const EIN = bez(.16, 1, .3, 1), EOUT = bez(.55, 0, 1, .45), EMOVE = bez(.65, 0, .35, 1);
  const clamp = v => Math.min(1, Math.max(0, v));

  // shrink text until it fits: data-fit-h (max px height), data-fit-w (max px width), data-fit-min (min font px)
  function fit() {
    document.querySelectorAll('[data-fit-h],[data-fit-w]').forEach(el => {
      const mh = +el.dataset.fitH || 1e9, mw = +el.dataset.fitW || 1e9, min = +el.dataset.fitMin || 24;
      let fs = parseFloat(getComputedStyle(el).fontSize), lh = parseFloat(getComputedStyle(el).lineHeight) / fs;
      while ((el.scrollHeight > mh + 1 || el.scrollWidth > mw + 1) && fs > min) {
        fs -= 2; el.style.fontSize = fs + 'px'; el.style.lineHeight = Math.round(fs * lh) + 'px';
      }
      el.dataset.fitted = fs;
    });
  }

  let els = [], segs = [], pulses = [], points = [];
  function collect() {
    els = [...document.querySelectorAll('[data-in]')].map(el => ({
      el, tin: +el.dataset.in, tout: el.dataset.out !== undefined ? +el.dataset.out : 1e9,
      k: el.dataset.k || 'rise', d: +(el.dataset.d || 0),
      dy: el.dataset.dy !== undefined ? +el.dataset.dy : 24, dx: +(el.dataset.dx || 0),
    }));
    els.forEach(o => { if (o.k === 'draw') { o.el.style.strokeDasharray = '1 1'; } if (o.k === 'grow') o.el.style.transformOrigin = 'left center'; if (o.k === 'vgrow') o.el.style.transformOrigin = 'center top'; });
    segs = [...document.querySelectorAll('[data-seg-s]')].map(el => ({ el, s: +el.dataset.segS, e: +el.dataset.segE, bar: el.querySelector('b') }));
    pulses = [...document.querySelectorAll('[data-pulse]')].map(el => ({ el, t: +el.dataset.pulse, out: +(el.dataset.out || 1e9) }));
    points = [...document.querySelectorAll('[data-on]')].map(el => ({ el, on: +el.dataset.on, next: +(el.dataset.next || 1e9) }));
  }

  window.setTime = function (t) {
    for (const o of els) {
      const st = o.el.style;
      let po = o.tout < 1e9 ? EOUT(clamp((t - o.tout) / 0.32)) : 0;
      if (o.k === 'draw') {
        const p = EMOVE(clamp((t - o.tin) / (o.d || 0.8)));
        st.strokeDashoffset = 1 - p; st.opacity = t < o.tin ? 0 : 1 - po;
      } else if (o.k === 'grow' || o.k === 'vgrow') {
        const p = EMOVE(clamp((t - o.tin) / (o.d || 0.8)));
        st.transform = o.k === 'grow' ? `scaleX(${p})` : `scaleY(${p})`; st.opacity = t < o.tin ? 0 : 1 - po;
      } else {
        const p = EIN(clamp((t - o.tin) / (o.d || 0.48)));
        const y = (o.k === 'fade' ? 0 : o.dy * (1 - p)) - 12 * po;
        const x = o.dx * (1 - p);
        st.opacity = p * (1 - po);
        st.transform = (x || y) ? `translate(${x}px, ${y}px)` : 'none';
      }
    }
    for (const s of segs) {
      const p = clamp((t - s.s) / (s.e - s.s));
      s.el.classList.toggle('done', t >= s.e);
      s.bar.style.width = (t >= s.e ? 0 : p * 100) + '%';
    }
    for (const p of pulses) {
      if (t < p.t || t > p.out) { p.el.style.opacity = 0; continue; }
      const ph = ((t - p.t) % 2.4) / 2.4, q = EIN(clamp(ph / 0.7));
      p.el.style.opacity = 1 - clamp(ph / 0.7);
      p.el.style.transform = `scale(${0.4 + 1.2 * q})`;
    }
    for (const p of points) {
      p.el.classList.toggle('now', t >= p.on && t < p.next);
      p.el.classList.toggle('past', t >= p.next);
    }
  };

  window.ready = (async function () {
    if (document.readyState !== 'complete') await new Promise(r => window.addEventListener('load', r));
    await document.fonts.ready;
    if (window.buildMaps) window.buildMaps();
    fit();
    if (window.layout) window.layout();
    collect();
    window.setTime(0);
    return true;
  })();
})();
