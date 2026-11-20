# Nau Laddoo
A 41.0-second Hindi animated puzzle for Stickbits. Watch `output/Nau_Laddoo.mp4`. Audition the hook, guess and answer in `output/Stickbits_Voice_A.mp3`. Recreate the sample with `python src/voice_preview.py`. The complete project includes the local Kokoro model, voice bank, editable art and recorded narration.

## Use in Claude
**Claude app.** Upload the separate `Direct_Hindi_Paheli_Claude.zip` under Customize → Skills → + → Create skill → Upload a skill. Enable it and use the prompt below. This compact skill includes the source starter, reference notes, fonts, Hindi voice bank and recorded example audio. For new narration, its setup downloads the pinned ONNX model once. The complete project ZIP already contains that model.

**Claude Code.** Extract the full project, open the MithaiMystery folder and invoke `/direct-hindi-paheli`. The skill lives in `.claude/skills/direct-hindi-paheli/`. Claude Code can also read the project instructions in CLAUDE.md.

**Prompt for your next episode**
> Use direct-hindi-paheli to make a new 35–45 second Stickbits Short in Hindi. Three tiffins are labeled roti, idli and mixed, and every label is wrong. Let me choose which one to sample, then prove the answer on screen. Use the shop animation as a visual reference and Kokoro hf_beta as the narrator. Show the options long enough to guess, keep the numbers and labels readable on a phone, and reveal the solution in this video. Work in a new episode folder. Install and verify the required tools in your sandbox, animate the tiffins and label swaps, and return a playable MP4, subtitles and editable project ZIP.

## Build in a Linux sandbox
Run from the extracted project directory. Use Python 3.12 for the tested configuration. No paid API, GPU, browser or Node.js is needed for this renderer.

| Command | Result |
|---|---|
| `bash setup.sh full` | Checks FFmpeg/ffprobe and encoders, installs missing Python packages in a project venv, verifies model hashes and synthesizes a Hindi phrase. |
| `bash build.sh full` | Runs setup, regenerates Hindi narration and subtitles, renders a short motion test and full sample, then checks the final file. |
| `bash build.sh existing-audio` | Re-renders the supplied sample using its bundled WAV and timeline. Useful in a sandbox without model-download access. |
| `bash build.sh art` | Installs/checks Inkscape when needed, regenerates the original SVG and PNG art from src/art.py, then exits. |
| `python src/verify.py` | Checks codec, geometry, frame rate, audio timing, subtitle count and full decode of the delivered MP4. |

The full build needs Bash, Python, NumPy, Pillow, FFmpeg with libx264 and AAC, ffprobe, kokoro-onnx 0.6.1, ONNX Runtime, SoundFile and the eSpeak NG phonemizer loaded by Kokoro. Pip resolves the speech runtime dependencies. SVG regeneration additionally uses Inkscape. PNG sprites and fonts ship with both versions. To edit the SVG files directly, export changed PNG counterparts into assets/sprites before rendering; running art.py regenerates the SVGs from code.

Setup reuses a working Python environment, otherwise it needs access to Python packages. Missing native tools require a Debian/Ubuntu package manager with installation privileges. A restricted hosted sandbox may need the full project with bundled weights, or a Linux environment that already provides the missing packages. For a different interpreter, set PYTHON_BIN to its executable before running setup. The setup smoke test confirms actual synthesis. Do not assume installation succeeded from the presence of the skill.

## Project map
| Path | Contents |
|---|---|
| docs/REFERENCE_ANALYSIS.md | Timestamped breakdown of both uploads and the editing patterns they demonstrate |
| docs/PRODUCTION.md | Creative choices, proof for all nine possible answers, palette, motion, voice direction, mix, credits and QA |
| .claude/skills/direct-hindi-paheli/ | Reusable Claude skill, editorial scorecard and a second worked puzzle |
| src/story.json and src/voice.py | Editable Hindi script, Roman captions, voice speeds, direction, pauses and Kokoro synthesis |
| src/art.py and assets/ | Original vector artwork, transparent puppet layers, sprites and bundled fonts |
| src/render.py | Timeline, staging, balance animation, sound cues, encoding and preview |
| models/ | Hindi voice bank and license. Full archive also includes the 92 MB INT8 ONNX model. |
| output/ | Full project: MP4, clean and mixed WAVs, Hindi and Roman SRTs, timing manifest and motion test. Compact upload: WAV, SRTs and timing manifest to rebuild the sample. |

For a production guide to writing and scaling new episodes, read the skill’s references/director-notes.md. Keep the A/B/C decision and its proof fair as the characters and setting change.

## Word-synced direction and scriptwriting
Use the Write Visual Paheli Claude ZIP for script writing, hook alternatives, clue design and the 20-point editorial scale. The full project includes both Claude skills. For a fresh full render, build.sh aligns all spoken words to the Voice A stem and renders from src/visual_cues.json. The existing-audio mode uses the bundled timing data. Each cue contains the triggering word, its occurrence and visible action. For an unrelated episode change the object art, direction and spoken anchors together. The director skill includes a copy of the full script rubric.
