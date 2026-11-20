# Stickbits Hindi puzzle production
Read README.md, docs/REFERENCE_ANALYSIS.md and the direct-hindi-paheli skill. Use a new writable copy when making another episode. Verify that the correct option is unique under the stated rules. Write a complete Hindi script with a spoken payoff. Preserve the selected Kokoro Hindi voice hf_beta. Keep Roman Hindi headlines in the picture and provide the exact speech as SRT. Implement new puzzle-specific drawings and state changes. Run the local build and media verification before presenting an MP4. When a hosted sandbox blocks installation, report the exact missing dependency; the recorded sample can be rendered with existing-audio mode.

For reference matching, stage each clue inside the story world. For each main action identify an actor, a prop, a contact frame and a visible response. Compare hook, clue and reveal frames with the uploaded reference before final export.

## Voice direction for Stickbits

Use Voice A for Hindi Shorts. Use the unblended Kokoro hf_beta voice, language hi and a fixed speed of 1.01×. Write and synthesize each complete scene as one conversational take. Use a 65 Hz high-pass filter and constant gain for each take. Give the viewer time to guess at the end of a scene. The approved audition is in assets/voice_A.wav. For new episodes, synthesize the new dialogue with src/voice_preset.json.

Use write-visual-paheli for the draft and scorecard. Align the finished narration and render characters and props from src/visual_cues.json throughout the cut.
