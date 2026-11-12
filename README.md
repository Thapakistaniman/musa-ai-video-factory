# Musa AI Video Factory

A cloud-ready pipeline for vertical 3D explainer shorts using Google Veo 3.1 and FFmpeg. **No Runway or Higgsfield.** Video generation is opt-in and may incur charges; dry-run is the default.

## Quick start

- Python 3.11+
- Install FFmpeg
- `pip install -e .`
- `cp .env.example .env` and set `GOOGLE_API_KEY` only when ready to generate
- `musa-video new --topic "How do black holes work?" --scenes 5`
- Review `projects/<slug>/prompts.md` and storyboard before generation
- Dry run: `musa-video generate projects/<slug>`
- Paid/usage-billed generation: `musa-video generate projects/<slug> --generate`
- Render: `musa-video assemble projects/<slug>`

## iPhone / cloud workflow

Use GitHub Actions → Actions → Musa Video Factory (manual) → Run workflow. The workflow creates a project and uploads its project files as an artifact. Add `GOOGLE_API_KEY` in repository Settings → Secrets and variables → Actions only if you explicitly want to enable Veo generation. Never put keys in source code or chat.

## Important

Veo model availability, API parameters, quotas, pricing and regional access depend on your Google account. Verify current terms and billing before enabling generation. This repository does not promise free generations. The initial workflow is manual, not an unattended auto-publisher.

## Pipeline

1. Create a topic brief and scene storyboard.
2. Review distinct scene prompts and visual continuity.
3. Generate clips through the Google Gen AI SDK only with explicit `--generate`.
4. Add narration and assemble a vertical MP4 with FFmpeg.

See `.env.example` for configuration and `docs/ROADMAP.md` for planned improvements.
