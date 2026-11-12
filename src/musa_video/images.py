import json, os
from pathlib import Path
from rich import print

def generate_story_images(project_dir: Path, confirmed: bool = False) -> None:
    board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
    if not confirmed:
        print("[yellow]DRY RUN: no image requests sent.[/yellow]")
        print(f"Would create {len(board['scenes'])} vertical storyboard images.")
        return
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY missing. Configure it as a private environment variable.")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    model = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image")
    out = project_dir / "assets" / "story_images"
    out.mkdir(parents=True, exist_ok=True)
    for scene in board["scenes"]:
        target = out / f"scene_{scene['number']:02d}.png"
        if target.exists() and target.stat().st_size:
            continue
        prompt = "Create one polished vertical 9:16 cinematic 3D storyboard frame. " + scene["visual_prompt"] + " This is a single still frame, not a collage, no panels, no written text."
        response = client.models.generate_content(model=model, contents=prompt, config=types.GenerateContentConfig(response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="9:16", image_size="1K")))
        saved = False
        for part in response.parts:
            if getattr(part, "inline_data", None) is not None:
                part.as_image().save(str(target))
                saved = True
                break
        if not saved:
            raise RuntimeError(f"Image model returned no image for scene {scene['number']}; stopping safely.")
        print(f"[green]Saved storyboard image:[/green] {target}")
