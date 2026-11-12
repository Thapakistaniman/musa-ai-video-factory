import os, shutil, typer
from pathlib import Path
from dotenv import load_dotenv
from rich import print
from .project import create_project
from .script import write_script
from .veo import generate_project
from .images import generate_story_images
from .captions import create_captions
from .audio import make_original_ambient_bed
from .music_ai import generate_lyria_track
from .assemble import assemble

load_dotenv()
app = typer.Typer(no_args_is_help=True, help="Create vertical AI explainer videos.")

@app.command()
def new(topic: str = typer.Option(..., help="Video topic"), language: str = typer.Option("en"), scenes: int = typer.Option(5, min=1, max=5)):
    path = create_project(topic, language, scenes)
    print(f"[green]Project created:[/green] {path}")
    print(f"Review prompts: {path / 'prompts.md'}")

@app.command()
def write(project_dir: Path, generate: bool = typer.Option(False, "--generate", help="Explicitly request AI scriptwriting; usage may be billed.")):
    write_script(project_dir, confirmed=generate)

@app.command()
def generate(project_dir: Path, generate: bool = typer.Option(False, "--generate", help="Explicitly submit Veo requests; usage may be billed.")):
    generate_project(project_dir, confirmed=generate)

@app.command()
def images(project_dir: Path, generate: bool = typer.Option(False, "--generate", help="Explicitly request AI images; usage may be billed.")):
    generate_story_images(project_dir, confirmed=generate)

@app.command()
def captions(project_dir: Path):
    print(f"[green]Captions saved:[/green] {create_captions(project_dir)}")

@app.command()
def music(project_dir: Path, duration: int = typer.Option(40, min=5, max=300)):
    target = project_dir / "assets" / "music_bed.mp3"
    print(f"[green]Original ambient bed saved:[/green] {make_original_ambient_bed(target, duration)}")


@app.command("music-ai")
def music_ai(project_dir: Path, prompt: str = typer.Option("Cinematic, modern instrumental score for a short-form explainer: energetic opening, curious tension, uplifting payoff, polished electronic textures and orchestral accents; no vocals.", help="Describe the original soundtrack"), generate: bool = typer.Option(False, "--generate", help="Explicitly request paid Lyria generation.")):
    target = project_dir / "assets" / "music_bed.wav"
    generate_lyria_track(target, prompt, confirmed=generate)

@app.command("assemble")
def assemble_command(project_dir: Path, platform: str = typer.Option("shorts", help="tiktok, reels, shorts or youtube")):
    print(f"[green]Rendered:[/green] {assemble(Path(project_dir), platform=platform)}")

@app.command()
def doctor():
    print(f"FFmpeg: {shutil.which('ffmpeg') or 'not found'}")
    print(f"Google API key: {'configured' if os.getenv('GOOGLE_API_KEY') else 'not configured (fine for dry runs)'}")
    print(f"Veo model: {os.getenv('VEO_MODEL', 'veo-3.1-generate-preview')}")
    print(f"Image model: {os.getenv('IMAGE_MODEL', 'gemini-3.1-flash-image')}")
    print(f"Script model: {os.getenv('SCRIPT_MODEL', 'gemini-3.1-flash-lite')}")

@app.command()
def narrate(project_dir: Path, text: str = typer.Option(""), voice: str = typer.Option("", help="Edge TTS voice; auto-selects Dutch or English when blank.")):
    try:
        import asyncio, edge_tts
    except ImportError as exc:
        raise typer.BadParameter("Install optional TTS with: pip install -e '.[tts]'") from exc
    if not text:
        import json
        board = json.loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
        text = " ".join(s["narration"] for s in board["scenes"])
        if "[" in text and "]" in text:
            raise typer.BadParameter("Replace the storyboard narration placeholders before generating speech.")
    if not voice:
        import json
        language = json.loads((project_dir / "brief.json").read_text(encoding="utf-8")).get("language", "en")
        voice = {"nl": "nl-NL-MaartenNeural", "en": "en-US-GuyNeural"}.get(language, "en-US-GuyNeural")
    target = project_dir / "assets" / "narration.mp3"
    asyncio.run(edge_tts.Communicate(text, voice).save(str(target)))
    print(f"[green]Narration saved:[/green] {target}")

if __name__ == "__main__":
    app()
