import json, os, time
from pathlib import Path
from rich import print

def generate_project(project_dir: Path, confirmed: bool = False) -> None:
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    model = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")
    if not confirmed:
        print("[yellow]DRY RUN: no video requests submitted.[/yellow]")
        print(f"Configured model: {model}; scenes: {len(board['scenes'])}")
        print("If matching storyboard stills exist, they will be used as scene opening frames.")
        print("Review current Google pricing and access; pass --generate only with explicit approval.")
        return
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY missing. Configure it privately; never commit it.")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    out = project_dir / "clips"
    out.mkdir(exist_ok=True)
    for scene in board["scenes"]:
        target = out / f"scene_{scene['number']:02d}.mp4"
        if target.exists() and target.stat().st_size:
            print(f"[cyan]Already exists: {target.name}[/cyan]")
            continue
        prompt = " ".join([scene["visual_prompt"], "Camera: " + scene["camera"], scene["continuity"], scene.get("sound_design", "")])
        still = project_dir / "assets" / "story_images" / f"scene_{scene['number']:02d}.png"
        kwargs = {"model": model, "prompt": prompt, "config": types.GenerateVideosConfig(aspect_ratio="9:16", duration_seconds=8)}
        if still.exists():
            kwargs["image"] = types.Image(image_bytes=still.read_bytes(), mime_type="image/png")
            print(f"[cyan]Using scene keyframe {still.name}[/cyan]")
        print(f"[bold]Requesting scene {scene['number']}[/bold]")
        operation = client.models.generate_videos(**kwargs)
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
        videos = getattr(operation.response, "generated_videos", None) or []
        if not videos:
            raise RuntimeError(f"No video returned for scene {scene['number']}; stopping safely.")
        client.files.download(file=videos[0].video)
        videos[0].video.save(str(target))
        if not target.exists() or not target.stat().st_size:
            raise RuntimeError(f"Video not saved: {target}")
        print(f"[green]Saved {target}[/green]")
