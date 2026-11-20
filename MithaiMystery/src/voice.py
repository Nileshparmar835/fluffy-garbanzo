"""Direct short Hindi takes, add their measured pauses and export the episode."""
import json
import subprocess
from pathlib import Path
import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
preset = json.loads((ROOT/'src/voice_preset.json').read_text())
options = ort.SessionOptions()
options.intra_op_num_threads = 3
options.inter_op_num_threads = 1
session = ort.InferenceSession(str(ROOT/'models/kokoro-v1.0.int8.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
engine = Kokoro.from_session(session, str(ROOT/'models/hindi-voices.bin'))
rate = 24000
parts, timeline = [], []
cursor = 0
for cue, hindi, roman, title, accent, _, pause, intent, action in json.loads((ROOT/'src/story.json').read_text()):
    if hindi == preset['audition_text']:
        # Keep the exact approved take in this episode's opening shot.
        take, sr = sf.read(ROOT / preset['reference_file'], dtype='int16')
    else:
        y, sr = engine.create(hindi, voice=preset['voice'], lang=preset['language'], speed=preset['speed'])
        active = np.flatnonzero(abs(y) > .004)
        assert len(active) and sr == rate and np.isfinite(y).all(), cue
        y = y[max(0,active[0]-480):active[-1]+840].copy()
        y[:80] *= np.linspace(0,1,80)
        y[-96:] *= np.linspace(1,0,96)
        args=['ffmpeg','-hide_banner','-nostats','-f','f32le','-ar',str(sr),'-ac','1','-i','pipe:0']
        measure=subprocess.run(args+['-af',preset['filter']+',loudnorm=I=-17:TP=-2:LRA=9:print_format=json','-f','null','-'],input=y.astype('<f4').tobytes(),capture_output=True,check=True)
        log=measure.stderr.decode()
        meters=json.loads(log[log.rindex('{'):log.rindex('}')+1])
        gain=min(-17-float(meters['input_i']),-2-float(meters['input_tp']))
        filtered=subprocess.run(args+['-af',preset['filter']+f',volume={gain:.3f}dB','-f','s16le','pipe:1'],input=y.astype('<f4').tobytes(),capture_output=True,check=True)
        take=np.frombuffer(filtered.stdout,dtype='<i2')
    assert sr == rate
    start=cursor
    speech_end=start+len(take)
    hold=round(rate*pause)
    parts.extend([take,np.zeros(hold,dtype=np.int16)])
    cursor=speech_end+hold
    timeline.append(dict(cue=cue,start=start/rate,speech_end=speech_end/rate,end=cursor/rate,hindi=hindi,roman=roman,title=title,accent=accent,intent=intent,action=action,voice=preset['voice'],speed=preset['speed']))
    print(cue,round(cursor/rate,2),flush=True)
sf.write(OUT/'narration.wav',np.concatenate(parts),rate,subtype='PCM_16')
(OUT/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
def stamp(t):
    ms=round(t*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for language in ['hindi','roman']:
    (OUT/(language+'.srt')).write_text('\n\n'.join(f"{i}\n{stamp(s['start'])} --> {stamp(s['speech_end'])}\n{s[language]}" for i,s in enumerate(timeline,1))+'\n')
