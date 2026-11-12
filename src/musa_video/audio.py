from pathlib import Path
import shutil, subprocess

def make_original_ambient_bed(output: Path, duration: int = 40) -> Path:
    """Create a simple original synthesized ambient bed; no sampled/copyrighted recording."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to synthesize a backing bed.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # A deliberately subtle, generated chord pad. This is a placeholder score, not a commercial soundtrack.
    tones = [110.00, 164.81, 220.00, 261.63]
    sources = [f"sine=f={hz}:d={duration}:sample_rate=44100,volume=0.025" for hz in tones]
    graph = ";".join(f"[{i}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}]" for i in range(len(tones)))
    graph += ";" + "".join(f"[a{i}]" for i in range(len(tones))) + f"amix=inputs={len(tones)}:normalize=0,afade=t=in:st=0:d=2,afade=t=out:st={max(0,duration-3)}:d=3,alimiter=limit=0.8[out]"
    cmd = [ffmpeg, "-y"]
    for hz in tones:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency={hz}:duration={duration}:sample_rate=44100"]
    cmd += ["-filter_complex", graph, "-map", "[out]", "-c:a", "aac", "-b:a", "160k", str(output)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError(run.stderr[-2000:])
    return output
