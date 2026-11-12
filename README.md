# Musa AI Video Factory

A modular production pipeline for TikTok, Instagram Reels, YouTube Shorts and landscape YouTube videos. The target is polished, story-led video: real generated motion, distinct scenes, coherent characters/subjects, narration, music, subtitles, sound design, thumbnails and platform-specific publishing copy.

**Video provider:** Google Veo 3.1. **Image provider:** Gemini image generation. **Editing:** FFmpeg. No Runway or Higgsfield.

## What is implemented
- Topic project generator with five narrative beats and a scene-by-scene storyboard.
- Character/subject bible and continuity instructions to reduce visual drift.
- Opt-in vertical AI storyboard-image generation (one distinct image per scene).
- Opt-in Veo clip generation; dry-run is the default.
- Optional TTS narration (Edge TTS), SRT caption generation and original synthesized ambient audio bed.
- FFmpeg assembly with burned-in captions and voice/music mix.
- Manual GitHub Actions cloud workflow and downloadable project artifact.
- Editorial quality checklist and platform publishing-pack template.

## Quick start
Python 3.11+ and FFmpeg required.

```bash
pip install -e '.[tts]'
cp .env.example .env
musa-video doctor
musa-video new --topic "How does a black hole work?" --language en --scenes 5
```

Review and edit:
- `projects/<slug>/character_bible.md`
- `projects/<slug>/storyboard.json`
- `projects/<slug>/prompts.md`
- `projects/<slug>/publishing_pack.md`

Generate storyboard stills only after approving usage:
```bash
musa-video images projects/<slug> --generate
```

Generate moving Veo clips only after checking model access and cost:
```bash
musa-video generate projects/<slug> --generate
```

Create narration after replacing the storyboard narration placeholders:
```bash
musa-video narrate projects/<slug> --voice en-US-GuyNeural
musa-video captions projects/<slug>
musa-video music projects/<slug> --duration 40
musa-video assemble projects/<slug>
```

The original ambient music command creates a simple synthesized pad, not a finished commercial soundtrack. For professional results, add properly licensed music and sound effects to `assets/` and keep the license/source record.

## iPhone / cloud
Open repository → Actions → **Musa Video Factory (manual)** → Run workflow. The manual workflow creates the storyboard, optionally generates Veo clips only when the checkbox is enabled, assembles the MP4, and uploads the project as an artifact. Add `GOOGLE_API_KEY` under Settings → Secrets and variables → Actions. Never paste API keys into chat or source code.

## Billing and provider limits
Image and video generation can incur charges. Dry-run is the default and every paid generation path requires an explicit `--generate` flag or workflow checkbox. Check current Google model availability, region, quotas and pricing before running. Veo 3.1 has different model IDs and capabilities depending on Gemini API versus Vertex AI; configure the exact supported ID in `VEO_MODEL` and confirm that the authentication method matches your account. See Google's [Veo 3.1 documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate) and [video generation guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/generate-videos-from-text).

## Important quality limitation
AI output is not guaranteed to be perfect. Character consistency, physics, lip sync, typography and scene continuity require review and sometimes regeneration. This repository does not auto-publish. Watch the complete video, verify rights, and approve every final export before posting.

See [Quality Standard](docs/QUALITY_STANDARD.md) and [Roadmap](docs/ROADMAP.md).
