"""Read Kokoro's internal token durations and anchor them to the saved Voice A takes."""
import json
from pathlib import Path
import tempfile
import wave

import numpy as np
import onnxruntime as ort
from kokoro_onnx import Kokoro
from kokoro_onnx.trim import trim as trim_audio
from kokoro_onnx.sliding import token_edges

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'

def varint(n):
    out=bytearray()
    while n>=128:
        out.append((n & 127)|128)
        n >>= 7
    out.append(n)
    return bytes(out)

def fields(data):
    def integer(i):
        v=0
        shift=0
        while True:
            byte=data[i];i+=1
            v|=(byte&127)<<shift
            if byte<128:return v,i
            shift+=7
    i=0
    while i<len(data):
        start=i
        tag,i=integer(i)
        wire=tag & 7
        if wire==2:
            size,i=integer(i); end=i+size
        elif wire==0:
            _,end=integer(i)
        else:
            end=i+{1:8,5:4}[wire]
        yield tag>>3,data[i:end],data[start:end]
        i=end

def message(key,data):
    return varint(key*8+2)+varint(len(data))+data

def timing_model(model_path,dest):
    # The pinned INT8 model already calculates rounded/clamped per-token lengths.
    # Promote its existing ValueInfo from graph.value_info(13) to graph.output(12)
    # in a temporary copy. The recorded voice model itself is preserved.
    data=model_path.read_bytes()
    with dest.open('wb') as result:
        for key,body,raw in fields(data):
            if key!=7:
                result.write(raw)
                continue
            info=next(value for k,value,_ in fields(body) if k==13 and
                      any(i==1 and name==b'/encoder/Clip_output_0' for i,name,_ in fields(value)))
            result.write(message(7,body+message(12,info)))

def export():
    preset=json.loads((ROOT/'src/voice_preset.json').read_text())
    timeline=json.loads((OUT/'timeline.json').read_text())
    with wave.open(str(OUT/'narration.wav')) as source:
        sr=source.getframerate()
        stem=np.frombuffer(source.readframes(source.getnframes()),dtype='<i2')
    assert sr==24000
    report={}
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'word-timing.onnx'
        timing_model(ROOT/'models/kokoro-v1.0.int8.onnx',path)
        opts=ort.SessionOptions();opts.intra_op_num_threads=3;opts.inter_op_num_threads=1
        session=ort.InferenceSession(str(path),sess_options=opts,providers=['CPUExecutionProvider'])
        engine=Kokoro.from_session(session,str(ROOT/'models/hindi-voices.bin'))
        for scene in timeline:
            voice,ph,batches=engine._prepare(scene['hindi'],preset['voice'],preset['speed'],preset['language'],False,.25,.10)
            phones=[];edges=[];parts=[];offset=0
            for batch,pause in batches:
                tokens=engine.tokenizer.tokenize(batch)
                samples,durations=session.run(None,{engine._tokens_input:np.array([[0,*tokens,0]],dtype=engine._input_dtypes[engine._tokens_input]),'speed':np.array([preset['speed']],dtype=engine._input_dtypes['speed']),'style':engine._style_for(voice,len(tokens))})
                audio=np.asarray(samples).ravel()
                times=token_edges(np.ravel(durations),len(audio))[1:]
                trimmed,(head,_)=trim_audio(audio)
                times=np.clip(times-head,0,len(trimmed))
                phonemes=engine.tokenizer.known(batch)
                phones.extend(phonemes)
                edges.extend((offset+int(times[i]),offset+int(times[i+1])) for i in range(len(phonemes)))
                silence=np.zeros(int(sr*pause))
                parts.extend([trimmed,silence]);offset+=len(trimmed)+len(silence)
            audio=np.concatenate(parts)
            active=np.flatnonzero(np.abs(audio)>.004)
            lo=max(0,active[0]-480);hi=min(len(audio),active[-1]+840)
            actual=stem[round(sr*scene['start']):round(sr*scene['speech_end'])]
            # Random excitation in Kokoro may vary between syntheses. Register
            # timing estimates to the recorded speech envelope at 5 ms resolution.
            def envelope(y):
                n=len(y)//120
                return np.sqrt(np.mean(y[:n*120].astype(float).reshape(n,120)**2,axis=1))
            synth=envelope(audio[lo:hi]); recorded=envelope(actual)
            drift=len(recorded)-len(synth)
            assert abs(drift)<25,(scene['cue'],drift)
            best=(-1,0)
            for lag in range(-20,21):
                x=synth[max(0,-lag):];y=recorded[max(0,lag):];n=min(len(x),len(y))
                corr=float(np.corrcoef(x[:n],y[:n])[0,1])
                if corr>best[0]:best=(corr,lag)
            assert best[0]>.80,(scene['cue'],best)
            runs=[];run=[]
            for i,ch in enumerate(phones):
                if ch.isspace():
                    if run:runs.append(run);run=[]
                else:run.append(i)
            if run:runs.append(run)
            words=scene['hindi'].split()
            assert len(words)==len(runs),(scene['cue'],words,[''.join(phones[i] for i in ix) for ix in runs])
            def seconds(n):
                return round(np.clip((n-lo)/sr+best[1]*.005,0,len(actual)/sr),4)
            report[scene['cue']]=[dict(word=w,start=seconds(edges[ix[0]][0]),end=seconds(edges[ix[-1]][1])) for w,ix in zip(words,runs)]
            print(scene['cue'],round(best[0],3),report[scene['cue']],flush=True)
    (OUT/'word_marks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':export()
