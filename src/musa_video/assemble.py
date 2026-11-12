import json, shutil, subprocess
from pathlib import Path
def _run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-2500:] or "FFmpeg failed")
def assemble(project_dir: Path) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required; install it and retry.")
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    clips = [project_dir / "clips" / f"scene_{s['number']:02d}.mp4" for s in board["scenes"]]
    missing = [str(p) for p in clips if not p.is_file() or not p.stat().st_size]
    if missing:
        raise FileNotFoundError("Missing clips:\n" + "\n".join(missing))
    concat = project_dir / "clips" / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in clips), encoding="utf-8")
    out = project_dir / "output"
    out.mkdir(exist_ok=True)
    silent, final = out / "picture.mp4", out / "final.mp4"
    _run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(silent)])
    narration = project_dir / "assets" / "narration.mp3"
    if narration.exists():
        _run([ffmpeg, "-y", "-i", str(silent), "-i", str(narration), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)])
    else:
        shutil.copy2(silent, final)
    return final
