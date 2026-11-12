import json, shutil, subprocess
from pathlib import Path

def _run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:] or "FFmpeg failed")

def _has_audio(ffprobe: str, path: Path) -> bool:
    result = subprocess.run([ffprobe, "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return result.returncode == 0 and bool(result.stdout.strip())

def _filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:")

def assemble(project_dir: Path) -> Path:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("FFmpeg and ffprobe are required; install the FFmpeg package.")
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    clips = [project_dir / "clips" / f"scene_{s['number']:02d}.mp4" for s in board["scenes"]]
    missing = [str(p) for p in clips if not p.is_file() or not p.stat().st_size]
    if missing:
        raise FileNotFoundError("Missing clips:\\n" + "\\n".join(missing))
    concat = project_dir / "clips" / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve().as_posix()}'\\n" for p in clips), encoding="utf-8")
    out = project_dir / "output"
    out.mkdir(exist_ok=True)
    picture, final = out / "picture.mp4", out / "final.mp4"
    _run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p", "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(picture)])
    captions = project_dir / "assets" / "captions.srt"
    video_input = picture
    if captions.exists() and captions.stat().st_size:
        subtitled = out / "subtitled.mp4"
        vf = "subtitles='" + _filter_path(captions) + "':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=220'"
        _run([ffmpeg, "-y", "-i", str(video_input), "-vf", vf, "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k", str(subtitled)])
        video_input = subtitled
    narration = project_dir / "assets" / "narration.mp3"
    music_wav = project_dir / "assets" / "music_bed.wav"\n    music = music_wav if music_wav.exists() else project_dir / "assets" / "music_bed.mp3"
    has_source_audio = _has_audio(ffprobe, video_input)
    inputs = [video_input]
    if narration.exists():
        inputs.append(narration)
    if music.exists():
        inputs.append(music)
    cmd = [ffmpeg, "-y"]
    for item in inputs:
        if item == music:
            cmd += ["-stream_loop", "-1", "-i", str(item)]
        else:
            cmd += ["-i", str(item)]
    tracks = []
    graph_parts = []
    index = 1
    if has_source_audio:
        graph_parts.append("[0:a]volume=0.55[source]")
        tracks.append("[source]")
    if narration.exists():
        graph_parts.append(f"[{index}:a]volume=1.0[voice]")
        tracks.append("[voice]")
        index += 1
    if music.exists():
        graph_parts.append(f"[{index}:a]volume=0.10[music]")
        tracks.append("[music]")
    if tracks:
        graph_parts.append("".join(tracks) + f"amix=inputs={len(tracks)}:duration=first:dropout_transition=2,alimiter=limit=0.95[aout]")
        cmd += ["-filter_complex", ";".join(graph_parts), "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)]
    else:
        shutil.copy2(video_input, final)
    return final
