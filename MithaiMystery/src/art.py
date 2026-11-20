"""Draw original mithai-shop scenery and puppets, and rasterize editable SVG masters."""
from pathlib import Path
import math
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor

A = Path(__file__).resolve().parents[1] / 'assets'
INK = '#382c2c'
jobs = []
def svg(name,w,h,body):
    path=A/'vector'/f'{name}.svg'
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'+body+'</svg>')
    jobs.append((path,A/'sprites'/f'{name}.png'))
def path(d,fill,stroke=INK,sw=3):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
def rect(x,y,w,h,fill,r=0,stroke='none',sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def ell(x,y,rx,ry,fill,stroke='none',sw=2):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def group(data, transform):
    return f'<g transform="{transform}">{data}</g>'
def star(cx,cy,r,c):
    return group(path('M0 -12 Q1 -2 10 0 Q2 1 0 12 Q-2 1 -10 0 Q-2 -1 0 -12Z',c,'none'),f'translate({cx} {cy}) scale({r/12})')
def arch(x,y,s):
    inner=path('M0 280 V95 Q0 65 28 65 Q28 44 51 42 Q57 21 92 9 Q102 5 110 0 Q117 6 128 9 Q161 23 168 42 Q190 43 194 65 Q220 66 220 95 V280Z','#e3ab71','#be784c',5)
    inner+=path('M10 280 V99 Q10 75 36 74 Q35 49 61 51 Q66 30 110 14 Q151 30 160 51 Q183 49 185 75 Q210 75 210 100 V280Z','#b9624d','#f9cc85',6)
    inner+=path('M24 279 V110 Q20 80 51 84 Q48 59 70 63 Q78 43 110 29 Q141 45 150 63 Q171 60 172 84 Q201 83 196 111 V279Z','#774641','none')
    return group(inner,f'translate({x} {y}) scale({s})')
def jar(x,y,s,col):
    obj=rect(-15,0,30,7,'#f5cf82',2,'#664433')+path('M-11 8 L-11 14 Q-22 20 -20 28 L-19 64 Q-19 72 -12 72 H13 Q20 72 20 65 L21 28 Q22 20 12 14 V8Z','#d4946b','#543a36',3)
    obj+=rect(-16,35,32,30,col,6)+rect(-16,36,32,13,'#ffe3a1',1)+path('M-13 20 Q-16 24 -15 32','none','#ffe5bd',3)
    return group(obj,f'translate({x} {y}) scale({s})')
def scene():
    v=rect(0,0,720,1280,'#e7b983')
    for i in range(-1,9):
        for j in range(3,15):
            x=i*98+48*(j%2); y=j*49
            v+=path(f'M{x} {y} q8 -5 17 0 q-8 5 -17 0Z','#d7a771','none')
    for x in [-101,237,575]: v+=arch(x,322,1.12)
    for side in [-8,565]:
        for j in range(2):
            y=515+96*j
            for i,c in enumerate(['#aa6852','#b18d54','#9fba91']):
                v+=jar(side+21+54*i,y-58,.77,c)
            v+=rect(side-15,y,192,11,'#6d4641',2,'#593e38')+rect(side-15,y,192,4,'#d3a464',2)
    for i in range(-1,14):
        x=i*62
        v+=path(f'M{x} 282 h62 v30 q-31 36 -62 0Z',['#bc5543','#f6d297'][i%2],'#96553c',2)
    v+=rect(0,277,720,8,'#70423c')+rect(0,272,720,6,'#e2a858')
    v+=rect(0,713,720,485,'#f2d5aa')+rect(0,704,720,14,'#563c30')+rect(0,712,720,8,'#ffe5b3')
    for x in range(-1100,1900,180):
        v+=path(f'M{(x-360)*.39+360} 722 L{x} 1200','none','#e4bf95',2)
    for y in [757,815,909,1040,1175]: v+=rect(0,y,720,2,'#dfbb90')
    v+=rect(0,1183,720,97,'#12665f')+rect(0,1180,720,8,'#493c32')+rect(0,1191,720,5,'#edbd69')+rect(0,1202,720,3,'#399084')
    for x in range(-10,730,45):
        v+=path(f'M{x} 1223 l22 15 -22 15 -22 -15Z','#21867a','none')+ell(x,1238,4,4,'#bfa268')
    # Chalkboard with a double pinstripe and hand-painted corner florets.
    v+=rect(0,0,720,273,'#124d49')+rect(16,14,688,246,'none',19,'#589082',2)+rect(23,21,674,232,'none',14,'#b8a770',1)
    for x in (40,680):
        for y in (40,235): v+=star(x,y,8,'#d8b26e')
    return v
svg('shop',720,1280,scene())

# Chanda, the halwai. The head is separate so gaze and chin can lead the gesture.
body=path('M53 385 Q49 315 62 282 Q75 245 119 242 L200 237 Q244 236 270 266 Q288 293 291 382Z','#e8ae3f',INK,5)
body+=path('M64 281 Q72 257 97 250 L131 380 H51 Q47 330 64 281Z','#c55a46',INK,4)
body+=path('M215 245 L246 253 Q230 285 212 316 Q199 337 176 385 H95 Q140 334 166 299Z','#157d70',INK,4)
body+=path('M230 246 Q211 292 154 380 M243 248 Q223 295 170 381','none','#f2c875',4)
for i in range(8):
    body+=star(160+i*7.7,345-i*12,4,'#e1b76a')
body+=path('M123 229 Q145 252 171 255 Q191 255 211 236 L205 216 L134 211Z','#b76f4d',INK,4)
body+=path('M120 244 Q143 276 177 264 Q191 260 204 248','none','#f8d16c',5)
body+=ell(167,269,6,8,'#d44732','#6c442e',2)
body+=path('M55 340 Q78 331 102 353 L115 375 H53Z','#de835e',INK,4)
svg('body',320,390,body)
def head(blink,talk):
    v=ell(224,100,50,47,'#473137',INK,5)+path('M204 71 Q225 44 255 68 Q273 89 258 104 Q263 81 242 74 Q221 70 213 89Z','#72464b','none')
    for x,y in [(240,62),(250,65),(258,71),(263,81),(265,91)]:
        v+=ell(x,y,8,7,'#f0b445','#7e503b',2)+ell(x-1,y-2,3,2,'#ffe0a3')
    v+=path('M80 117 Q72 83 102 54 Q125 29 161 34 Q220 29 240 77 Q255 111 239 160 L221 184 L90 171Z','#382e35',INK,5)
    v+=path('M92 111 Q107 92 130 79 Q151 96 189 91 Q214 94 221 113 L229 141 Q236 123 246 133 Q261 148 244 166 L228 172 Q221 206 183 222 Q161 232 132 220 Q99 212 91 181 Q79 182 73 169 Q64 150 76 145 Q83 143 89 151Z','#e69b70',INK,4)
    v+=path('M91 109 Q111 95 130 76 Q147 85 167 87 Q186 87 205 98 Q187 88 174 79 Q145 75 133 60 Q107 65 89 93Z','#463139','none')
    v+=path('M93 82 Q107 54 131 50 M145 52 Q162 68 186 70 M200 61 Q218 72 225 89','none','#79514e',3)
    for x,y in [(113,155),(201,153)]: v+=ell(x,y,13,7,'#d98566')
    v+=path('M146 139 Q139 153 143 158 Q149 164 156 158','none','#8f5246',3)
    for x,y in [(118,131),(182,127)]:
        if blink: v+=path(f'M{x-14} {y+4} q14 6 28 -1','none',INK,4)
        else:
            v+=ell(x,y,15,13,'#fff0cb',INK,3)+ell(x+3,y+2,7,9,'#3b3033')+ell(x+5,y-2,2.5,3,'#fff1cd')
    v+=path('M100 113 Q112 104 131 109 M166 106 Q182 97 197 104','none','#503434',6)
    v+=ell(149,108,5,7,'#b84336')
    v+=path('M128 177 Q156 189 182 168 Q178 190 156 194 Q139 195 128 177Z' if talk else 'M130 176 Q154 191 179 171 Q161 198 136 184Z','#77413d',INK,3)
    v+=path('M136 178 Q158 184 177 172 Q163 187 141 183Z','#ffe9c6','none')
    for x,y in [(84,173),(235,168)]:
        v+=ell(x,y,4,4,'#f8d681',INK,2)+path(f'M{x} {y+4} l-8 14 q8 6 16 -1Z','#edb548',INK,2)+ell(x,y+20,3,3,'#e2a74b',INK,1)
    return v
for b in [0,1]:
    for t in [0,1]: svg(f'head{b}{t}',320,390,head(b,t))
# Raised hand, open palm and bangles. The wrist pivots at (247,318).
arm=path('M233 318 Q235 297 253 298 Q278 296 289 274 L297 249 Q288 239 287 225 Q286 217 291 217 Q295 218 299 232 L302 211 Q302 203 307 205 Q310 207 307 225 L314 210 Q318 205 321 208 Q323 211 317 227 L325 218 Q330 214 332 218 Q332 222 320 239 L313 250 Q314 258 309 271 Q298 314 273 329 Q245 348 233 318Z','#e9a47b',INK,4)
arm+=path('M295 251 l17 7 M293 256 l16 7','none','#ebbc5e',4)+path('M297 239 Q305 232 313 234','none','#aa664f',2)
svg('arm',350,390,arm)

# One identical sweet sprite. Only its paper-cup number changes on screen.
v=ell(61,102,47,8,'#b38150')
v+=path('M13 73 Q3 40 26 19 Q44 0 66 7 Q90 5 102 26 Q117 40 109 72 L96 89 H26Z','#dd842b',INK,4)
v+=path('M16 55 Q13 28 36 17 Q58 5 80 17 Q98 28 100 46 Q93 68 68 72 Q36 81 16 55Z','#f2a941','none')
rng=random.Random(12)
for i in range(58):
    x,y=rng.uniform(21,101),rng.uniform(17,74)
    if ((x-60)/43)**2+((y-46)/33)**2<1:
        v+=ell(round(x,1),round(y,1),rng.choice([1,2,3]),rng.choice([1,2,3]),rng.choice(['#ffc86b','#e79831','#d9872e','#f7b44a']))
for x,y,a in [(49,24,-25),(71,20,8),(80,29,-18)]:
    v+=group(path('M-6 0 Q-2 -5 7 -2 Q3 3 -6 0Z','#819447','#58633b',1),f'translate({x} {y}) rotate({a})')
v+=path('M8 72 Q59 89 113 72 L101 96 Q58 109 22 96Z','#faf0d0',INK,3)
for x in [21,33,45,58,71,84,97]: v+=path(f'M{x} 79 l3 15','none','#dab789',2)
svg('sweet',120,112,v)
# Cut face showing an ivory khoya core.
v=path('M14 75 Q3 53 18 29 Q34 7 63 12 Q91 13 105 38 Q121 71 96 87 Q71 105 36 93Z','#f4ad44',INK,4)
v+=path('M29 71 Q20 54 30 38 Q43 22 62 26 Q85 26 94 44 Q103 64 87 77 Q59 93 37 80Z','#ffdf9a','#c97a32',3)
v+=path('M40 66 Q32 52 46 41 Q64 29 79 44 Q92 60 78 70 Q56 82 40 66Z','#fff0c8','none')
for x,y in [(42,45),(66,40),(49,69),(82,59),(56,52)]:v+=ell(x,y,2,1.5,'#ddbc80')
svg('cut',120,112,v)
# Full-height street-side shop set. The actors play in front of the shelves.
v='''<defs>
<linearGradient id="wall" x2=".3" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#ffdc96"/><stop offset=".63" stop-color="#ffe3a7"/><stop offset="1" stop-color="#edaf75"/></linearGradient>
<linearGradient id="wood" x2="0" y2="1"><stop stop-color="#b3673f"/><stop offset="1" stop-color="#81452f"/></linearGradient>
<linearGradient id="glass" x2=".2" y2="1"><stop stop-color="#86b6ba"/><stop offset="1" stop-color="#bdd5c0"/></linearGradient>
</defs>'''+rect(0,0,720,1280,'url(#wall)')
# Overhead molding and painted wall. Enough clear space for short floating captions.
v+=rect(0,0,720,18,'#754433')+rect(0,18,720,12,'#cf9155')+rect(0,30,720,4,'#e4ab68')
for x,y in [(22,254),(107,289),(611,260),(570,220),(669,300),(37,370),(315,270)]:
    v+=path(f'M{x} {y} q7 -5 12 -1 m5 1 9 -2','none','#e7b77c',2)
# Lit street through an arched doorway.
v+=path('M263 697 V426 Q263 349 361 327 Q459 348 459 426 V697Z','#b57556','#824b3c',4)
v+=path('M277 696 V429 Q277 370 361 343 Q444 368 444 429 V696Z','#96cfc9','#f7c992',5)
v+=ell(401,441,24,24,'#ffe39a')+path('M279 582 Q300 561 326 573 L351 548 Q375 541 401 569 Q431 548 444 558 V689 H279Z','#689d87','none')
for x,wd,h,c in [(284,26,52,'#dc9b6c'),(310,42,61,'#e8b980'),(357,25,43,'#e3b989'),(388,40,55,'#dba375')]:
    v+=rect(x,646-h,wd,h,c,1,'#9a7860',1)+rect(x-2,643-h,wd+4,4,'#b37c59')
v+=rect(276,647,168,40,'#ceb58c')
# Both wall shelves contain boxed sweets, jars and paper packets.
rng=random.Random(42)
for left in (-12,499):
    for j,yy in enumerate((420,545,666)):
        v+=rect(left+2,yy+1,236,13,'#c98e64',3)+rect(left,yy-6,235,10,'#a76c47',2,'#684735',2)
        for k in range(4):
            xx=left+19+53*k
            if (j+k)%3==0:
                v+=jar(xx+12,yy-63,.77,['#af8e5c','#c88356','#7ead86'][k%3])
            else:
                h=rng.randint(34,51);c=['#e7b45a','#dfa083','#80b9a0','#e1b883'][(k+j)%4]
                v+=rect(xx,yy-h-7,38,h,c,2,'#865c45',2)+rect(xx-2,yy-h-10,42,8,'#f3d6a1',2,'#926649',1)
                v+=rect(xx+2,yy-h+4,34,13,'#fbe2b3')+ell(xx+19,yy-h+10,5,4,'#b66a56')
# Hand painted timber plaque hangs from little hooks.
v+=path('M244 322 v27 M477 322 v27','none','#89583e',3)
v+=rect(208,340,304,64,'#8e533b',11,INK,3)+rect(212,335,296,60,'#ab3f35',9,INK,3)+rect(219,342,282,46,'none',5,'#edba79',2)
# Marble top, wood trim, glass mithai display and tiled floor.
v+=rect(0,742,720,266,'#f0c493')+rect(0,738,720,7,'#634b3e')
for x in range(-200,850,145):
    v+=path(f'M{x} 765 q42 10 51 30 t65 25 m-6 -4 q22 8 43 7','none','#e3b681',2)
v+=rect(0,998,720,167,'url(#wood)',0,INK,4)+rect(0,992,720,11,'#e5a362',1,INK,3)
v+=rect(15,1014,690,130,'url(#glass)',7,'#5f443b',5)
for i in range(21):
    xx=25+i*34
    for j in range(2+(i//5)%2):
        yy=1120-j*17
        if (i//6)%2==0:
            v+=ell(xx+j*2,yy,13,11,['#df9846','#eaae5b'][j%2],'#9d724b',1.5)
        else:
            v+=rect(xx-11+j*2,yy-9,22,17,'#f2d9a1',2,'#b3986e',1)
for x in (53,289,486):
    v+=path(f'M{x} 1019 l-45 116 h19 l47 -116Z','#d1dfc5','none')
for x in (208,487):v+=rect(x,1017,6,124,'#876146')
v+=rect(0,1145,720,15,'#a86a42',0,'#684432',2)
for row in range(3):
    for i in range(-1,10):
        v+=rect(i*93+(row%2)*46,1162+row*42,93,43,['#e4bb84','#f2cc98'][(i+row)%2])
svg('open-shop',720,1280,v)
# Original apprentice, including separate eyes and mouth animated by the renderer.
v=path('M26 211 Q30 181 58 171 L124 169 Q158 173 178 211 L189 297 H14Z','#df7348',INK,4)
v+=path('M29 220 Q45 202 65 195 L73 174 L89 197 L104 175 L133 178 L140 296 H39Z','#f0aa57',INK,4)
v+=path('M66 172 Q89 195 108 170 L110 151 L66 153Z','#c98158',INK,4)
v+=path('M65 175 l21 23 -13 12 -16 -28 M110 175 l-21 23 12 13 19 -31','#fff0ca',INK,3)
v+=path('M85 202 v74','none','#bd7d41',3)+ell(94,232,3,3,'#74523a')
svg('helper-body',200,300,v)
v=path('M22 80 Q14 47 47 28 Q74 6 126 25 Q160 35 170 83 L161 128 L47 141Z','#453339',INK,4)
v+=path('M27 77 Q34 47 80 46 Q126 38 155 65 Q170 80 161 99 Q177 91 178 108 Q179 124 162 130 Q155 157 129 172 Q101 187 70 176 Q44 169 31 147 Q20 146 15 136 Q9 121 24 121Z','#e7a374',INK,4)
v+=path('M28 95 Q17 70 32 50 Q53 17 95 25 Q139 27 157 62 Q139 55 123 59 Q113 64 98 64 Q108 59 111 52 Q92 66 70 64 Q57 65 51 71 Q54 63 61 57 Q44 64 37 81 L31 100Z','#493035',INK,4)
v+=path('M26 66 Q22 37 48 16 Q82 -3 116 13 Q144 18 153 39 L158 52 Q99 32 34 72Z','#3b9484',INK,4)
v+=path('M40 51 Q60 22 90 22 M50 48 Q79 30 100 30','none','#84c0a2',3)
v+=path('M29 61 Q73 26 125 34 Q149 37 164 49 Q177 59 157 61 Q111 43 42 75 L24 82Z','#226458',INK,4)
v+=path('M115 118 q12 5 10 12 q-1 6 -12 6','none','#a8634c',3)
for xx,yy in [(51,129),(56,134),(45,136),(145,131),(149,126)]:v+=ell(xx,yy,2,2,'#ba7958')
svg('helper-head',194,187,v)

def export(job):
    source,out=job
    subprocess.run(['inkscape',str(source),'--export-filename='+str(out)],check=True,capture_output=True)
with ThreadPoolExecutor(3) as pool:
    list(pool.map(export,jobs))
