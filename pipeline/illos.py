"""Abstract topic illustrations from the Daily News design system (1080 x 520 viewBox).

Fills use classes: f1 = surface, f2 = surface-2, ln = line stroke, c = category fill,
cs = category stroke, a = accent. Each element gets class "a-el" so the animation engine
can stagger them in.
"""
import math


def _politics():
    out = ['<path class="ln" d="M140 470H940"/>']
    rows = [(150, 10, 25), (210, 8, 21), (270, 7, 17), (330, 5, 13), (390, 4, 9)]
    for r_i, (x0, lit, n) in enumerate(rows):
        r = 540 - x0
        for k in range(n):
            ang = math.pi - math.pi * k / (n - 1)
            x, y = 540 + r * math.cos(ang), 450 - r * math.sin(ang)
            cls = "c" if k < lit else "f2"
            out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="16"/>')
    out.append('<rect class="f1" x="490" y="400" width="100" height="50" rx="12"/>')
    return "".join(out)


ECONOMY = ('<path class="ln" d="M120 460H960M120 360H960M120 260H960M120 160H960" opacity=".6"/>'
           + "".join(f'<rect class="f2" x="{x}" y="{y}" width="72" height="{460 - y}" rx="8"/>'
                     for x, y in [(150, 340), (262, 290), (374, 310), (486, 250), (598, 210), (710, 230), (822, 170)])
           + '<polyline class="cs draw" pathLength="1" points="186,290 298,240 410,260 522,200 634,160 746,180 858,120" stroke-linejoin="round"/>'
           '<circle class="c" cx="858" cy="120" r="16"/>')

_TECH_EDGES = [(180, 300, 300, 160), (180, 300, 330, 400), (180, 300, 220, 120), (300, 160, 460, 260), (300, 160, 220, 120),
               (330, 400, 470, 450), (460, 260, 560, 110), (560, 110, 700, 230), (600, 400, 760, 450), (600, 400, 470, 450),
               (700, 230, 820, 120), (820, 120, 960, 240), (860, 360, 960, 240), (860, 360, 760, 450)]
_TECH_NODES = [(180, 300, 0), (300, 160, 0), (330, 400, 0), (460, 260, 1), (560, 110, 0), (600, 400, 0), (700, 230, 1),
               (820, 120, 0), (860, 360, 1), (960, 240, 0), (220, 120, 0), (760, 450, 0), (470, 450, 0)]
TECH = ("".join(f'<path class="ln draw" pathLength="1" d="M{a} {b}L{c} {d}"/>' for a, b, c, d in _TECH_EDGES)
        + "".join(f'<circle class="{"c" if hi else "f2"}" cx="{x}" cy="{y}" r="{22 if hi else 16}"/>' for x, y, hi in _TECH_NODES))

_CLIMATE_STEMS = [(150, 173, 215, 1), (210, 234, 174, 0), (255, 235, 252, 1), (330, 375, 173, 1), (390, 354, 260, 0),
                  (430, 458, 138, 1), (520, 492, 231, 1), (575, 529, 221, 0), (640, 666, 209, 1), (700, 729, 233, 1),
                  (760, 713, 180, 0), (830, 866, 189, 1), (880, 853, 212, 1), (940, 962, 154, 0)]
CLIMATE = ('<path class="ln" d="M0 70H1080M120 120H960"/>'
           '<path class="f1" d="M0 430 Q270 395 540 420 T1080 410 V520 H0Z"/>'
           + "".join(f'<path class="{"cs" if c else "ln"} draw" pathLength="1" d="M{x} 425 C{x} {(425 + y) / 2:.0f} {cx} {y + 50} {cx} {y}" '
                     f'stroke-width="{10 if c else 8}" stroke-linecap="round"/>' for x, cx, y, c in _CLIMATE_STEMS))

WORLD = ('<path class="f2" d="M120 120 C260 80 380 130 470 110 L520 230 C500 320 540 400 470 470 L160 470 C130 380 90 250 120 120Z"/>'
         '<path class="f2" d="M560 90 C700 70 820 120 950 100 L960 470 L600 470 C640 380 560 320 590 230 Z"/>'
         '<path class="cs" d="M540 80 L520 230 L560 330 L530 480" stroke-dasharray="4 18"/>'
         '<circle class="ln" cx="760" cy="260" r="44" style="stroke:var(--cat);stroke-width:4"/>'
         '<circle class="c" cx="760" cy="260" r="16"/>')

CULTURE = ('<ellipse class="cs draw" pathLength="1" cx="540" cy="270" rx="420" ry="200"/>'
           '<ellipse class="ln" cx="540" cy="270" rx="360" ry="160"/><ellipse class="ln" cx="540" cy="270" rx="300" ry="120"/>'
           '<ellipse class="ln" cx="540" cy="270" rx="240" ry="80"/><path class="ln" d="M540 70V470"/>'
           '<circle class="c" cx="900" cy="300" r="18"/>')

ILLOS = {"politics": _politics(), "economy": ECONOMY, "tech": TECH, "climate": CLIMATE, "world": WORLD, "culture": CULTURE}


def illo_svg(cat):
    return f'<svg viewBox="0 0 1080 520" aria-hidden="true">{ILLOS.get(cat, WORLD)}</svg>'
