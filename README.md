# Musa AI Video Factory

A free-first production pipeline for TikTok, Instagram Reels, YouTube Shorts and landscape YouTube.

## Free mode (default and safe)
The GitHub Actions workflow **Musa Video Factory — FREE** uses no Google API key, no paid generation API, no paid cloud GPU and no billing secrets. It creates a project, fills an editable narration scaffold, renders distinct animated motion-graphic scenes with FFmpeg, generates voice-over with Edge TTS, creates SRT captions, synthesizes an original ambient audio bed, assembles the selected aspect ratio and saves all project files as a downloadable Actions artifact.

**Important quality distinction:** this default free cloud workflow creates animated motion graphics, not photorealistic AI-generated 3D footage. It is deliberately transparent rather than pretending that still images are real AI video. Voice generation uses the Edge TTS service and therefore requires network access; it does not use a paid API key, but service availability and terms are controlled by Microsoft.

## Run from iPhone
1. Open this repository on GitHub.
2. Go to **Actions**.
3. Select **Musa Video Factory — FREE**.
4. Tap **Run workflow**, enter topic, language, scene count and platform.
5. Wait for the workflow to finish.
6. Open the run's **Artifacts** section and download the ZIP containing the MP4 and editable project.

No secrets or payment setup are needed for the free workflow.

## Local AI video mode (free model, your own GPU)
For real generated video motion, use ComfyUI with open-weight Wan 2.2. The official ComfyUI documentation says the Wan 2.2 TI2V 5B workflow can fit on 8 GB VRAM with native offloading, though speed and usable resolution depend on the GPU, system RAM and settings. The 14B models need substantially more resources. See the [official ComfyUI Wan 2.2 guide](https://docs.comfy.org/tutorials/video/wan/wan2_2) and [Wan 2.2 model card](https://huggingface.co/Comfy-Org/Wan-2.2). Model license is Apache 2.0 per the model documentation. Model weights are large and must be downloaded locally. No paid generation API is required, but electricity and hardware are not literally free.

The next integration step is to connect this project to a local ComfyUI worker. The correct model/workflow depends on the exact GPU and VRAM in the user's PC. GitHub-hosted Actions runners cannot use the user's local GPU automatically.

## Local quick start
Python 3.11+ and FFmpeg required.

```bash
pip install -e '.[tts]'
musa-video new --topic "How does a black hole work?" --language en --scenes 5
musa-video free-script projects/how-does-a-black-hole-work
musa-video free-render projects/how-does-a-black-hole-work
musa-video narrate projects/how-does-a-black-hole-work
musa-video captions projects/how-does-a-black-hole-work
musa-video music projects/how-does-a-black-hole-work --duration 40
musa-video assemble projects/how-does-a-black-hole-work --platform shorts
```

## Paid providers
Google Gemini image/script generation, Veo video generation and Vertex Lyria are not part of the free workflow. Their commands remain separate, opt-in developer features and are never called by the free Actions workflow. Do not enable them unless you intentionally choose a paid provider and verify current pricing.

## Quality and roadmap
The free workflow is a working automated editing pipeline, not a claim of perfect photorealistic AI output. Review factual narration, voice pronunciation, captions, safe areas, transitions and final export before publishing. Auto-publishing is not enabled.
