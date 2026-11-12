import json, shutil, subprocess
from pathlib import Path

def _run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:] or "FFmpeg failed")

def _filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:")

def assemble(project_dir: Path) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required; install it and retry.")
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    clips = [project_dir / "clips" / f"scene_{s['number']:02d}.mp4" for s in board["scenes"]]
    missing = [str(p) for p in clips if not p.is_file() or not p.stat().st_size]
    if missing:
        raise FileNotFoundError("Missing clips:\\n" + "\\n".join(missing))
    concat = project_dir / "clips" / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve().as_posix()}'\\n" for p in clips), encoding="utf-8")
    out = project_dir / "output"
    out.mkdir(exist_ok=True)
    silent, final = out / "picture.mp4", out / "final.mp4"
    _run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19", str(silent)])
    narration = project_dir / "assets" / "narration.mp3"
    music = project_dir / "assets" / "music_bed.mp3"
    captions = project_dir / "assets" / "captions.srt"
    video_input = str(silent)
    if captions.exists():
        subtitled = out / "subtitled.mp4"
        vf = "subtitles='" + _filter_path(captions) + "':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=220'"
        _run([ffmpeg, "-y", "-i", video_input, "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-an", str(subtitled)])
        video_input = str(subtitled)
    cmd = [ffmpeg, "-y", "-i", video_input]
    audio_inputs = []
    if narration.exists():
        cmd += ["-i", str(narration)]
        audio_inputs.append("1:a")
    if music.exists():
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        audio_inputs.append(f"{len(audio_inputs)+1}:a")
    if audio_inputs:
        if len(audio_inputs) == 2:
            graph = "[1:a]volume=1.0[voice];[2:a]volume=0.12[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[aout]"
        elif narration.exists():
            graph = "[1:a]alimiter=limit=0.95[aout]"
        else:
            graph = "[1:a]volume=0.18,alimiter=limit=0.95[aout]"
        cmd += ["-filter_complex", graph, "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)]
    else:
        shutil.copy2(video_input, final)
    return final
