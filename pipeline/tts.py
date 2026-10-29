"""Voiceover with Kokoro (local, free). One WAV per scene plus sentence start times.

Story fields used: voice, say (word -> respelling for pronunciation), and every scene's "vo".
"""
import json, os, re, sys
import numpy as np, soundfile as sf

MODELS = os.environ.get("DN_MODELS", os.path.expanduser("~/.cache/daily-news/models"))
GAP = 0.28  # pause between sentences (s)
_k = None


def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(f"{MODELS}/kokoro-v1.0.onnx", f"{MODELS}/voices-v1.0.bin")
    return _k


def respell(text, say):
    for word, sp in (say or {}).items():
        text = re.sub(rf"\b{re.escape(word)}\b", sp, text)
    return text


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def speak(text, voice, say):
    k = kokoro()
    s, sr = k.create(respell(text, say), voice=voice, speed=1.0, lang="en-us")
    a = np.abs(s)
    i = np.where(a > 0.01)[0]
    if len(i) == 0:
        return s, sr
    return s[max(i[0] - int(0.03 * sr), 0): i[-1] + int(0.08 * sr)], sr


def scene_audio(text, voice, say, path):
    """Writes path, returns (duration, [sentence start times])."""
    parts, starts, t, sr = [], [], 0.0, 24000
    for n, sent in enumerate(sentences(text)):
        s, sr = speak(sent, voice, say)
        if n:
            parts.append(np.zeros(int(GAP * sr), dtype=s.dtype))
            t += GAP
        starts.append(round(t, 3))
        parts.append(s)
        t += len(s) / sr
    audio = np.concatenate(parts) if parts else np.zeros(1)
    sf.write(path, audio, sr)
    return round(len(audio) / sr, 3), starts


def phonemes(words):
    k = kokoro()
    return {w: k.tokenizer.phonemize(w, "en-us") for w in words}


if __name__ == "__main__":
    # python3 tts.py check Word1 Word2 ...  -> prints how Kokoro will pronounce them
    if len(sys.argv) > 2 and sys.argv[1] == "check":
        for w, p in phonemes(sys.argv[2:]).items():
            print(f"{w:20s} {p}")
