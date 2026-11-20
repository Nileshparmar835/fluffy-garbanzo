"""Test real Hindi synthesis; an import alone does not verify phonemization."""
from pathlib import Path
import numpy as np
import onnxruntime as ort
from kokoro_onnx import Kokoro
p=Path(__file__).resolve().parents[1]/'models'
opt=ort.SessionOptions()
opt.intra_op_num_threads=2
opt.inter_op_num_threads=1
session=ort.InferenceSession(str(p/'kokoro-v1.0.int8.onnx'),opt,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(session,str(p/'hindi-voices.bin'))
y,sr=k.create('नौ लड्डू।',voice='hf_beta',lang='hi',speed=1)
assert sr==24000 and len(y)>4000 and np.isfinite(y).all() and max(abs(y))>.03
print('Kokoro hf_beta Hindi CPU synthesis passed.')
