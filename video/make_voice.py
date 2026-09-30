"""Generate the narration, one clip per scene, with ElevenLabs.

Writes video/build/audio/<scene>.mp3 and video/build/timings.json (clip
duration plus character-level timestamps, used for the subtitles).
Needs ELEVENLABS_API_KEY in the environment. Clips already generated are
reused, so a rerun only spends characters on changed or missing scenes.

Usage: python video/make_voice.py [--only title,problem] [--model eleven_v4]
"""

import argparse
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
AUDIO = BUILD / "audio"
TIMINGS = BUILD / "timings.json"
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"


def duration(path: Path) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(path)])
    return float(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="")
    parser.add_argument("--model", default="eleven_v4")
    args = parser.parse_args()

    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    spec = json.loads((HERE / "narration.json").read_text(encoding="utf-8"))
    voice = spec["voice"]["voice_id"]
    only = {s for s in args.only.split(",") if s}

    AUDIO.mkdir(parents=True, exist_ok=True)
    timings = json.loads(TIMINGS.read_text(encoding="utf-8")) if TIMINGS.exists() else {}

    for scene in spec["scenes"]:
        sid, text = scene["id"], scene["text"]
        digest = hashlib.sha1(f"{voice}|{args.model}|{text}".encode()).hexdigest()
        mp3 = AUDIO / f"{sid}.mp3"
        if only and sid not in only:
            continue
        if mp3.exists() and timings.get(sid, {}).get("digest") == digest:
            print(f"  = {sid:<11} cached  {timings[sid]['duration']:.2f}s")
            continue

        r = requests.post(API.format(voice=voice), headers={"xi-api-key": key}, timeout=120, json={
            "text": text,
            "model_id": args.model,
            "output_format": "mp3_44100_192",
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.8, "style": 0.15,
                               "use_speaker_boost": True, "speed": 0.95},
        })
        if r.status_code != 200:
            raise SystemExit(f"{sid}: HTTP {r.status_code} {r.text[:300]}")
        body = r.json()
        mp3.write_bytes(base64.b64decode(body["audio_base64"]))
        align = body.get("alignment") or {}
        timings[sid] = {
            "digest": digest,
            "model": args.model,
            "duration": duration(mp3),
            "chars": align.get("characters", []),
            "starts": align.get("character_start_times_seconds", []),
            "ends": align.get("character_end_times_seconds", []),
        }
        TIMINGS.write_text(json.dumps(timings), encoding="utf-8")
        print(f"  + {sid:<11} {timings[sid]['duration']:.2f}s  ({len(text)} chars)")

    total = sum(t["duration"] for t in timings.values())
    print(f"narration total {total:.1f}s")


if __name__ == "__main__":
    main()
