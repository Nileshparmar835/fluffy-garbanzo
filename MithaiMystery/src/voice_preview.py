"""Export a short voice-only audition using complete takes from the episode."""
import json
import subprocess
import tempfile
import wave
from pathlib import Path

out = Path(__file__).resolve().parents[1]/'output'
rows = {r['cue']:r for r in json.loads((out/'timeline.json').read_text())}
with wave.open(str(out/'narration.wav'),'rb') as source:
    sr = source.getframerate()
    params = source.getparams()
    pieces = []
    for cue in ('hook','guess','reveal'):
        r = rows[cue]
        first = round(r['start']*sr)
        source.setpos(first)
        pieces.append(source.readframes(round(r['end']*sr)-first))
with tempfile.TemporaryDirectory() as tmp:
    wav = Path(tmp)/'audition.wav'
    with wave.open(str(wav),'wb') as dest:
        dest.setparams(params)
        dest.writeframes(b''.join(pieces))
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(wav),'-af','loudnorm=I=-15:TP=-1.5:LRA=8','-ar','48000','-c:a','libmp3lame','-b:a','160k',str(out/'Stickbits_Voice_A.mp3')],check=True)
