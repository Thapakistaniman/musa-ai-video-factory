import base64, os
from pathlib import Path
from rich import print

def generate_lyria_track(output: Path, prompt: str, confirmed: bool = False) -> Path:
    """Generate a 30-second original instrumental with Vertex AI Lyria 002."""
    if not confirmed:
        print("[yellow]DRY RUN: no music-generation request sent.[/yellow]")
        print("Lyria 002 generates a 30-second WAV; Google Cloud billing and credentials are required.")
        return output
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    if not project:
        raise RuntimeError("Set GOOGLE_CLOUD_PROJECT for Vertex AI Lyria.")
    try:
        import google.auth
        from google.auth.transport.requests import Request
        import requests
    except ImportError as exc:
        raise RuntimeError("Install Google Cloud dependencies with pip install -e '.[cloud]'.") from exc
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())
    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/lyria-002:predict"
    response = requests.post(url, headers={"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json"}, json={"instances": [{"prompt": prompt, "negative_prompt": "copyrighted song, recognizable melody, artist imitation, speech, clipping"}], "parameters": {}}, timeout=180)
    response.raise_for_status()
    data = response.json()
    predictions = data.get("predictions", [])
    if not predictions or not predictions[0].get("audioContent"):
        raise RuntimeError("Lyria returned no audio content.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(base64.b64decode(predictions[0]["audioContent"]))
    if not output.exists() or output.stat().st_size < 1024:
        raise RuntimeError("Lyria audio file is empty or incomplete.")
    print(f"[green]Generated original Lyria track:[/green] {output}")
    return output
