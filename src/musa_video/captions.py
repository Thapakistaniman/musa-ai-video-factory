import json
from pathlib import Path

def srt_time(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    h, rem = divmod(ms, 3_600_000); m, rem = divmod(rem, 60_000); s, milli = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{milli:03}"

def create_captions(project_dir: Path, output: Path | None = None) -> Path:
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    rows, cursor = [], 0.0
    for scene in board["scenes"]:
        text = scene.get("narration", "").strip()
        duration = float(scene.get("duration_seconds", 8))
        if text and not text.startswith("["):
            rows.extend([str(len(rows)//4+1), f"{srt_time(cursor)} --> {srt_time(cursor+duration)}", text, ""])
        cursor += duration
    target = output or project_dir / "assets" / "captions.srt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(rows), encoding="utf-8")
    return target
