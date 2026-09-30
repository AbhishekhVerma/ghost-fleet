"""The watch page's media must exist and agree with each other."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "dashboard" / "media"
WATCH = (ROOT / "dashboard" / "watch.html").read_text(encoding="utf-8")


def test_watch_page_references_existing_media():
    refs = set(re.findall(r'(?:src|poster|href)="(media/[^"]+)"', WATCH)) | {"media/chapters.json"}
    missing = [r for r in refs if not (ROOT / "dashboard" / r).exists()]
    assert not missing, missing


def test_subtitle_files_agree():
    srt = (MEDIA / "ghost-fleet-demo.srt").read_text(encoding="utf-8")
    vtt = (MEDIA / "ghost-fleet-demo.vtt").read_text(encoding="utf-8")
    assert vtt.startswith("WEBVTT")
    assert len(re.findall(r"-->", srt)) == len(re.findall(r"-->", vtt)) > 0


def test_chapters_are_ordered_and_within_the_video():
    chapters = json.loads((MEDIA / "chapters.json").read_text(encoding="utf-8"))
    starts = [c["start"] for c in chapters]
    assert starts == sorted(starts) and starts[0] == 0
    last_cue = re.findall(r"--> (\d{2}):(\d{2}):(\d{2}),(\d{3})", (MEDIA / "ghost-fleet-demo.srt").read_text(encoding="utf-8"))[-1]
    h, m, s, ms = map(int, last_cue)
    assert starts[-1] < h * 3600 + m * 60 + s + ms / 1000


def test_video_fits_github_file_limits():
    assert (MEDIA / "ghost-fleet-demo.mp4").stat().st_size < 50_000_000
