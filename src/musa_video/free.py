import json, shutil, subprocess
from pathlib import Path

def _run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-2500:] or "Free render failed")

def render_free(project_dir: Path) -> list[Path]:
    """Render deterministic, zero-API-cost motion-graphic scenes with FFmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required. Install FFmpeg and retry.")
    board_path = project_dir / "storyboard.json"
    board = json.loads(board_path.read_text(encoding="utf-8"))
    clips_dir = project_dir / "clips"
    assets_dir = project_dir / "assets" / "free_scene_text"
    clips_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    title = str(board.get("title", "Musa Video Factory"))
    palette = ["0x101827", "0x172554", "0x312e81", "0x164e63", "0x1f2937"]
    results = []
    for index, scene in enumerate(board["scenes"]):
        number = int(scene["number"])
        target = clips_dir / f"scene_{number:02d}.mp4"
        beat = str(scene.get("beat", "SCENE")).replace("_", " ")
        narration = str(scene.get("narration", "")).strip()
        headline = narration if narration and not narration.startswith("[") else f"{title} — {beat.title()}"
        # FFmpeg reads text from files so punctuation in user topics cannot break filter syntax.
        headline_file = assets_dir / f"scene_{number:02d}.txt"
        headline_file.write_text(headline, encoding="utf-8")
        label_file = assets_dir / f"label_{number:02d}.txt"
        label_file.write_text(f"SCENE {number:02d}  /  {beat}", encoding="utf-8")
        duration = max(4, min(15, int(scene.get("duration_seconds", 8))))
        color = palette[index % len(palette)]
        vf = (
            "zoompan=z='min(zoom+0.00035,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            "d=1:s=1080x1920:fps=30,"
            f"drawbox=x=70:y=180:w=940:h=2:color=white@0.65:t=fill,"
            f"drawtext=textfile='{label_file.as_posix()}':fontcolor=0x93c5fd:fontsize=30:x=80:y=230,"
            f"drawtext=textfile='{headline_file.as_posix()}':fontcolor=white:fontsize=58:line_spacing=18:"
            "x=80:y=(h-text_h)/2:box=1:boxcolor=black@0.18:boxborderw=24,"
            "drawbox=x=70:y=1580:w=940:h=3:color=white@0.4:t=fill,"
            "drawtext=text='MUSA  /  VIDEO FACTORY':fontcolor=white@0.7:fontsize=24:x=80:y=1640,"
            "fade=t=in:st=0:d=0.45,fade=t=out:st=" + str(duration-0.5) + ":d=0.5,format=yuv420p"
        )
        _run([ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c={color}:s=1080x1920:r=30:d={duration}",
              "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
              "-t", str(duration), "-movflags", "+faststart", str(target)])
        results.append(target)
    return results

def write_free_narration(project_dir: Path) -> Path:
    """Fill safe, editable narration scaffolds without calling a paid or remote model."""
    board_path = project_dir / "storyboard.json"
    board = json.loads(board_path.read_text(encoding="utf-8"))
    brief = json.loads((project_dir / "brief.json").read_text(encoding="utf-8"))
    topic = brief.get("topic", board.get("title", "dit onderwerp"))
    language = brief.get("language", "nl")
    if language == "nl":
        templates = [
            f"Stel je voor: {topic}. Dit is waar we naar gaan kijken.",
            f"Eerst zetten we {topic} in context. Let op de belangrijkste onderdelen.",
            "Nu zie je hoe de verschillende onderdelen met elkaar samenhangen.",
            "Het interessante zit in wat er daarna gebeurt. Kijk naar het verschil.",
            f"En dat is de kern van {topic}. Onthoud vooral dit inzicht."
        ]
    else:
        templates = [
            f"Imagine this: {topic}. Here is what we are going to explore.",
            f"First, let's put {topic} into context. Notice the key elements.",
            "Now see how the different parts connect and work together.",
            "Here is where it gets interesting. Watch what happens next.",
            f"And that is the key idea behind {topic}. Remember this insight."
        ]
    for i, scene in enumerate(board["scenes"]):
        old = str(scene.get("narration", ""))
        if not old.strip() or old.startswith("["):
            scene["narration"] = templates[min(i, len(templates)-1)]
    board_path.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")
    return board_path
