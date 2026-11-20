"""Decode finished media and check the relationship between narration, cues and picture."""
import json
import subprocess
import wave
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'output'
film=out/'Nau_Laddoo.mp4'
streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(film)]))['streams']
v=next(s for s in streams if s['codec_type']=='video')
a=next(s for s in streams if s['codec_type']=='audio')
assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],v['r_frame_rate'])==('h264',720,1280,'yuv420p','30/1')
assert a['codec_name']=='aac'
tl=json.loads((out/'timeline.json').read_text())
with wave.open(str(out/'narration.wav'),'rb') as f:
    sec=f.getnframes()/f.getframerate()
assert abs(tl[-1]['end']-sec)<.001 and tl[0]['start']==0
for i,row in enumerate(tl):
    assert row['start']<row['speech_end']<=row['end']
    if i: assert abs(row['start']-tl[i-1]['end'])<.001
assert abs(float(v['duration'])-sec)<.05 and abs(float(a['duration'])-sec)<.13
for language in ['hindi','roman']:
    assert (out/(language+'.srt')).read_text().count('-->')==len(tl)
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(film),'-f','null','-'],check=True)
print(f"Passed full decode, {v['nb_frames']} frames, {sec:.3f} s narration, {len(tl)} measured subtitle cues.")
