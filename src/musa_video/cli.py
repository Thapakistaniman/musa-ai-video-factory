import os, shutil, typer
from pathlib import Path
from dotenv import load_dotenv
from rich import print
from .project import create_project
from .veo import generate_project
from .assemble import assemble
load_dotenv()
app = typer.Typer(no_args_is_help=True, help="Create vertical AI explainer videos.")
@app.command()
def new(topic: str = typer.Option(..., help="Video topic"), language: str = typer.Option("en"), scenes: int = typer.Option(5, min=1, max=5)):
    path = create_project(topic, language, scenes)
    print(f"[green]Project created:[/green] {path}")
    print(f"Review prompts: {path / 'prompts.md'}")
@app.command()
def generate(project_dir: Path, generate: bool = typer.Option(False, "--generate", help="Explicitly submit Veo requests; usage may be billed.")):
    generate_project(project_dir, confirmed=generate)
@app.command("assemble")
def assemble_command(project_dir: Path):
    print(f"[green]Rendered:[/green] {assemble(Path(project_dir))}")
@app.command()
def doctor():
    print(f"FFmpeg: {shutil.which('ffmpeg') or 'not found'}")
    print(f"Google API key: {'configured' if os.getenv('GOOGLE_API_KEY') else 'not configured (fine for dry runs)'}")
    print(f"Veo model: {os.getenv('VEO_MODEL', 'veo-3.1-generate-preview')}")
@app.command()
def narrate(project_dir: Path, text: str = typer.Option(""), voice: str = typer.Option("en-US-GuyNeural")):
    try:
        import asyncio, edge_tts
    except ImportError as exc:
        raise typer.BadParameter("Install optional TTS: pip install -e '.[tts]'") from exc
    if not text:
        board = __import__("json").loads((project_dir / "storyboard.json").read_text(encoding="utf-8"))
        text = " ".join(s["narration"] for s in board["scenes"])
    target = project_dir / "assets" / "narration.mp3"
    asyncio.run(edge_tts.Communicate(text, voice).save(str(target)))
    print(f"[green]Narration saved:[/green] {target}")
