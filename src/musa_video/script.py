import json, os
from pathlib import Path
from rich import print

def write_script(project_dir: Path, confirmed: bool = False) -> None:
    board_path = project_dir / "storyboard.json"
    board = json.loads(board_path.read_text(encoding="utf-8"))
    if not confirmed:
        print("[yellow]DRY RUN: no text-generation request sent.[/yellow]")
        print(f"Would write narration for {len(board['scenes'])} scenes.")
        return
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY missing. Configure it privately.")
    from google import genai
    client = genai.Client(api_key=key)
    language = json.loads((project_dir / "brief.json").read_text(encoding="utf-8")).get("language", "en")
    prompt = f"""Write a fact-conscious, engaging short-form explainer narration in language code {language} about: {board['title']}.
Opening hook: {board['hook']}
Return ONLY a JSON array of exactly {len(board['scenes'])} strings, one spoken narration line for each scene in order.
Each line should be concise, natural to speak, avoid unsupported statistics, and connect into one story. No stage directions, markdown or labels."""
    model = os.getenv("SCRIPT_MODEL", "gemini-3.1-flash-lite")
    response = client.models.generate_content(model=model, contents=prompt)
    try:
        lines = json.loads(response.text)
    except Exception as exc:
        raise RuntimeError("Script model did not return valid JSON. No storyboard changes were saved.") from exc
    if not isinstance(lines, list) or len(lines) != len(board["scenes"]) or not all(isinstance(x, str) and x.strip() for x in lines):
        raise RuntimeError("Script model returned an unexpected number or type of narration lines.")
    for scene, line in zip(board["scenes"], lines):
        scene["narration"] = line.strip()
    board_path.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[green]Narration script saved:[/green] {board_path}")
