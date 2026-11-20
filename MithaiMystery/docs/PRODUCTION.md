# Nau Laddoo · production sheet

**Premise.** Nine sweets look alike. Eight weigh the same and one is heavier because it has extra khoya. A two-pan balance can be used twice. Which first move guarantees a solution?

**For the writer.** The episode opens with the exact Hindi question from the approved Voice A audition. Keep the tray visible throughout the question.

**For the animator.** Each story-critical noun or verb triggers a physical entrance, motion, reaction or proof. The hook counts nine sweets and shows the hidden filling as an anonymous cutaway. Chanda enters on her name. The box arrives on डिब्बा and opens on खोला. Aman enters on अमन and brings the scale on तराज़ू. Place the alternatives on their spoken numbers. Both weight transfers, the level-beam marks and the outside-group bracket follow distinct words. The reveal shows the interior and reconstructs seven equals eight. The final weighing icon is crossed on नहीं. See src/visual_cues.json for every action and output/word_marks.json for measured local times. Dialogue amplitude drives mouth motion.

**For the narrator.** Use Voice A for Hindi Shorts. Use the unblended Kokoro hf_beta voice, language hi and a fixed speed of 1.01×. Write and synthesize each complete scene as one conversational take. Use a 65 Hz high-pass filter and constant gain for each take. Give the viewer time to guess at the end of a scene. The approved audition is in assets/voice_A.wav. For new episodes, synthesize the new dialogue with src/voice_preset.json.

**For sound.** The balance contacts, option taps and four-note reveal are synthesized in `make_mix()`. They sit below the narration. The package contains a clean WAV and a separate mixed WAV. The MP4 uses AAC at 48 kHz and fast-start metadata.

## Why the solution is fair
Split the nine sweets into groups of three. Weigh 1–3 against 4–6. A tilt identifies the heavier trio. A tie identifies 7–9. From the identified trio, weigh one against another. A tilt identifies the heavy sweet; a tie identifies the one left out. This covers all nine possible hidden positions. Four versus four can leave four candidates after a tilt. One versus one can leave seven after a tie. One remaining weighing has only three outcomes. The sample plays the tie/tie branch, where number nine was never on the scale.

## Editor’s handoff
Open `output/timeline.json` for actual times, spoken copy, emotion, speed, holds, headline and visible action per cue. Open `src/story.json` to change the inputs. Each row stores cue ID, Hindi speech, Roman transcript, headline line 1, headline line 2, voice speed, post-speech hold, intention and action. The demo’s ten cue IDs drive scene selection. Add or change renderer branches for a different puzzle. Work in a fresh episode directory to preserve previous exports.

## Validation of the delivered sample
The opening of the clean narration stem matches the selected audition sample for sample. The remaining scenes use the same narrator and speed. Subtitle and shot boundaries come from measured speech durations.

## Credits and dependencies
The shop, presenter, sweets and brass balance are original illustrations generated from the included vector and drawing sources. All Foley is synthesized for this project. The font directory includes the DejaVu license. The model directory includes the Kokoro model license. The four Hindi style arrays are repackaged from the official v1.0 voice bank. The selected voice is hf_beta.

- Kokoro model and license: https://huggingface.co/hexgrad/Kokoro-82M
- Voice inventory: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- ONNX release: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
- Project skill location in Claude Code: https://code.claude.com/docs/en/skills
- Custom skill upload in Claude: https://support.claude.com/en/articles/12512180-use-skills-in-claude
