"""Story JSON -> finished Daily News MP4.

Usage:
  python3 pipeline/make_video.py stories/2026-10-30_01.json            # full render
  python3 pipeline/make_video.py stories/2026-10-30_01.json --stills   # quick check: contact sheet only
Outputs go to build/<name>/ : <name>.mp4, sheet.jpg (stills for review), timing.json
"""
import json, os, re, subprocess, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tts, music, build_page

FPS = 30
INTRO = 1.6
CATS = {"politics", "economy", "tech", "climate", "world", "culture"}
TYPES = {"statement", "stat", "map", "timeline", "quote"}


def run(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def validate(st):
    err, warn = [], []
    for k in ("date", "edition", "category", "headline", "beats", "title", "caption"):
        if k not in st:
            err.append(f"missing field: {k}")
    if err:
        return err, warn
    if st["edition"] not in ("morning", "evening"):
        err.append("edition must be morning or evening")
    if st["category"] not in CATS:
        err.append(f"category must be one of {sorted(CATS)}")
    if not 2 <= len(st["beats"]) <= 3:
        err.append("2 or 3 beats")
    for i, b in enumerate(st["beats"]):
        if b.get("type") not in TYPES:
            err.append(f"beat {i}: type must be one of {sorted(TYPES)}")
        if not b.get("vo"):
            err.append(f"beat {i}: vo missing")
        if b.get("type") == "map":
            if not b.get("places"):
                err.append(f"beat {i}: map needs places")
            names = set(open(f"{build_page.A}/country-names.txt").read().split("\n"))
            for c in b.get("focus", []):
                if c not in names:
                    err.append(f"beat {i}: unknown country '{c}' (see pipeline/assets/country-names.txt)")
        if b.get("type") == "stat" and len(b.get("number", "")) > 6:
            warn.append(f"beat {i}: number '{b['number']}' is long (≤5 chars looks best)")
        if b.get("type") == "timeline" and not 2 <= len(b.get("items", [])) <= 4:
            err.append(f"beat {i}: timeline needs 2-4 items")
    words = sum(len(x.split()) for x in [st["headline"].get("vo", "")] + [b.get("vo", "") for b in st["beats"]])
    if not 95 <= words <= 150:
        warn.append(f"voiceover has {words} words (aim for 110-140)")
    return err, warn


def text_times(s, k):
    """Show k texts one after another, switching at sentence starts."""
    ns = len(s["sent"])
    starts = [s["start"] + 0.3]
    for j in range(1, k):
        idx = round(j * ns / k)
        t = s["sent"][idx] if 0 < idx < ns else s["vo_at"] + s["vo"] * j / k
        starts.append(max(t, starts[-1] + 2.5))
    outs = [x - 0.32 for x in starts[1:]] + [s["end"] - 0.32]
    return list(zip(starts, outs))


def timing(st, work):
    voice = st.get("voice", "af_heart")
    say = st.get("say", {})
    end_vo = "Follow for tonight's story." if st["edition"] == "morning" else "Follow for tomorrow's story."
    scenes = [{"id": "headline", "text_vo": st["headline"]["vo"]}]
    scenes += [{"id": f"beat{i}", "text_vo": b["vo"], "beat": b} for i, b in enumerate(st["beats"])]
    scenes += [{"id": "end", "text_vo": end_vo}]
    t = INTRO
    for s in scenes:
        s["wav"] = f"{work}/vo_{s['id']}.wav"
        s["vo"], starts = tts.scene_audio(s["text_vo"], voice, say, s["wav"])
        s["start"] = t
        lead = 0.6 if s["id"] != "end" else 0.5
        s["vo_at"] = t + lead
        s["sent"] = [s["vo_at"] + x for x in starts]
        if s["id"] == "end":
            s["end"] = max(s["vo_at"] + s["vo"] + 1.6, t + 3.0)
        else:
            s["end"] = s["vo_at"] + s["vo"] + 0.7
            s["end"] = max(s["end"], t + (5.5 if s["id"] == "headline" else 4.0))
        b = s.get("beat")
        if b:
            texts = b.get("text") or []
            k = 1 if isinstance(texts, str) else max(1, len(texts))
            s["text_times"] = text_times(s, k)
            if b["type"] == "timeline":
                m = len(b["items"][:4]); ns = len(s["sent"])
                if ns >= m:
                    s["item_times"] = [s["sent"][round(j * ns / m)] if j else s["start"] + 0.5 for j in range(m)]
                else:
                    s["item_times"] = [s["start"] + 0.5 + j * (s["vo"] / m) for j in range(m)]
                s["note_time"] = s["sent"][-1] if ns > m else s["item_times"][-1] + 1.2
        t = s["end"] + 0.12
        s.pop("beat", None)
    total = scenes[-1]["end"]
    d = dt.date.fromisoformat(st["date"])
    return {"scenes": [{"id": "intro", "start": 0, "end": INTRO}] + scenes, "total": round(total, 3),
            "date_short": d.strftime("%a %-d %b"), "frames": int(round(total * FPS))}


def render(html, out_mp4, frames, stills=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto(f"file://{html}")
        pg.evaluate("window.ready")
        pg.wait_for_timeout(200)
        el = pg.locator("#frame")
        if stills:
            shots = []
            for i, ts in enumerate(stills):
                pg.evaluate(f"setTime({ts})")
                path = f"{os.path.dirname(html)}/still_{i:02d}.jpg"
                el.screenshot(path=path, type="jpeg", quality=85)
                shots.append(path)
            br.close()
            return shots
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out_mp4],
                              stdin=subprocess.PIPE)
        for i in range(frames):
            pg.evaluate(f"setTime({i / FPS})")
            ff.stdin.write(el.screenshot(type="jpeg", quality=92))
        ff.stdin.close()
        ff.wait()
        br.close()


def assemble(T, work, video, out):
    total = T["total"]
    vo = [s for s in T["scenes"] if "wav" in s]
    inputs, chains = [], []
    for i, s in enumerate(vo):
        inputs += ["-i", s["wav"]]
        ms = int(round(s["vo_at"] * 1000))
        chains.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms}[v{i}]")
    mix = "".join(f"[v{i}]" for i in range(len(vo)))
    fc = ";".join(chains) + f";{mix}amix=inputs={len(vo)}:normalize=0,apad=whole_dur={total},atrim=0:{total},loudnorm=I=-15:TP=-1.5:LRA=11[out]"
    run([*inputs, "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-ac", "1", f"{work}/voice.wav"])
    music.make(total + 0.5, f"{work}/music.wav")
    run(["-i", f"{work}/music.wav", "-af", f"atrim=0:{total},afade=t=in:d=0.3,afade=t=out:st={total - 1.4}:d=1.4,loudnorm=I=-27:TP=-3",
         "-ar", "48000", f"{work}/music_bed.wav"])
    run(["-i", video, "-i", f"{work}/voice.wav", "-i", f"{work}/music_bed.wav",
         "-filter_complex", "[1:a]pan=stereo|c0=c0|c1=c0[v];[v][2:a]amix=inputs=2:normalize=0,alimiter=limit=0.89[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out])


def review_times(T):
    ts = []
    for s in T["scenes"]:
        if s["id"] == "intro":
            ts.append(1.1)
        elif s["id"] == "end":
            ts.append(s["end"] - 0.3)
        else:
            ts.append(s["start"] + 2.0)
            ts.append(s["end"] - 0.5)
    return ts


def main(path, stills_only=False):
    st = json.load(open(path))
    err, warn = validate(st)
    for w in warn:
        print("WARNING:", w)
    if err:
        print("ERRORS:\n  " + "\n  ".join(err))
        sys.exit(2)
    name = os.path.splitext(os.path.basename(path))[0]
    work = os.path.abspath(f"build/{name}")
    os.makedirs(work, exist_ok=True)
    T = timing(st, work)
    json.dump(T, open(f"{work}/timing.json", "w"), indent=1)
    html = f"{work}/index.html"
    build_page.build(st, T, html)
    print(f"duration {T['total']:.1f}s")
    shots = render(html, None, 0, stills=review_times(T))
    n = len(shots)
    cols = 5
    run(["-i", f"{work}/still_%02d.jpg", "-vf", f"scale=360:640,tile={cols}x{(n + cols - 1) // cols}:padding=6:color=white",
         "-frames:v", "1", f"{work}/sheet.jpg"])
    print(f"review sheet: {work}/sheet.jpg")
    if stills_only:
        return
    render(html, f"{work}/video.mp4", T["frames"])
    out = f"{work}/{name}.mp4"
    assemble(T, work, f"{work}/video.mp4", out)
    print(f"video: {out}")


if __name__ == "__main__":
    main(sys.argv[1], "--stills" in sys.argv)
