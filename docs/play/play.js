/* play.js — the interactive companion. Every demo runs the same mathematics the static
   figures were drawn from, live in the browser. No libraries. Reads the sliders, steps the
   equations, paints a canvas. */
"use strict";

const REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const C = {
  ink: "#f3efe6", mute: "#b3ac9e", line: "#2a2a38", grid: "#1c1c28",
  hot: "#ffb347", blue: "#8fd0ff", red: "#ff6a5e", gold: "#ffd27a", violet: "#c8a6ff", green: "#8fe0a8",
  bg: "#050507"
};

/* ---- a small plotting surface over a <canvas>, with device-pixel scaling ---- */
function Plot(canvas, opts) {
  const o = opts || {};
  const c = canvas, ctx = c.getContext("2d");
  const pad = o.pad || [40, 14, 30, 46];
  let W = 0, H = 0, dpr = 1;
  const P = {
    xlim: o.xlim || [0, 1], ylim: o.ylim || [0, 1],
    resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = c.getBoundingClientRect();
      W = Math.max(200, rect.width); H = o.h || Math.round(W * (o.ratio || 0.62));
      c.width = W * dpr; c.height = H * dpr; c.style.height = H + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    },
    get w() { return W; }, get h() { return H; },
    ix0() { return pad[0]; }, ix1() { return W - pad[1]; },
    iy0() { return H - pad[2]; }, iy1() { return pad[3] ? pad[3] : 14; },
    mx(x) { return this.ix0() + (x - this.xlim[0]) / (this.xlim[1] - this.xlim[0]) * (this.ix1() - this.ix0()); },
    my(y) { return this.iy0() + (y - this.ylim[0]) / (this.ylim[1] - this.ylim[0]) * (this.iy1() - this.iy0()); },
    clear() { ctx.clearRect(0, 0, W, H); ctx.fillStyle = C.bg; ctx.fillRect(this.ix0(), this.iy1(), this.ix1() - this.ix0(), this.iy0() - this.iy1()); },
    axes(t) {
      t = t || {};
      ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.fillStyle = C.mute;
      ctx.font = "11px 'Avenir Next',system-ui,sans-serif";
      const xt = t.xticks || tickvals(this.xlim[0], this.xlim[1], 5);
      ctx.textAlign = "center"; ctx.textBaseline = "top";
      xt.forEach(v => {
        const X = this.mx(v);
        ctx.beginPath(); ctx.moveTo(X, this.iy1()); ctx.lineTo(X, this.iy0()); ctx.stroke();
        ctx.fillText(fmt(v), X, this.iy0() + 4);
      });
      const yt = t.yticks || tickvals(this.ylim[0], this.ylim[1], 4);
      ctx.textAlign = "right"; ctx.textBaseline = "middle";
      yt.forEach(v => {
        const Y = this.my(v);
        ctx.beginPath(); ctx.moveTo(this.ix0(), Y); ctx.lineTo(this.ix1(), Y); ctx.stroke();
        ctx.fillText(fmt(v), this.ix0() - 5, Y);
      });
      ctx.strokeStyle = C.line; ctx.lineWidth = 1.4;
      ctx.strokeRect(this.ix0(), this.iy1(), this.ix1() - this.ix0(), this.iy0() - this.iy1());
      if (t.title) { ctx.fillStyle = C.ink; ctx.textAlign = "left"; ctx.textBaseline = "top"; ctx.font = "700 12px 'Avenir Next',system-ui,sans-serif"; ctx.fillText(t.title, this.ix0() + 4, this.iy1() + 4); }
      if (t.xlabel) { ctx.fillStyle = C.mute; ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.font = "11px 'Avenir Next',system-ui,sans-serif"; ctx.fillText(t.xlabel, (this.ix0() + this.ix1()) / 2, H - 1); }
    },
    line(pts, color, w) {
      ctx.strokeStyle = color; ctx.lineWidth = w || 1.6; ctx.lineJoin = "round"; ctx.lineCap = "round";
      ctx.beginPath();
      for (let i = 0; i < pts.length; i++) { const X = this.mx(pts[i][0]), Y = this.my(pts[i][1]); if (i) ctx.lineTo(X, Y); else ctx.moveTo(X, Y); }
      ctx.stroke();
    },
    hline(y, color, dash) { ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.setLineDash(dash || [5, 5]); ctx.beginPath(); ctx.moveTo(this.ix0(), this.my(y)); ctx.lineTo(this.ix1(), this.my(y)); ctx.stroke(); ctx.setLineDash([]); },
    vline(x, color, dash) { ctx.strokeStyle = color; ctx.lineWidth = 1.4; ctx.setLineDash(dash || [5, 5]); ctx.beginPath(); ctx.moveTo(this.mx(x), this.iy1()); ctx.lineTo(this.mx(x), this.iy0()); ctx.stroke(); ctx.setLineDash([]); },
    dot(x, y, color, r) { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(this.mx(x), this.my(y), r || 3, 0, 7); ctx.fill(); },
    label(x, y, s, color, align) { ctx.fillStyle = color; ctx.font = "12px 'Avenir Next',system-ui,sans-serif"; ctx.textAlign = align || "left"; ctx.textBaseline = "alphabetic"; ctx.fillText(s, this.mx(x), this.my(y)); },
    ctx() { return ctx; }
  };
  P.resize();
  return P;
}

function tickvals(lo, hi, n) {
  const step = nice((hi - lo) / n); const out = []; let v = Math.ceil(lo / step) * step;
  while (v <= hi + step * 1e-9) { out.push(Math.round(v * 1e6) / 1e6); v += step; } return out;
}
function nice(x) { if (x <= 0) return 1; const e = Math.floor(Math.log10(x)), f = x / 10 ** e; const nf = f < 1.5 ? 1 : f < 3 ? 2 : f < 4 ? 2.5 : f < 7 ? 5 : 10; return nf * 10 ** e; }
function fmt(v) { if (Math.abs(v) >= 1000 || (v !== 0 && Math.abs(v) < 0.01)) return v.toExponential(0); return (Math.round(v * 100) / 100).toString(); }
function $(id) { return document.getElementById(id); }
function bind(slider, out, fn) { const el = $(slider), o = $(out); function upd() { if (o) o.textContent = fn ? fn(+el.value) : el.value; } el.addEventListener("input", upd); upd(); return el; }

/* ============================================================ 1 · the logistic lab */
function logisticLab() {
  const cob = Plot($("lab-cobweb"), { xlim: [0, 1], ylim: [0, 1], ratio: 1, pad: [34, 12, 26, 36] });
  const ts = Plot($("lab-series"), { xlim: [0, 60], ylim: [0, 1], ratio: 0.5, pad: [34, 12, 26, 36] });
  const bif = Plot($("lab-bif"), { xlim: [2.5, 4], ylim: [0, 1], ratio: 0.5, pad: [34, 12, 26, 36] });
  const rEl = bind("lab-r", "lab-r-out", v => v.toFixed(3));
  const xEl = bind("lab-x0", "lab-x0-out", v => v.toFixed(2));
  let bifCache = null;

  function period(r) {
    let x = 0.5; for (let i = 0; i < 2000; i++) x = r * x * (1 - x);
    const tail = []; for (let i = 0; i < 400; i++) { x = r * x * (1 - x); tail.push(x); }
    const last = tail[tail.length - 1];
    for (const p of [1, 2, 3, 4, 8, 16]) { let ok = true; for (let k = 1; k <= 3; k++) if (Math.abs(tail[tail.length - 1 - k * p] - last) > 1.5e-4) { ok = false; break; } if (ok && Math.abs(tail[tail.length - 1 - p] - last) < 1.5e-4) return p; }
    return 0;
  }
  function buildBif() {
    bif.clear(); bif.axes({ title: "the whole family — click to set r", xlabel: "r" });
    const ctx = bif.ctx(); ctx.fillStyle = "rgba(255,179,71,.5)";
    for (let i = 0; i < 700; i++) {
      const r = 2.5 + 1.5 * i / 699; let x = 0.5;
      for (let k = 0; k < 300; k++) x = r * x * (1 - x);
      for (let k = 0; k < 80; k++) { x = r * x * (1 - x); ctx.fillRect(bif.mx(r), bif.my(x), 0.7, 0.7); }
    }
    bifCache = ctx.getImageData(0, 0, bif.ctx().canvas.width, bif.ctx().canvas.height);
  }
  function draw() {
    const r = +rEl.value, x0 = +xEl.value;
    // cobweb
    cob.clear(); cob.axes({ title: "the rule and the staircase", xlabel: "this step" });
    const hill = []; for (let i = 0; i <= 200; i++) { const x = i / 200; hill.push([x, r * x * (1 - x)]); }
    cob.line(hill, C.hot, 2.2); cob.line([[0, 0], [1, 1]], C.mute, 1.2);
    let x = x0; const web = [[x, 0]];
    for (let i = 0; i < 200; i++) { const y = r * x * (1 - x); web.push([x, y]); web.push([y, y]); x = y; }
    cob.line(web, C.blue, 1);
    // series
    ts.clear(); ts.axes({ title: "value over time", xlabel: "step" });
    x = x0; const s = [[0, x]]; for (let i = 1; i <= 60; i++) { x = r * x * (1 - x); s.push([i, x]); }
    ts.line(s, C.hot, 1.8); s.forEach(p => ts.dot(p[0], p[1], C.gold, 1.6));
    // bifurcation marker
    if (bifCache) bif.ctx().putImageData(bifCache, 0, 0);
    bif.vline(r, C.violet, [4, 4]);
    // readout
    const p = period(r);
    const word = p === 1 ? "settles to one value" : p === 0 ? "chaos — it never repeats" : "a " + p + "-step cycle";
    $("lab-read").innerHTML = "r = <b>" + r.toFixed(3) + "</b> · " + word;
  }
  $("lab-bif").addEventListener("click", ev => {
    const rect = ev.target.getBoundingClientRect();
    const rx = 2.5 + (ev.clientX - rect.left - bif.ix0()) / (bif.ix1() - bif.ix0()) * 1.5;
    rEl.value = Math.min(4, Math.max(2.5, rx)); rEl.dispatchEvent(new Event("input"));
  });
  [rEl, xEl].forEach(e => e.addEventListener("input", draw));
  const ro = new ResizeObserver(() => { cob.resize(); ts.resize(); bif.resize(); buildBif(); draw(); });
  ro.observe($("lab-cobweb").parentElement);
  buildBif(); draw();
}

/* ============================================================ 2 · two starts diverging */
function divergence() {
  const p = Plot($("div-canvas"), { xlim: [0, 70], ylim: [0, 1], ratio: 0.42, pad: [34, 12, 26, 40] });
  const rEl = bind("div-r", "div-r-out", v => v.toFixed(3));
  const gEl = bind("div-gap", "div-gap-out", v => "10" + sup(-v));
  let a = [], b = [], t = 0, raf = null;
  function reset() {
    const r = +rEl.value, gap = 10 ** (-(+gEl.value));
    a = [0.4]; b = [0.4 + gap]; t = 0;
    let xa = a[0], xb = b[0];
    for (let i = 1; i <= 70; i++) { xa = r * xa * (1 - xa); xb = r * xb * (1 - xb); a.push(xa); b.push(xb); }
    frame(REDUCED ? 71 : 0);
  }
  function frame(upTo) {
    p.clear(); p.axes({ title: "same rule, two starts a hair apart", xlabel: "step" });
    const n = Math.min(upTo, 70);
    p.line(a.slice(0, n + 1).map((v, i) => [i, v]), C.blue, 1.8);
    p.line(b.slice(0, n + 1).map((v, i) => [i, v]), C.hot, 1.8);
    let sep = 70; for (let i = 0; i <= n; i++) if (Math.abs(a[i] - b[i]) > 0.25) { sep = i; break; }
    if (sep <= n) { p.vline(sep, C.mute, [4, 5]); p.label(sep + 1, 0.94, "they part at step " + sep, C.mute); }
    if (!REDUCED && upTo < 70) raf = requestAnimationFrame(() => frame(upTo + 1));
  }
  rEl.addEventListener("input", reset); gEl.addEventListener("input", reset);
  $("div-replay").addEventListener("click", () => { if (raf) cancelAnimationFrame(raf); reset(); });
  new ResizeObserver(() => { p.resize(); frame(70); }).observe($("div-canvas").parentElement);
  reset();
}
function sup(n) { const m = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶" }; return String(n).split("").map(c => m[c] || c).join(""); }

/* ============================================================ 3 · the Lorenz attractor */
function lorenzLab() {
  const p = Plot($("lz-canvas"), { xlim: [-24, 24], ylim: [0, 52], ratio: 0.8, pad: [34, 12, 26, 40] });
  const rhoEl = bind("lz-rho", "lz-rho-out", v => v.toFixed(0));
  const twinEl = $("lz-twin");
  let A, Bt, dt = 0.006, raf = null, trailA = [], trailB = [];
  function deriv(s, rho) { const [x, y, z] = s; return [10 * (y - x), x * (rho - z) - y, x * y - 8 / 3 * z]; }
  function step(s, rho) {
    const k1 = deriv(s, rho), k2 = deriv([s[0] + dt / 2 * k1[0], s[1] + dt / 2 * k1[1], s[2] + dt / 2 * k1[2]], rho),
      k3 = deriv([s[0] + dt / 2 * k2[0], s[1] + dt / 2 * k2[1], s[2] + dt / 2 * k2[2]], rho),
      k4 = deriv([s[0] + dt * k3[0], s[1] + dt * k3[1], s[2] + dt * k3[2]], rho);
    return [0, 1, 2].map(i => s[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
  }
  function reset() { A = [1, 1, 1]; Bt = [1 + 1e-3, 1, 1]; trailA = []; trailB = []; }
  function tick() {
    const rho = +rhoEl.value, twin = twinEl.checked;
    for (let i = 0; i < (REDUCED ? 4000 : 12); i++) { A = step(A, rho); trailA.push([A[0], A[2]]); if (twin) { Bt = step(Bt, rho); trailB.push([Bt[0], Bt[2]]); } }
    if (trailA.length > 4000) trailA = trailA.slice(-4000);
    if (trailB.length > 4000) trailB = trailB.slice(-4000);
    p.clear(); p.axes({ title: "the butterfly · ρ = " + rho + " (σ=10, β=8/3)", xlabel: "x  (z upward)" });
    p.line(trailA, C.hot, 0.8);
    if (twin) { p.line(trailB, C.blue, 0.8); const gap = Math.hypot(A[0] - Bt[0], A[1] - Bt[1], A[2] - Bt[2]); $("lz-read").innerHTML = "gap between the twins: <b>" + gap.toFixed(2) + "</b>"; }
    else $("lz-read").textContent = "";
    if (!REDUCED) raf = requestAnimationFrame(tick);
  }
  rhoEl.addEventListener("input", reset); twinEl.addEventListener("change", reset);
  $("lz-reset").addEventListener("click", reset);
  new ResizeObserver(() => p.resize()).observe($("lz-canvas").parentElement);
  reset(); if (REDUCED) { for (let i = 0; i < 20; i++) tick(); } else tick();
}

/* ============================================================ 4 · the law of large numbers */
function diceLab() {
  const p = Plot($("dice-canvas"), { xlim: [1, 1000], ylim: [1, 6], ratio: 0.42, pad: [34, 12, 26, 44] });
  let n = 0, sum = 0, run = [];
  const sigma = Math.sqrt([1, 2, 3, 4, 5, 6].reduce((a, k) => a + (k - 3.5) ** 2, 0) / 6);
  function draw() {
    p.xlim = [1, Math.max(50, n)];
    p.clear(); p.axes({ title: "one fair die, rolled again and again", xlabel: "rolls" });
    // funnel
    const ctx = p.ctx(); ctx.fillStyle = "rgba(143,208,255,.12)";
    ctx.beginPath();
    for (let i = 1; i <= Math.max(1, n); i++) { const X = p.mx(i), Y = p.my(Math.min(6, 3.5 + 2 * sigma / Math.sqrt(i))); if (i === 1) ctx.moveTo(X, Y); else ctx.lineTo(X, Y); }
    for (let i = Math.max(1, n); i >= 1; i--) { const X = p.mx(i), Y = p.my(Math.max(1, 3.5 - 2 * sigma / Math.sqrt(i))); ctx.lineTo(X, Y); }
    ctx.closePath(); ctx.fill();
    p.hline(3.5, C.gold, [6, 5]);
    if (run.length) p.line(run, C.hot, 1.6);
    $("dice-read").innerHTML = n ? "rolls: <b>" + n + "</b> · average so far: <b>" + (sum / n).toFixed(3) + "</b> (true 3.5)" : "roll some dice.";
  }
  function roll(k) { for (let i = 0; i < k; i++) { n++; sum += 1 + Math.floor(Math.random() * 6); run.push([n, sum / n]); } if (run.length > 2000) run = run.slice(-2000); draw(); }
  $("dice-1").addEventListener("click", () => roll(1));
  $("dice-100").addEventListener("click", () => roll(100));
  $("dice-1000").addEventListener("click", () => roll(1000));
  $("dice-reset").addEventListener("click", () => { n = 0; sum = 0; run = []; draw(); });
  new ResizeObserver(() => { p.resize(); draw(); }).observe($("dice-canvas").parentElement);
  draw();
}

/* ============================================================ 5 · the governor */
function governorLab() {
  const p = Plot($("gov-canvas"), { xlim: [0, 260], ylim: [-16, 16], ratio: 0.42, pad: [34, 12, 26, 44] });
  const kEl = bind("gov-k", "gov-k-out", v => (v * 100).toFixed(0) + "%");
  let drift = 0, held = 0, A = [], B = [], t = 0, raf = null, shock = 0;
  function gauss() { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function reset() { drift = 0; held = 0; A = []; B = []; t = 0; }
  function tick() {
    const k = +kEl.value;
    const s = gauss() * 0.5 + shock; shock *= 0.6;
    drift += s; held += s; held -= k * held;
    A.push([t, drift]); B.push([t, held]); t++;
    if (A.length > 260) { A.shift(); B.shift(); A.forEach((pt, i) => pt[0] = i); B.forEach((pt, i) => pt[0] = i); t = 260; }
    p.clear(); p.axes({ title: "same shocks, two tanks", xlabel: "step" });
    p.hline(0, C.mute, [4, 6]);
    p.line(A, C.red, 1.7); p.line(B, C.green, 1.8);
    p.label(4, 14, "no feedback", C.red); p.label(4, -13, "pulls back " + (k * 100).toFixed(0) + "%", C.green);
    if (!REDUCED) raf = requestAnimationFrame(tick);
  }
  kEl.addEventListener("input", () => {});
  $("gov-kick").addEventListener("click", () => { shock += 6; });
  $("gov-reset").addEventListener("click", reset);
  new ResizeObserver(() => p.resize()).observe($("gov-canvas").parentElement);
  reset(); if (REDUCED) { for (let i = 0; i < 260; i++) tick(); } else tick();
}

/* ---- go ---- */
function boot() {
  if ($("lab-cobweb")) logisticLab();
  if ($("div-canvas")) divergence();
  if ($("lz-canvas")) lorenzLab();
  if ($("dice-canvas")) diceLab();
  if ($("gov-canvas")) governorLab();
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
