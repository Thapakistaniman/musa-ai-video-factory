import json, os, time
from pathlib import Path
from rich import print

def generate_project(project_dir: Path, confirmed: bool = False) -> None:
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    model = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")
    if not confirmed:
        print("[yellow]DRY RUN: no video requests submitted.[/yellow]")
        print(f"Configured model: {model}; scenes: {len(board['scenes'])}")
        print("Review current Google pricing and access; pass --generate only with explicit approval.")
        return
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY missing. Configure privately; never commit it.")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    out = project_dir / "clips"
    out.mkdir(exist_ok=True)
    for s in board["scenes"]:
        target = out / f"scene_{s['number']:02d}.mp4"
        if target.exists() and target.stat().st_size:
            print(f"[cyan]Already exists: {target.name}[/cyan]")
            continue
        prompt = " ".join([s["visual_prompt"], "Camera: " + s["camera"], s["continuity"]])
        operation = client.models.generate_videos(model=model, prompt=prompt, config=types.GenerateVideosConfig(aspect_ratio="9:16", duration_seconds=s["duration_seconds"]))
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
        videos = getattr(operation.response, "generated_videos", None) or []
        if not videos:
            raise RuntimeError(f"No video returned for scene {s['number']}; stopping safely.")
        client.files.download(file=videos[0].video)
        videos[0].video.save(str(target))
        if not target.exists() or not target.stat().st_size:
            raise RuntimeError(f"Video not saved: {target}")
        print(f"[green]Saved {target}[/green]")
