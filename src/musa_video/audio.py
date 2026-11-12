from pathlib import Path
import shutil, subprocess

def make_original_ambient_bed(output: Path, duration: int = 40) -> Path:
    """Create a simple original synthesized ambient pad; no sampled/copyrighted recording."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to synthesize a backing bed.")
    if duration < 5:
        raise ValueError("Duration must be at least five seconds.")
    output.parent.mkdir(parents=True, exist_ok=True)
    tones = [110.00, 164.81, 220.00, 261.63]
    graph = ";".join(
        f"[{i}:a]volume=0.025,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}]"
        for i in range(len(tones))
    )
    graph += ";" + "".join(f"[a{i}]" for i in range(len(tones)))
    graph += f"amix=inputs={len(tones)}:normalize=0,afade=t=in:st=0:d=2,afade=t=out:st={duration-3}:d=3,alimiter=limit=0.8[out]"
    cmd = [ffmpeg, "-y"]
    for hz in tones:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency={hz}:duration={duration}:sample_rate=44100"]
    cmd += ["-filter_complex", graph, "-map", "[out]", "-c:a", "aac", "-b:a", "160k", str(output)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-2000:])
    return output
