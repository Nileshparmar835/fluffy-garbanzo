"""Install the pinned ONNX file for the lightweight Claude skill. Verify both assets."""
import hashlib
from pathlib import Path
import shutil
import tempfile
import urllib.request

models=Path(__file__).resolve().parents[1]/'models'
weights=models/'kokoro-v1.0.int8.onnx'
digest='6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb'
def check(path,expected):
    with path.open('rb') as f:
        sha=hashlib.sha256()
        for buf in iter(lambda:f.read(1<<20),b''): sha.update(buf)
    if sha.hexdigest()!=expected: raise ValueError(f'Incorrect model checksum for {path.name}')
check(models/'hindi-voices.bin','f9f26fb177dc97e19ec269a1f764ad9277b86372ce671a187663295dd84e900a')
if not weights.exists():
    base='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
    with tempfile.NamedTemporaryFile(dir=models,delete=False) as tmp:
        temp=Path(tmp.name)
    try:
        with urllib.request.urlopen(base+weights.name,timeout=120) as src,temp.open('wb') as dst:
            shutil.copyfileobj(src,dst)
        check(temp,digest)
        temp.replace(weights)
    finally:
        temp.unlink(missing_ok=True)
else:check(weights,digest)
