import json, re
from pathlib import Path
BEATS = [("HOOK", "A striking visual reveal.", "fast macro push-in"), ("SETUP", "Establish the subject and scale with a reference object.", "wide establishing shot"), ("MECHANISM", "Reveal the hidden process with a readable 3D cutaway.", "smooth orbit and cutaway"), ("PAYOFF", "Show the consequence with a strong visual transformation.", "dynamic tracking shot"), ("REVEAL", "End on a memorable hero image that answers the hook.", "cinematic pull-back")]
def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "new-project"
def create_project(topic: str, language: str = "en", scenes: int = 5) -> Path:
    root = Path("projects") / slugify(topic)
    for name in ("assets", "clips", "audio", "output"):
        (root / name).mkdir(parents=True, exist_ok=True)
    brief = {"topic": topic, "language": language, "style": "cinematic stylized 3D explainer, polished materials, dramatic lighting", "aspect_ratio": "9:16", "scene_count": scenes}
    board = {"title": topic, "hook": f"What if you understood {topic} in under a minute?", "scenes": []}
    for i in range(scenes):
        beat, action, camera = BEATS[i]
        board["scenes"].append({"number": i+1, "duration_seconds": 8, "beat": beat, "narration": f"[Write concise {language} narration about {topic} for this beat.]", "visual_prompt": f"{brief['style']}. Subject: {topic}. Action: {action} Distinct composition. Vertical 9:16, clear focal subject, coherent physical motion, no text, logos or watermark.", "camera": camera, "continuity": "Maintain subject design, proportions, palette and world rules; vary action, framing and camera movement."})
    (root / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
    (root / "storyboard.json").write_text(json.dumps(board, indent=2), encoding="utf-8")
    lines = [f"# {topic}", "", f"**Hook:** {board['hook']}", "", "Review and rewrite prompts before generation.", ""]
    for s in board["scenes"]:
        lines += [f"## Scene {s['number']} — {s['beat']}", "", s["visual_prompt"], "", f"**Camera:** {s['camera']}", f"**Narration:** {s['narration']}", f"**Continuity:** {s['continuity']}", ""]
    (root / "prompts.md").write_text("\n".join(lines), encoding="utf-8")
    return root
