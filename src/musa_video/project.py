import json, re
from pathlib import Path

BEATS = [
    ("HOOK", "A striking visual reveal that creates an immediate question.", "fast macro push-in"),
    ("SETUP", "Establish the subject, environment and scale with a clear reference object.", "wide establishing shot"),
    ("MECHANISM", "Reveal the hidden process with a readable 3D cutaway or transformation.", "smooth orbit and cutaway"),
    ("PAYOFF", "Show the consequence with a strong visual contrast and physical action.", "dynamic tracking shot"),
    ("REVEAL", "End on a memorable hero image that answers the opening question.", "cinematic pull-back"),
]

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "new-project"

def create_project(topic: str, language: str = "en", scenes: int = 5) -> Path:
    if not 1 <= scenes <= len(BEATS):
        raise ValueError(f"Scenes must be between 1 and {len(BEATS)}.")
    root = Path("projects") / slugify(topic)
    for name in ("assets/story_images", "clips", "audio", "output"):
        (root / name).mkdir(parents=True, exist_ok=True)
    brief = {
        "topic": topic, "language": language,
        "style": "premium cinematic photorealistic 3D CGI explainer, physically based materials, lifelike textures, realistic anatomy and proportions, expressive cinematic lighting, volumetric atmosphere, detailed environments, high-end feature-film render quality",
        "aspect_ratio": "9:16", "scene_count": scenes,
        "audience": "general social video audience", "target_duration_seconds": scenes * 8,
    }
    character_bible = """# Subject / Character Bible

Before generation, fill this in and keep it unchanged across all scenes.

- Main subject name / description: define one unmistakable subject.
- Silhouette and proportions: specify body shape, scale and distinctive silhouette.
- Face / identifying details: specify stable eyes, facial structure, markings or surface details.
- Wardrobe / materials: exact clothing, materials, accessories and colors.
- Color palette: 3–5 fixed colors with lighting rules.
- Environment: define the world, time of day and recurring background elements.
- Motion language: define natural movement, weight, inertia and interaction with objects.
- Camera language: cinematic, deliberate, varied shot sizes; no repetitive digital zooms.
- Continuity rule: do not redesign, morph, recolor or replace the subject between shots.

For non-character explainers, define the recurring object/system instead of a character.
"""
    (root / "character_bible.md").write_text(character_bible, encoding="utf-8")
    board = {"title": topic, "hook": f"What if you understood {topic} in under a minute?", "scenes": []}
    for i in range(scenes):
        beat, action, camera = BEATS[i]
        board["scenes"].append({
            "number": i + 1, "duration_seconds": 8, "beat": beat,
            "narration": f"[Write concise, factual {language} narration for this beat about {topic}.]",
            "visual_prompt": f"{brief['style']}. Subject: {topic}. Action: {action} This scene must have a unique composition and a clear beginning, middle and end. Vertical 9:16, strong focal hierarchy, believable physical motion, realistic contact shadows and reflections, rich but coherent detail. No text, captions, logos or watermark.",
            "camera": camera,
            "continuity": "Follow character_bible.md exactly. Keep subject identity, proportions, palette, materials and world rules unchanged. Change action and framing from the previous scene; do not reuse the same shot.",
            "sound_design": "Use subtle scene-matched environmental sound and a clean transition; keep dialogue intelligible.",
        })
    (root / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
    (root / "storyboard.json").write_text(json.dumps(board, indent=2), encoding="utf-8")
    lines = [f"# {topic}", "", f"**Hook:** {board['hook']}", "", "Review facts, narration and prompts. Complete character_bible.md before generating.", ""]
    for s in board["scenes"]:
        lines += [f"## Scene {s['number']} — {s['beat']}", "", s["visual_prompt"], "", f"**Camera:** {s['camera']}", f"**Narration:** {s['narration']}", f"**Continuity:** {s['continuity']}", f"**Sound:** {s['sound_design']}", ""]
    (root / "prompts.md").write_text("\n".join(lines), encoding="utf-8")
    pack = f"""# Publishing pack — {topic}

Create a tailored title, description, thumbnail and caption for each platform after the final edit.

## TikTok
- Short title / hook:
- Caption:
- Hashtags:
- Cover text:

## Instagram Reels
- Caption:
- Hashtags:
- Cover text:

## YouTube Shorts
- Title (front-load the topic):
- Description:
- Hashtags:
- Thumbnail text:

## YouTube landscape
- Title:
- Description:
- Chapters:
- Thumbnail concept:

Do not auto-publish. Review factual claims, rights and platform-specific safe areas first.
"""
    (root / "publishing_pack.md").write_text(pack, encoding="utf-8")
    return root
