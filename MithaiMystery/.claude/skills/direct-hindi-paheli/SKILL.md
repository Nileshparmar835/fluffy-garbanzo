---
name: direct-hindi-paheli
description: Write, storyboard and render original Hindi or Hinglish animated paheli Shorts for Stickbits. Use when the viewer should solve a visual riddle, choose a suspect, predict a move, or see a previous episode’s answer proved on screen. Includes a Kokoro Hindi production workflow.
---

# Direct a Hindi paheli

Read the requested deliverable first. For a script, give the finished spoken Hindi, on-screen Roman Hindi, a shot plan and the answer proof. For a video, continue through an actual MP4 export. Read references/director-notes.md for the two reference patterns, scale options, and editorial checks.

## Work backwards from the answer

1. Write the solution in one sentence and list the minimum facts a viewer needs to reach it. For a logic puzzle, test every offered option, including awkward edge cases. If two answers work, change the premise.
2. Write three first lines built around different invitations: spot a contradiction, prevent a loss, or choose the first move. Pick the one a viewer can answer through the picture. Draw what frame zero will show alongside the line.
3. Anchor the puzzle in an ordinary place the audience recognizes. Give the storyteller a reason to care. Introduce one unusual rule. Show what it does to an object. Keep alternatives equally legible until the vote closes.
4. Give viewers a short quiet interval to decide. Reveal the answer with a visible change of state. End on a consequence, callback or honest new question. For connected episodes, resolve the old question before presenting the new one. Default to a complete answer within a standalone Short.
5. Use an editorial score as a revision tool. Never invent swipe rates, audience curves or a predicted viral score. After publishing, use the actual drop-off time to decide which beat to change.

## Direct the performance and picture

Use Kokoro v1.0 INT8, Hindi language `hi`, female voice `hf_beta` unless the user changes it. Give the hook playful urgency, the rule a matter-of-fact delivery, and the reveal room to land. Separate clean Devanagari speech from English directions. Spell out numbers for speech. Keep Roman Hindi headlines short enough to read in a glance. Make one pose or prop move for each change of evidence. Keep colors and positions stable across reverse shots. Use an accent for the decisive word and a lower area for choices. Use original characters, artwork, branding and sound.

## Match the reference animation

Before rendering, compare three actual frames from the reference with the corresponding rough shots for the hook, clue and reveal. Check where the actors stand, how much of the room is visible, how the viewer sees the object move, and where captions sit. Use a portrait, edge-to-edge set, a bold outlined sans face, compact Roman Hindi headlines and a restrained choice overlay.

Block an observable action for every clue. Write who reaches, what is in their hand, where it lands, and who notices the change. Keep fingers attached to held props from pickup to release. In the weighing example, the beam first dips under the shopkeeper’s load and levels when the apprentice adds his load. Have the apprentice look toward the remaining sweets. Reframe only to emphasize a decision or reaction. Watch a muted motion test and check that the cause and effect is still understandable.

## Build the video when requested

Find the writable project with `src/story.json` and `build.sh`. The uploadable skill includes a starter in `resources/project/`; copy that starter into a writable project directory before editing. The standalone full project already has the starter at its root. Open its README. Run `bash setup.sh full` and read the actual result. A fresh Linux sandbox may need package access. If a dependency is missing, name it precisely and preserve any verified output.

Draft the new episode in a copy. The sample renderer draws a nine-laddoo puzzle. A new mystery requires new objects, labels, movements, answer logic and corresponding scene functions in `src/render.py`. Replace SVG art or add assets when needed. Keep voice, style and technical configuration reusable. Generate narration first and use the measured scene boundaries; reuse recorded narration only for the supplied example. Run the motion test, inspect frames around important actions, render the film and decode the final MP4. Save the new MP4, SRT, proof, source and production notes. Give the user the files.

## Voice direction for Stickbits

Use Voice A for Hindi Shorts. Use the unblended Kokoro hf_beta voice, language hi and a fixed speed of 1.01×. Write and synthesize each complete scene as one conversational take. Use a 65 Hz high-pass filter and constant gain for each take. Give the viewer time to guess at the end of a scene. The approved audition is in assets/voice_A.wav. For new episodes, synthesize the new dialogue with src/voice_preset.json.

## Synchronize the whole short to Voice A

Use the companion write-visual-paheli skill for script development. The uploadable director also includes references/script-scale.md. Map named people, objects, choices and important verbs before drawing. Generate or retain the approved voice, then run the word alignment on the saved audio. In this project src/align_words.py reads Kokoro’s token durations and registers them against the recorded take. output/word_marks.json holds relative word times per scene; src/visual_cues.json names each anchor and its occurrence. Place motion, captions and optional Foley on that clock throughout the episode. A box arrives on डिब्बा and opens on खोला. Render actual entrances, not only changes of label. Keep the camera on the result long enough to understand it. When developing a different story, replace the action map and draw the appropriate objects. Inspect the frame before each key word, the first visible movement and the settled state.
