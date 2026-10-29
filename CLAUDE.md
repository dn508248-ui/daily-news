# Daily News – production runbook

Daily News is a short-form news channel (TikTok, Instagram Reels, YouTube Shorts): **one story, twice a day**,
the single most important story in the world, 45–60 s, calm, neutral, English voiceover.
Morning edition goes live **06:00 London**, Evening edition **18:00 London**.

A scheduled run produces ONE edition end-to-end, without asking anyone. Follow these steps.

## 1. Setup (2 min)
```
cd <repo> && bash pipeline/setup.sh
```
Edition number: `01` = morning, `02` = evening. Date = today's date in **Europe/London**.
Story file: `stories/<YYYY-MM-DD>_<01|02>.json`. If it already exists and `videos/<same name>.json` too, this edition is done: stop.

## 2. Pick the story
- Search the web (several searches: world news today, Reuters, AP, BBC) for the **most important story of the last ~12 hours**, worldwide, any topic (politics, economy, tech & science, climate, world/conflict/disasters, sports & culture).
- Prefer what matters most to many people; young audience. Neutral and informative.
- **Do not repeat** the topic of the previous edition (read the newest file in `stories/`), unless there is a major new development – then say what is new.
- **Unconfirmed breaking news: skip it** and take another story. Every number and claim must be confirmed by at least two reputable sources (wire services, public broadcasters, official statements). Use "at least" for rising tolls. Never guess.
- Fetch the actual articles (WebFetch) for exact figures, names, times and places.

## 3. Write the story JSON
```json
{
  "date": "2026-10-30", "edition": "morning",            // morning | evening
  "category": "world",            // politics | economy | tech | climate | world | culture   (world = conflict, disasters)
  "source": "Reuters, AP",        // max 2 sources, shown on screen
  "voice": "af_heart",
  "say": {"Urda": "Oorda"},       // optional respellings so the voice pronounces names right
  "headline": {"text": "Spain investigates high-speed train crash",   // subject + verb, ≤ 60 chars, no question, no clickbait
               "context": "At least 69 people died south of Madrid.",   // one line, ≤ 60 chars
               "vo": "…"},       // 1–2 sentences
  "beats": [ 2 or 3 beats, see below ],
  "title": "…",                   // YouTube/TikTok title, ≤ 90 chars, plain
  "caption": "…",                 // 2–4 sentences: what happened, why it matters, what's next. English.
  "hashtags": ["world", "news", "dailynews", "spain", "traincrash"]   // 5: category first, then news, dailynews, 2 topical
}
```
Beat types (each has `"vo"` = what the voice says during that beat, 1–4 sentences):
- `statement`: `"text": "One fact, ≤ 12 words."` – category illustration under it.
- `stat`: `"number": "69"` (≤ 5 chars: 69, 1.2M, 4%, $40bn), `"label": "deaths confirmed so far, officials say"`, optional `"text": "second fact"`.
- `map`: `"focus": ["Spain"]` (exact names from `pipeline/assets/country-names.txt`; several allowed), optional `"bbox": [west, south, east, north]` to set the view,
  `"places": [{"name": "Madrid", "lat": 40.4168, "lon": -3.7038}, {"name": "Urda", "lat": 39.41, "lon": -3.71, "main": true}]` (look up real coordinates; exactly one `main`),
  optional `"route": ["Madrid", "Urda"]`, optional `"labels": [{"name": "Atlantic", "lat": .., "lon": ..}]`, `"text"`.
- `timeline`: `"title": "How it happened"`, `"items": [{"when": "08:30", "what": "Safety system fails"}, …]` (2–4 items, `what` ≤ 30 chars), optional `"note"`.
  Items appear with the sentences of the vo, so write one sentence per item.
- `quote`: `"quote": "…"` (≤ 20 words, verbatim from a source), `"who": "Name"`, `"role": "Title"`.

`"text"` may also be a list of 2 texts: they are shown one after the other, switching at the middle sentence of the vo.
Mark at most one phrase per text with `*asterisks*` – it is shown in the accent colour (the number or key term).

Writing rules: on-screen text states the fact, the voice explains. Sentence case, no exclamation marks, no emoji, no adjectives
that judge ("shocking", "historic"). Attribute claims ("…, officials say"). Sensitive stories: exact attributed figures, name
places not victims, nothing graphic. Disputed facts: say so.
Voiceover: **110–140 words in total** (headline + beats) → 45–60 s. Write numbers in the vo as words when unusual
("sixty-nine", "five hundred"); years as digits are fine. Check names: `python3 pipeline/tts.py check Name1 Name2` and add
respellings to `"say"` when the phonemes look wrong.
Good beat mixes: map + stat + timeline · stat + quote + statement · map + statement + quote. Use a map whenever a place matters.

## 4. Check the layout
```
python3 pipeline/make_video.py stories/<name>.json --stills
```
Fix every ERROR/WARNING it prints. Then **look at `build/<name>/sheet.jpg`** (Read tool): text must not overlap, run out
of the frame or be cut; the map must show the right area with the marker in view. Fix the JSON and repeat if needed.

## 5. Render and publish
```
python3 pipeline/publish.py stories/<name>.json
```
This renders the MP4 (~3 min), uploads it, pushes `videos/<name>.json`; a GitHub Action then schedules it in Buffer for
06:00 / 18:00 London on TikTok, Instagram and YouTube, and the script waits for the result.
- If it is already later than 15 minutes before the slot, add `--now` (publishes immediately).
- `RESULT: OK` → done. Finish with a 2-line summary (story + scheduled time).
- `RESULT: FAILED` / `UNKNOWN` or any step you cannot fix → retry once; if it still fails, send a push notification to the
  user (PushNotification tool) in German: what failed and that the edition is missing, and end the run with that message.

Never post anything else, never delete posts, never change workflows or secrets during a scheduled run.

## Repo map
- `pipeline/examples/` – a complete example story
- `pipeline/` – make_video.py (story → MP4), publish.py, build_page.py (layouts), engine.js/map.js (animation), tts.py (Kokoro voice), music.py
- `stories/` – one JSON per edition · `videos/` – Buffer job files (trigger `.github/workflows/publish.yml`)
- branch `media` – the MP4 files (cleaned weekly) · branch `bot-logs` – results of the Buffer workflow
- `config/channels.json` – Buffer channel IDs · secret `BUFFER_API_KEY` (GitHub Actions)
