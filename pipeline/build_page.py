"""Builds the animated 1080x1920 page for one story (see make_video.py for timing)."""
import html, json, os, re
from illos import illo_svg

HERE = os.path.dirname(os.path.abspath(__file__))
A = f"{HERE}/assets"

CAT_LABEL = {"politics": "Politics", "economy": "Economy", "tech": "Tech &amp; Science", "climate": "Climate",
             "world": "World", "culture": "Sports &amp; Culture"}
SUN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
       '<path d="M7 16a5 5 0 0 1 10 0"/><path d="M3 19.5h18M12 5v2.5M5.3 8.3l1.6 1.6M18.7 8.3l-1.6 1.6M3 16h1.5M19.5 16H21"/></svg>')
MOON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M19.5 14.5A8 8 0 1 1 9.5 4.5a6.5 6.5 0 0 0 10 10Z"/></svg>')
DOC = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
       '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>')
QUOTE = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 7H6a2 2 0 0 0-2 2v4h4v1a2 2 0 0 1-2 2v2a4 4 0 0 0 4-4zm10 0h-4a2 2 0 0 0-2 2v4h4v1a2 2 0 0 1-2 2v2a4 4 0 0 0 4-4z"/></svg>'
MARK_TXT = open(f"{A}/wordmark.path").read().strip()


def lockup(cls=""):
    return (f'<svg class="mark {cls}" viewBox="0 22 740 106"><path class="disc" d="M31.00 75.69A46.00 46.00 0 0 1 123.00 75.69Z"/>'
            f'<rect class="bar" x="0" y="87.69" width="154" height="12.31"/><path class="txt" d="{MARK_TXT}"/></svg>')


def esc(s):
    return html.escape(s or "", quote=False)


def rich(s):
    """*phrase* -> accent highlight."""
    return re.sub(r"\*(.+?)\*", r'<em class="hl">\1</em>', esc(s))


def a(tin, tout=None, k=None, **kw):
    s = f' data-in="{tin:.3f}"'
    if tout is not None:
        s += f' data-out="{tout:.3f}"'
    if k:
        s += f' data-k="{k}"'
    for key, v in kw.items():
        s += f' data-{key}="{v}"'
    return s


CSS = """
@font-face { font-family: SG; src: url('ASSETS/fonts/SchibstedGrotesk.ttf'); font-weight: 400 900; }
@font-face { font-family: SG; src: url('ASSETS/fonts/SchibstedGrotesk-Italic.ttf'); font-weight: 400 900; font-style: italic; }
:root { --accent:#f2b441; --ink:#f5f2eb; --on-accent:#10161d;
  --cat-politics:#8fb0e8; --cat-economy:#b9a6e6; --cat-tech:#6fcfd8; --cat-climate:#9acb7f; --cat-world:#c9bfaf; --cat-culture:#e7a6c0; }
.morning { --bg:#1c2633; --surface:#263243; --surface-2:#303d50; --line:#46546a; --ink-muted:#b4bdc9; --ink-subtle:#919dac; --map-hl:#4a586e; }
.evening { --bg:#0d1218; --surface:#171e28; --surface-2:#212a36; --line:#364254; --ink-muted:#a6b0bd; --ink-subtle:#808b99; --map-hl:#3a4558; }
html, body { margin:0; padding:0; background:#000; }
#frame { position:relative; width:1080px; height:1920px; overflow:hidden; background:var(--bg); color:var(--ink);
  font-family:SG, Arial, sans-serif; -webkit-font-smoothing:antialiased; font-kerning:normal; }
#frame * { box-sizing:border-box; }
h1, h2, p, blockquote, ol { margin:0; padding:0; }
.abs { position:absolute; }
.hl { color:var(--accent); font-style:normal; }
.cat-politics { --cat:var(--cat-politics); } .cat-economy { --cat:var(--cat-economy); } .cat-tech { --cat:var(--cat-tech); }
.cat-climate { --cat:var(--cat-climate); } .cat-world { --cat:var(--cat-world); } .cat-culture { --cat:var(--cat-culture); }

/* top band */
.chap { position:absolute; left:72px; top:232px; width:936px; height:8px; display:flex; gap:12px; }
.chap i { flex:1; height:8px; border-radius:4px; background:var(--line); position:relative; overflow:hidden; }
.chap i.done { background:var(--ink-muted); }
.chap i b { position:absolute; left:0; top:0; bottom:0; width:0; background:var(--accent); border-radius:4px; }
.tag { position:absolute; left:72px; top:266px; display:inline-flex; align-items:center; gap:16px; height:60px; padding:0 30px 0 26px;
  border-radius:30px; background:var(--surface); font:700 32px/36px SG; letter-spacing:.08em; text-transform:uppercase; white-space:nowrap; }
.tag::before { content:""; width:16px; height:16px; border-radius:50%; background:var(--cat); }
.edition { position:absolute; right:72px; top:266px; height:60px; display:inline-flex; align-items:center; gap:12px; color:var(--ink-muted);
  font:500 30px/36px SG; white-space:nowrap; }
.edition svg { width:44px; height:44px; color:var(--accent); }
.edition b { color:var(--ink); font-weight:700; letter-spacing:.08em; text-transform:uppercase; font-size:32px; margin-right:4px; }
.source { position:absolute; left:72px; top:1580px; display:flex; align-items:center; gap:12px; font:500 30px/36px SG; color:var(--ink-subtle); }
.source svg { width:30px; height:30px; }
.step { position:absolute; left:72px; font:500 32px/40px SG; color:var(--ink-subtle); letter-spacing:.02em; font-variant-numeric:tabular-nums; }

/* headline */
.rule { position:absolute; left:72px; top:376px; width:72px; height:7px; border-radius:4px; background:var(--cat); }
.h1 { position:absolute; left:72px; top:420px; width:900px; font:700 116px/124px SG; letter-spacing:-.02em; text-wrap:balance; }
.ctx { position:absolute; left:72px; width:820px; font:400 56px/68px SG; color:var(--ink-muted); text-wrap:pretty; }
.illo { position:absolute; left:0; width:1080px; height:500px; }
.illo svg { width:100%; height:100%; display:block; overflow:visible; }
.illo .f1 { fill:var(--surface); } .illo .f2 { fill:var(--surface-2); }
.illo .ln { fill:none; stroke:var(--line); stroke-width:4; } .illo .c { fill:var(--cat); }
.illo .cs { fill:none; stroke:var(--cat); stroke-width:6; stroke-linecap:round; } .illo .a { fill:var(--accent); }

/* statements */
.stm { position:absolute; left:72px; width:900px; font:600 84px/102px SG; letter-spacing:-.012em; text-wrap:balance; }

/* stat */
.stat { position:absolute; left:72px; top:440px; width:936px; }
.stat .num { display:block; font:800 460px/400px SG; letter-spacing:-.04em; white-space:nowrap; font-variant-numeric:lining-nums proportional-nums; }
.stat .bar { display:block; width:260px; height:12px; border-radius:6px; background:var(--accent); margin:44px 0 36px; }
.stat .lbl { display:block; font:500 58px/70px SG; color:var(--ink-muted); width:900px; }

/* map */
.mapbox { position:absolute; left:0; top:330px; width:1080px; height:900px; overflow:hidden; }
.mapsvg { display:block; }
.mapsvg .grat { fill:none; stroke:var(--line); stroke-width:1.5; opacity:.55; }
.mapsvg .land { fill:var(--surface-2); stroke:var(--bg); stroke-width:1.5; stroke-linejoin:round; }
.mapsvg .hl { fill:var(--map-hl); stroke:var(--cat-world); stroke-width:3; stroke-linejoin:round; }
.mapsvg .route { fill:none; stroke:var(--ink-muted); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
.mapsvg .city { fill:var(--ink-muted); stroke:var(--bg); stroke-width:5; }
.mapsvg .clabel { font:600 40px SG; fill:var(--ink-muted); paint-order:stroke; stroke:var(--bg); stroke-width:8px; stroke-linejoin:round; }
.mapsvg .cname { font:700 30px SG; letter-spacing:.12em; fill:var(--ink-subtle); text-transform:uppercase; }
.mapsvg .mdot { fill:var(--accent); stroke:var(--bg); stroke-width:7; }
.mapsvg .ring { fill:none; stroke:var(--accent); stroke-width:4; }
.mapsvg .pcard { fill:var(--surface); }
.mapsvg .plabel { font:700 48px SG; fill:var(--ink); }

/* timeline */
.tl-title { position:absolute; left:72px; top:420px; width:900px; font:600 84px/100px SG; letter-spacing:-.012em; }
.tl { position:absolute; left:72px; width:936px; list-style:none; }
.tl li { position:absolute; left:0; width:936px; display:grid; grid-template-columns:72px 1fr; column-gap:32px; }
.tl .pt { width:60px; height:60px; border-radius:50%; background:var(--line); margin:22px 0 0 6px; transition:none; }
.tl li.past .pt { background:var(--ink-muted); }
.tl li.now .pt { background:var(--accent); box-shadow:0 0 0 8px var(--bg), 0 0 0 12px var(--accent); }
.tl .when { display:block; font:800 120px/116px SG; letter-spacing:-.02em; font-variant-numeric:tabular-nums; white-space:nowrap; }
.tl .what { display:block; font:500 58px/68px SG; color:var(--ink-muted); margin-top:4px; }
.tl .spine { position:absolute; left:34px; width:4px; background:var(--line); border-radius:2px; transform-origin:top; }
.tl-note { position:absolute; left:72px; width:900px; font:500 56px/68px SG; color:var(--ink-muted); }

/* quote */
.quote { position:absolute; left:72px; top:440px; width:936px; padding:72px 64px 64px; border-radius:28px; background:var(--surface); }
.quote > svg { width:110px; height:110px; color:var(--accent); display:block; margin:0 0 28px -10px; }
.quote blockquote { font:italic 500 76px/96px SG; letter-spacing:-.005em; text-wrap:balance; }
.quote cite { display:block; margin-top:48px; font:700 40px/50px SG; font-style:normal; color:var(--ink-muted); }
.quote cite span { display:block; font-weight:500; font-size:34px; color:var(--ink-subtle); }

/* brand */
.mark .disc { fill:var(--accent); } .mark .bar, .mark .txt { fill:var(--ink); }
.intro-lock { position:absolute; left:160px; top:820px; width:760px; }
.intro-lock svg { width:760px; height:auto; display:block; overflow:visible; }
.intro-ed { position:absolute; left:0; right:0; top:1040px; text-align:center; font:600 40px/50px SG; color:var(--ink-muted); letter-spacing:.02em; }
.intro-ed b { color:var(--ink); text-transform:uppercase; letter-spacing:.1em; font-weight:700; }
.end-lock { position:absolute; left:72px; top:470px; width:700px; }
.end-lock svg { width:700px; height:auto; display:block; }
.end-h { position:absolute; left:72px; top:680px; width:880px; font:700 124px/128px SG; letter-spacing:-.02em; }
.next { position:absolute; left:72px; top:1100px; display:flex; align-items:center; gap:28px; padding:34px 52px 34px 40px; border-radius:28px; background:var(--surface); }
.next svg { width:76px; height:76px; color:var(--accent); }
.next b { display:block; font:700 36px/42px SG; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-muted); }
.next span { display:block; font:700 76px/84px SG; font-variant-numeric:tabular-nums; }
.tagline { position:absolute; left:72px; top:1370px; font:500 56px/68px SG; color:var(--ink-muted); }
"""


def build(story, T, out_html):
    ed = story["edition"]
    cat = story.get("category", "world")
    src = esc(story.get("source", ""))
    date_short = T["date_short"]
    sc = {s["id"]: s for s in T["scenes"]}
    parts, maps = [], []

    def O(s):  # exit time for a scene's elements
        return s["end"] - 0.32

    # ---------- intro ----------
    it = sc["intro"]
    dy = 60 if ed == "morning" else -60
    lock = lockup()
    lock = lock.replace('class="disc"', f'class="disc"{a(0.1, O(it), dy=dy, d=0.55)}')
    lock = lock.replace('<rect class="bar"', f'<rect class="bar"{a(0.0, O(it), "grow", d=0.45)}')
    lock = lock.replace('class="txt"', f'class="txt"{a(0.35, O(it), dx=-16, dy=0)}')
    ed_name = "Morning" if ed == "morning" else "Evening"
    parts.append(f'<div class="intro-lock">{lock}</div>')
    parts.append(f'<div class="intro-ed"{a(0.55, O(it), dy=16)}><b>{ed_name} edition</b> · {date_short}</div>')

    # ---------- top band (headline start .. end-card start) ----------
    content = [s for s in T["scenes"] if s["id"] not in ("intro", "end")]
    band_in, band_out = content[0]["start"], sc["end"]["start"] - 0.32
    segs = "".join(f'<i data-seg-s="{s["start"]:.3f}" data-seg-e="{s["end"]:.3f}"><b></b></i>' for s in content)
    parts.append(f'<div class="chap"{a(band_in, band_out, "fade")}>{segs}</div>')
    parts.append(f'<span class="tag cat-{cat}"{a(band_in, band_out, "fade")}>{CAT_LABEL.get(cat, "World")}</span>')
    parts.append(f'<span class="edition"{a(band_in + 0.08, band_out, "fade")}>{SUN if ed == "morning" else MOON}<b>{ed_name}</b>· {date_short}</span>')
    if src:
        parts.append(f'<div class="source"{a(band_in + 0.3, band_out, "fade")}>{DOC}<span>Source: {src}</span></div>')

    # ---------- headline ----------
    h = sc["headline"]; hs = story["headline"]; t0 = h["start"]
    parts.append(f'<div class="rule cat-{cat}"{a(t0, O(h), "grow", d=0.5)}></div>')
    parts.append(f'<h1 class="h1" data-fit-h="500" data-fit-min="84"{a(t0 + 0.05, O(h))}>{rich(hs["text"])}</h1>')
    parts.append(f'<p class="ctx" id="ctx" data-fit-h="140" data-fit-min="44"{a(t0 + 0.25, O(h))}>{rich(hs.get("context", ""))}</p>')
    parts.append(f'<div class="illo cat-{cat}" id="hillo" style="top:1060px"{a(t0 + 0.35, O(h), "fade", d=0.8)}>{illo_svg(cat)}</div>')

    # ---------- beats ----------
    beats = story["beats"]
    n = len(beats)
    for i, b in enumerate(beats):
        s = sc[f"beat{i}"]; t0, out = s["start"], O(s)
        step = f'<div class="step" style="top:{STEP_TOP.get(b["type"], 376)}px"{a(t0, out, "fade")}>{i + 1} / {n}</div>'
        texts = b.get("text") or []
        if isinstance(texts, str):
            texts = [texts]
        tt = s["text_times"]  # list of (in, out) per text
        kind = b["type"]
        if kind == "map":
            parts.append(f'<div class="mapbox" id="map{i}"></div>')
            maps.append({"id": f"map{i}", "w": 1080, "h": 900, "focus": b.get("focus", []), "bbox": b.get("bbox"),
                         "places": b.get("places", []), "route": b.get("route"), "labels": b.get("labels", []),
                         "maxScale": b.get("max_scale", 9000), "t0": t0, "tPlaces": t0 + 0.6, "tMain": t0 + 1.0, "tout": out})
            parts.append(step.replace("top:376px", "top:1256px"))
            for (ti, to), tx in zip(tt, texts):
                parts.append(f'<h2 class="stm" style="top:1300px" data-fit-h="210" data-fit-min="60"{a(ti, to)}>{rich(tx)}</h2>')
        elif kind == "stat":
            parts.append(step)
            parts.append(f'<div class="stat"><span class="num" data-fit-w="936" data-fit-min="160"{a(t0 + 0.05, out)}>{esc(b["number"])}</span>'
                         f'<span class="bar"{a(t0 + 0.35, out, "grow")}></span>'
                         f'<span class="lbl" data-fit-h="150" data-fit-min="40"{a(t0 + 0.45, out)}>{rich(b.get("label", ""))}</span></div>')
            for (ti, to), tx in zip(tt, texts):
                parts.append(f'<h2 class="stm stattxt" style="top:1260px" data-fit-h="300" data-fit-min="60"{a(ti, to)}>{rich(tx)}</h2>')
        elif kind == "timeline":
            parts.append(step)
            items = b["items"][:4]
            parts.append(f'<h2 class="tl-title"{a(t0 + 0.05, out)}>{rich(b.get("title", "How it happened"))}</h2>')
            gap = 270 if len(items) <= 3 else 205
            top0 = 600
            lis = []
            on = s["item_times"]
            for j, it_ in enumerate(items):
                nxt = on[j + 1] if j + 1 < len(on) else 1e9
                y = top0 + j * gap
                if j:
                    lis.append(f'<div class="spine" style="top:{y - gap + 96}px;height:{gap - 96}px"{a(on[j] - 0.3, out, "vgrow", d=0.5)}></div>')
                lis.append(f'<li style="top:{y}px" data-on="{on[j]:.3f}" data-next="{nxt:.3f}"{a(on[j], out)}><div class="pt"></div>'
                           f'<div><span class="when">{esc(it_["when"])}</span><span class="what">{rich(it_["what"])}</span></div></li>')
            spines = "".join(x for x in lis if 'class="spine"' in x)
            parts.append(f'<div class="tl" style="top:0;height:0">{spines}</div>')
            parts.append(f'<ol class="tl" style="top:0">{"".join(x for x in lis if x.startswith("<li"))}</ol>')
            if b.get("note"):
                ny = top0 + len(items) * gap + (20 if len(items) <= 3 else 40)
                parts.append(f'<p class="tl-note" style="top:{min(ny, 1440)}px"{a(s["note_time"], out)}>{rich(b["note"])}</p>')
        elif kind == "quote":
            parts.append(step)
            parts.append(f'<div class="quote"{a(t0 + 0.05, out)}>{QUOTE}<blockquote data-fit-h="490" data-fit-min="52">“{esc(b["quote"])}”</blockquote>'
                         f'<cite>{esc(b.get("who", ""))}<span>{esc(b.get("role", ""))}</span></cite></div>')
        else:  # statement (+ category illustration)
            parts.append(step)
            for (ti, to), tx in zip(tt, texts):
                parts.append(f'<h2 class="stm stmtop" style="top:420px" data-fit-h="520" data-fit-min="64"{a(ti, to)}>{rich(tx)}</h2>')
            parts.append(f'<div class="illo cat-{cat} stmillo" style="top:1020px"{a(t0 + 0.3, out, "fade", d=0.8)}>{illo_svg(cat)}</div>')

    # ---------- end card ----------
    e = sc["end"]; t0 = e["start"]
    follow = "Follow for tonight’s story." if ed == "morning" else "Follow for tomorrow’s story."
    nxt_label, nxt_time, nxt_icon = (("Next · Evening edition", "18:00 London", MOON) if ed == "morning"
                                     else ("Next · Morning edition", "06:00 London", SUN))
    parts.append(f'<div class="end-lock"{a(t0, None)}>{lockup()}</div>')
    parts.append(f'<h2 class="end-h"{a(t0 + 0.1, None)}>{follow}</h2>')
    parts.append(f'<div class="next"{a(t0 + 0.25, None)}>{nxt_icon}<div><b>{nxt_label}</b><span>{nxt_time}</span></div></div>')
    parts.append(f'<p class="tagline"{a(t0 + 0.4, None)}>One story. Twice a day.</p>')

    css = CSS.replace("ASSETS", A)
    body = "\n".join(parts)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>
<body><div id="frame" class="{ed}">{body}</div>
<script src="{A}/vendor/d3-array.min.js"></script><script src="{A}/vendor/d3-geo.min.js"></script>
<script src="{A}/vendor/topojson-client.min.js"></script>
<script>window.WORLD = {open(f"{A}/vendor/countries-50m.json").read()};
window.MAPS = {json.dumps(maps)};</script>
<script src="{HERE}/map.js"></script><script src="{HERE}/engine.js"></script>
<script>
window.layout = function () {{
  const box = e => e && {{ top: e.offsetTop, bottom: e.offsetTop + e.offsetHeight }};
  const h1 = document.querySelector('.h1'), ctx = document.getElementById('ctx'), il = document.getElementById('hillo');
  if (h1 && ctx) {{
    ctx.style.top = (box(h1).bottom + 40) + 'px';
    const top = Math.max(1060, box(ctx).bottom + 70);
    il.style.top = top + 'px'; il.style.height = Math.min(500, 1560 - top) + 'px';
  }}
  const st = document.querySelector('.stat'), tx = document.querySelectorAll('.stattxt');
  if (st) tx.forEach(t => t.style.top = (box(st).bottom + 70) + 'px');
  document.querySelectorAll('.stmillo').forEach(il => {{
    const tops = [...il.parentNode.querySelectorAll('.stmtop')].filter(t => Math.abs(+t.dataset.in - +il.dataset.in) < 1e9);
    let b = 0; tops.forEach(t => b = Math.max(b, box(t).bottom));
    il.style.top = Math.min(1060, Math.max(860, b + 110)) + 'px';
  }});
}};
</script>
</body></html>"""
    open(out_html, "w").write(page)


STEP_TOP = {"stat": 376, "timeline": 376, "quote": 376, "statement": 376, "map": 1256}
