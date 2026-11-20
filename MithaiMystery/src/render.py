"""Frame-accurate layered 2D animation. All positions use the 720×1280 reference canvas."""
import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
A=ROOT/'assets'
W,H,FPS=720,1280,30
INK='#382d33'
GREEN='#144e48'
CREAM='#fff0cb'
GOLD='#ffd076'
RUST='#a53f37'
MINT='#bce7b3'
timeline=json.loads((OUT/'timeline.json').read_text())
assets={p.stem:Image.open(p).convert('RGBA') for p in (A/'sprites').glob('*.png')}
background=assets['shop'].convert('RGB')
# Fixed paper grain keeps the image tactile and does not shimmer between frames.
pixels=np.asarray(background,dtype=np.int16)
grain=np.random.default_rng(9).normal(0,1.8,(H,W,1)).astype(np.int16)
background=Image.fromarray(np.uint8(np.clip(pixels+grain,0,255)))
@lru_cache(maxsize=180)
def font(size,face='sans'):
    names={'serif':'DejaVuSerifCondensed-Bold','sans':'DejaVuSansCondensed-Bold','mono':'DejaVuSansMono-Bold'}
    return ImageFont.truetype(str(A/'fonts'/(names[face]+'.ttf')),size)
def word(draw,x,y,text,size,col=INK,face='sans',maxw=640):
    f=font(size,face)
    while draw.textlength(text,font=f)>maxw and size>10:
        size-=1
        f=font(size,face)
    draw.text((round(x),round(y)),text,font=f,fill=col,anchor='mm')
def rr(d,box,r,fill,edge=None,sw=2):
    d.rounded_rectangle(tuple(round(a) for a in box),r,fill,edge,sw)
def line(d,points,col,width):
    d.line([(round(x),round(y)) for x,y in points],col,width,joint='curve')
def ellipse(d,x,y,rx,ry,col,edge=None,w=2):
    d.ellipse((round(x-rx),round(y-ry),round(x+rx),round(y+ry)),col,edge,w)
def star(d,x,y,r,col):
    d.polygon([(x,y-r),(x+r*.25,y-r*.24),(x+r*.83,y),(x+r*.25,y+r*.21),(x,y+r),(x-r*.25,y+r*.21),(x-r*.83,y),(x-r*.25,y-r*.24)],col)
def smooth(z):
    z=max(0,min(1,z))
    return z*z*(3-2*z)
def mix(a,b,w):
    return a+(b-a)*w
@lru_cache(maxsize=160)
def scaled(key,w):
    a=assets[key]
    return a.resize((w,round(w*a.height/a.width)),Image.Resampling.LANCZOS)
def put(im,key,x,y,w,angle=0,pivot=None):
    s=scaled(key,int(w))
    if abs(angle)>.1:
        s=s.rotate(angle,Image.Resampling.BICUBIC,center=pivot,expand=False)
    im.paste(s,(round(x),round(y)),s)
def label(d,x,y,txt,color=GREEN,fg=CREAM):
    w=round(d.textlength(txt,font=font(18,'mono')))+34
    rr(d,(x-w/2,y-17,x+w/2,y+17),15,color)
    word(d,x,y,txt,18,fg,'mono')
def tray(d,cx,cy,rx,ry):
    ellipse(d,cx,cy+9,rx,ry,'#b0916b')
    ellipse(d,cx,cy,rx,ry,'#b37240',INK,4)
    ellipse(d,cx,cy-4,rx-3,ry-4,'#e6b765','#78543c',3)
    ellipse(d,cx,cy-5,rx-15,ry-13,'#f9dc8e','#a26e40',3)
    ellipse(d,cx,cy-5,rx-23,ry-20,'#deb274','#fff0b3',2)
def pos_mix(start,end,v,arc):
    return (mix(start[0],end[0],v),mix(start[1],end[1],v)-math.sin(v*math.pi)*arc)
def outlined(d,x,y,txt,size,color,maxw=635,stroke=5):
    f=font(size)
    while d.textlength(txt,font=f)>maxw and size>12:
        size-=1
        f=font(size)
    d.text((round(x+1),round(y+3)),txt,font=f,fill=INK,anchor='mm',stroke_width=stroke+1,stroke_fill='#6e472f')
    d.text((round(x),round(y)),txt,font=f,fill=color,anchor='mm',stroke_width=stroke,stroke_fill=INK)

def cards(d,values,u,starts):
    for i,(letter,value) in enumerate(zip('ABC',values)):
        elapsed=u-starts[i]
        if elapsed<0:continue
        x=49+i*213
        y=1020+22*(1-smooth(elapsed/.22))
        rr(d,(x+2,y+6,x+193,y+69),14,'#764c3b')
        rr(d,(x,y,x+192,y+63),14,'#fff6dc',INK,4)
        ellipse(d,x+32,y+32,21,21,['#b74d42','#2b739a','#328360'][i],INK,2)
        word(d,x+32,y+31,letter,24,'white')
        word(d,x+117,y+31,value,30,INK,'sans',104)

def shop():
    a=assets['open-shop'].convert('RGB')
    d=ImageDraw.Draw(a)
    word(d,360,365,'CHANDA  MITHAIWALI',23,'#fff0bc','sans',271)
    # Soft light falls down the wall and a light vignette frames the action.
    pix=np.asarray(a,dtype=np.int16)
    yy,xx=np.mgrid[:H,:W]
    shade=(6*((xx-345)/420)**2+2*((yy-600)/800)**2)[:,:,None]
    return Image.fromarray(np.clip(pix-shade+grain,0,255).astype('uint8'))
set_image=shop()

def helper_face(im,x,y,sc,t,cue,focus):
    head=assets['helper-head'].copy()
    d=ImageDraw.Draw(head)
    astonished=cue in ('balance','guess','reveal')
    blink=(t+1.83)%3.35<.13
    for xx,yy in [(75,98),(127,95)]:
        if blink:
            d.arc((xx-16,yy-8,xx+16,yy+7),5,175,INK,4)
        else:
            rad=18 if astonished else 15
            ellipse(d,xx,yy,rad,rad+2,'#fff7e3',INK,3)
            px=xx+max(-7,min(7,(focus[0]-x-85)/46))
            py=yy+max(-4,min(7,(focus[1]-y-95)/46))
            ellipse(d,px,py,7,9,INK)
            ellipse(d,px+2,py-3,2.7,2.7,'white')
        brow=yy-(30 if astonished else 23)
        line(d,[(xx-13,brow+3),(xx-4,brow),(xx+9,brow-1)],INK,5)
    if astonished:
        ellipse(d,92,149,9,11,'#713a3a',INK,3)
    elif cue in ['choose','rules','last']:
        d.arc((75,134,110,154),2,155,INK,4)
    else:
        d.pieslice((72,129,117,158),0,180,'#943f39',INK,3)
        d.rectangle((82,144,106,147),fill='#fff4ce')
    head=head.resize((round(194*sc),round(187*sc)),Image.Resampling.LANCZOS)
    tilt=2*math.sin(t*2.1)+(-5 if astonished else 1)
    head=head.rotate(tilt,Image.Resampling.BICUBIC)
    im.paste(head,(round(x),round(y)),head)

def arm(d,shoulder,hand,side,skin,sleeve):
    sx,sy=shoulder; hx,hy=hand
    # Bend outward; wrist and prop share a target during pickup and release.
    ex=.48*sx+.52*hx+side*37
    ey=.48*sy+.52*hy+19
    for w,col in [(29,INK),(22,skin)]:
        line(d,[(sx,sy),(ex,ey),(hx,hy)],col,w)
        ellipse(d,ex,ey,w/2,w/2,col)
    mid=((sx+ex)/2,(sy+ey)/2)
    for w,col in [(38,INK),(31,sleeve)]:
        line(d,[shoulder,mid],col,w);ellipse(d,*mid,w/2,w/2,col)
    ellipse(d,hx,hy,16,13,skin,INK,3)
    ellipse(d,hx-side*8,hy-7,7,7,skin)

def scale_actor(d,tilt):
    px,py=360,658
    ellipse(d,360,878,75,10,'#cb9c71')
    rr(d,(349,637,371,860),8,'#ce9350',INK,4)
    line(d,[(356,655),(356,855)],'#f7ca76',3)
    d.polygon([(358,807),(380,844),(410,856),(312,856),(343,844)],'#c08b4e',INK)
    rr(d,(300,851,420,870),7,'#377166',INK,3)
    for side in [-1,1]:
        x=360+side*167;y=658+side*tilt
        line(d,[(px,py),(x,y)],INK,12)
        line(d,[(px,py-1),(x,y-1)],'#e9b468',6)
        for o in [-85,85]:
            line(d,[(x,y+3),(x+o,y+141)],INK,3)
        d.pieslice((x-85,y+123,x+85,y+160),0,180,'#bf8642',INK,3)
        ellipse(d,x,y+141,85,8,'#edc576',INK,3)
        ellipse(d,x,y,6,6,'#e5b45f',INK,2)
    ellipse(d,px,py,14,14,'#e3b677',INK,4)
    ellipse(d,px,py,5,5,'#40695f')

def trayload(u,start):
    return smooth((u-start)/.66)

def panel_sweet(im,d,n,x,y,w):
    put(im,'sweet',x-w/2,y-w*.50,w)
    r=w*.155
    ellipse(d,x,y+w*.26,r,r,'#225d51','#fff3c8',2)
    word(d,x,y+w*.25,str(n),round(w*.215),'#fff6dc','sans')

# The exact same clock drives actor entrances, prop motion, titles and Foley.
direction=json.loads((ROOT/'src/visual_cues.json').read_text())
word_marks=json.loads((OUT/'word_marks.json').read_text())
def events_for(cue):
    words=word_marks[cue]
    events={}
    for beat in direction[cue]['actions']:
        found=[w for w in words if w['word'].strip('।,.!?')==beat['word']]
        events[beat['id']]=found[beat['occurrence']-1]['start']
    return events
events={s['cue']:events_for(s['cue']) for s in timeline}
with wave.open(str(OUT/'narration.wav')) as voice_file:
    mouth_sr=voice_file.getframerate()
    samples=np.frombuffer(voice_file.readframes(voice_file.getnframes()),dtype='<i2').astype(float)/32768
mouth_frame=round(mouth_sr/FPS)
mouth_energy=np.sqrt(np.mean(np.pad(samples,(0,(-len(samples))%mouth_frame)).reshape(-1,mouth_frame)**2,axis=1))

def pop(elapsed):
    if elapsed<0:return 0
    phase=min(1,(elapsed+.025)/.22)
    return 1+(2.3*(phase-1)+1.3)*(phase-1)**2

def badge_icon(im,kind,cx,cy,elapsed,width=126):
    scale=pop(elapsed)
    if scale<=0:return
    layer=icon_image(kind)
    size=max(2,round(width*scale))
    stamp=layer.resize((size,size),Image.Resampling.LANCZOS)
    im.paste(stamp,(round(cx-size/2),round(cy-size/2)),stamp)

@lru_cache(maxsize=16)
def icon_image(kind):
    im=Image.new('RGBA',(180,180));d=ImageDraw.Draw(im)
    ellipse(d,92,96,78,75,'#a97450')
    ellipse(d,90,89,78,76,'#fff2cc',INK,5)
    ellipse(d,90,89,69,67,None,'#e7b666',3)
    if kind=='filling':
        put(im,'cut',42,39,97)
        rr(d,(74,108,142,141),12,GREEN,INK,2);word(d,108,124,'×2',25,'white')
    elif kind=='mass':
        ellipse(d,90,63,15,19,None,INK,8)
        d.polygon([(64,67),(115,67),(130,122),(49,122)],fill='#376e65',outline=INK,width=4)
        word(d,90,98,'?',32,CREAM)
    elif kind in ('scale','unused'):
        line(d,[(90,44),(90,120),(75,125),(106,125)],INK,5)
        line(d,[(45,63),(134,63)],'#8b552e',6)
        for cx in (50,130):
            line(d,[(cx,63),(cx-17,95),(cx+17,95),(cx,63)],INK,3)
            d.pieslice((cx-18,86,cx+18,108),0,180,'#da9a42',INK,2)
        if kind=='unused':line(d,[(40,135),(140,43)],'#c24e3e',10)
    else:
        word(d,90,90,kind,74,GREEN,'sans',132)
    return im

def flare(d,x,y,u):
    if not 0<=u<.32:return
    a=u/.32
    for j in range(8):
        k=j*math.pi/4
        r=26+30*a
        line(d,[(x+r*math.cos(k),y+r*math.sin(k)),(x+(r+11*(1-a))*math.cos(k),y+(r+11*(1-a))*math.sin(k))],'#fff1a3',max(1,int(5*(1-a))))

def box(im,d,progress,opened):
    # Perspective front wall and a hinged lid, sharing the same back edge.
    dx=round(-525*(1-progress));y=754
    def poly(pts,c):d.polygon([(x+dx,yy) for x,yy in pts],fill=c,outline=INK,width=3)
    traypts=[(191,y),(528,y),(559,898),(160,898)]
    poly(traypts,'#ffe3a1')
    poly([(160,898),(559,898),(551,927),(170,927)],'#af5545')
    for n in range(9):
        row,col=divmod(n,3)
        panel_sweet(im,d,n+1,260+col*99+dx,772+row*46,57)
    front=round(898-237*opened)
    edge=round(24-16*opened)
    poly([(186,y),(532,y),(558,front),(161,front)],'#bc5548' if opened<.5 else '#efc88c')
    poly([(161,front),(558,front),(555,front+edge),(165,front+edge)],'#913f38')
    if opened<.42:
        my=(front+y)/2
        diamond=[(360+dx,my-20),(388+dx,my),(360+dx,my+20),(332+dx,my)]
        d.polygon(diamond,fill='#f8d681',outline=INK,width=2)
    if opened>.7:
        for x in (216,504):ellipse(d,x+dx,front+24,6,6,'#ffe5a6','#ab8052',2)

def outside_bracket(d,u):
    v=smooth(u/.22)
    if v<=0:return
    for x,sgn in [(199,1),(521,-1)]:
        line(d,[(x,933),(x,961),(x+sgn*100*v,961)],GREEN,5)
    if v>.75:word(d,360,969,'BAHAR',20,GREEN)

def scale_entry(im,d,elapsed):
    if elapsed<0:return
    phase=smooth((elapsed+.035)/.32)
    if phase==1:scale_actor(d,0);return
    obj=Image.new('RGBA',(720,1280));scale_actor(ImageDraw.Draw(obj),-7*(1-phase))
    obj=obj.crop((84,623,636,902))
    im.paste(obj,(84+round(535*(1-phase)),623-round(16*math.sin(phase*math.pi))),obj)

def cast(im,t,u,s,hand1,hand2,focus):
    cue=s['cue']
    # Head anticipation and delayed torso lift give each reaction a distinct silhouette.
    surprise=cue in ('balance','guess','reveal')
    bounce=math.sin(min(u/.44,1)*math.pi)*14 if surprise else 0
    lean=10*math.sin(min(u/1.25,1)*math.pi) if cue in ('move','last') else 0
    y=361+2*math.sin(t*2.15)-bounce*.6+lean
    entry=1 if cue!='rules' else smooth((u-events[cue]['chanda'])/.30)
    dx=-340*(1-entry);x=-29+lean+dx
    hand1=(hand1[0]+dx,hand1[1])
    put(im,'body',x,y,342)
    angle=(5 if surprise else -1)+2.1*math.sin(t*2.25)
    b=int(t%3.8<.12);m=int(mouth_energy[min(len(mouth_energy)-1,int(t*FPS))]>.053)
    put(im,f'head{b}{m}',x,y,342,angle,(177,224))
    helper_entry=0 if cue=='rules' else (smooth((u-events[cue]['aman'])/.30) if cue=='limit' else 1)
    shift=300*(1-helper_entry);bx=475-lean*.65+shift
    hand2=(hand2[0]+shift,hand2[1])
    by=443+1.6*math.sin(t*2.65)-bounce+lean
    put(im,'helper-body',bx-2,by,214)
    helper_face(im,bx+1,by-5,1.05,t,cue,focus)
    # Place the body behind the counter, then draw the forearms in front.
    im.paste(set_image.crop((0,739,W,810)),(0,739))
    arm(ImageDraw.Draw(im),(x+255,y+304),hand1,-1,'#e6a17b','#e2aa41')
    arm(ImageDraw.Draw(im),(bx+42,by+201),hand2,1,'#e8a577','#e3874c')

def wide_counter(im,d,cue,u,t):
    e=events[cue]
    left=(254,651+3*math.sin(t*3));right=(504,674+2*math.sin(t*2))
    focus=(340,830)
    if cue=='hook':
        tray(d,360,839,240,105)
        for n in range(9):
            dt=u-e['sweets']-.031*n
            size=pop(dt)
            if size<=0:continue
            row,col=divmod(n,3)
            panel_sweet(im,d,n+1,360+100*(col-1),771+row*60-14*(1-min(1,size)),max(3,round(68*size)))
        item,at=('9','nine')
        for key,kind in [('filling','filling'),('turns','2'),('question','?')]:
            if u>=e[key]:item,at=kind,key
        badge_icon(im,item,360,552,u-e[at],158)
        return
    if cue=='rules':
        opened=smooth((u-e['open'])/.42)
        left=(241,743-65*opened)
    if cue=='limit':
        left=(264,670);right=(503+100*(1-smooth((u-e['scale'])/.32)),714)
    moving=cue in ('move','balance','last','guess')
    second=cue in ('last','guess')
    if moving:
        if cue in ('move','last'):
            cl,cr=('seven','eight') if second else ('left','right')
            ls,rs=e[cl],e[cr]
            le,re=(ls+.30,e['weigh']) if second else (e['left_land'],e['right_land'])
            a=smooth((u-ls)/(le-ls));b=smooth((u-rs)/(re-rs))
            tilt=16*(b-a)+3*math.sin(7*max(0,u-re))*(b==1)
        else:
            a=b=1
            tilt=3*(1-smooth(u/e['level']))*math.sin(5*u+.45)
        sa,sb=((225,918),(360,918)) if second else ((209,849),(511,849))
        pa=pos_mix(sa,(193,761-tilt),a,56)
        pb=pos_mix(sb,(527,761+tilt),b,56)
        if cue in ('move','last'):
            def grip(origin,load,rest,start,land):
                reach=smooth((u-start+.15)/.15);release=smooth((u-land)/.33)
                hold=(load[0],load[1]+17)
                return tuple(mix(mix(origin[i],hold[i],reach),rest[i],release) for i in range(2))
            left=grip(left,pa,(235,715),ls,le);right=grip(right,pb,(511,712),rs,re)
        elif cue=='balance':
            left=(248,712);right=(483,739)
        else:left=(236,709);right=(546,627)
        focus=(365,917) if cue=='balance' and u>=e['outside'] else (360,775)
    if cue in ('reveal','tag'):
        z=smooth((u-e['winner'])/.55) if cue=='reveal' else 1
        cy=mix(902,730,z)
        if cue=='tag':cy-=15*math.sin(math.pi*smooth((u-e['caught'])/.40))
        left=(337-48*z,cy+18);right=(389+49*z,cy+18);focus=(365,cy)
    cast(im,t,u,next(s for s in timeline if s['cue']==cue),left,right,focus)
    if cue=='rules':
        if u>=e['box']:box(im,d,smooth((u-e['box']+.035)/.24),opened)
        if e['chanda']<=u<e['box']:label(d,177,653,'CHANDA')
        if e['same']<=u<e['heavy']:
            for i in range(3):flare(d,260+i*99,824,u-e['same']-.13*i)
        badge_icon(im,'mass',585,814,u-e['heavy'],96)
    elif cue=='limit':
        scale_entry(im,d,u-e['scale'])
        if e['aman']<=u<e['scale']+.45:label(d,545,626,'AMAN')
        for j in range(2):badge_icon(im,str(j+1),305+j*110,939,u-e['two']-.10*j,70)
    elif cue=='choose':
        tray(d,360,837,240,101)
        for n in range(9):
            row,col=divmod(n,3);panel_sweet(im,d,n+1,360+102*(col-1),769+row*61,71)
    elif moving:
        scale_actor(d,tilt);tray(d,360,930,205,51)
        if second:
            panel_sweet(im,d,7,*pa,78);panel_sweet(im,d,8,*pb,78);panel_sweet(im,d,9,495,917,78)
            if cue=='last' and u>=e['nine']:
                ellipse(d,495,917,49,43,None,'#317662',4);flare(d,495,917,u-e['nine'])
        else:
            for loc,base in [(pa,1),(pb,4)]:
                for j in range(3):panel_sweet(im,d,base+j,loc[0]+(j-1)*50,loc[1]+10,57)
            for j in range(3):panel_sweet(im,d,7+j,225+135*j,917,78)
            outside_bracket(d,u-e['outside'])
        if cue in ('balance','guess'):
            badge_icon(im,'=',360,750,u-e['level'],65)
            if cue=='guess':badge_icon(im,'?',360,518,u-e['which'],85)
    else:
        tray(d,360,930,205,51)
        w=round(mix(78,141,z))
        put(im,'sweet',left[0]-w*.50,cy-w*.55,w,-9*z)
        if z>.01:put(im,'cut',right[0]-w*.49,cy-w*.57,max(1,round(w*z)),9*z)
        if cue=='reveal':
            for key,kind,x in [('seven','7',268),('eight','8',448),('equal','=',358)]:
                badge_icon(im,kind,x,913,u-e[key],70)
            badge_icon(im,'9',366,565,u-e['answer'],101)
        else:
            if u>=e['weigh']:
                stamp='unused' if u>=e['never'] else 'scale'
                badge_icon(im,stamp,360,910,u-e['weigh'],98)
            flare(d,360,731,u-e['caught'])

def frame(t):
    s=next((s for s in timeline if t<s['end']),timeline[-1])
    u=t-s['start'];cue=s['cue']
    im=set_image.copy();d=ImageDraw.Draw(im)
    wide_counter(im,d,cue,u,t)
    # Physical camera on the set; captions and decision cards stay in screen space.
    # Reaction inserts favor the listener or the evidence, then return to the two-shot.
    zoom,cx,cy=1.0,360,640
    if cue=='hook':zoom=1.12-.085*smooth(u/1.1);cy=668
    if cue=='rules':zoom=1.18;cx=392;cy=640
    if cue=='limit':zoom=1.10;cy=657
    if cue=='balance' and u>events[cue]['outside']:zoom=1.24;cx=388;cy=692
    if cue=='last':zoom=1.08;cy=666
    if cue=='guess':zoom=1.14;cx=380;cy=675
    if cue in ('reveal','tag'):zoom=1.11+.065*smooth(u/1.0) if cue=='reveal' else 1.175;cy=655
    if zoom>1.001:
        cw,ch=W/zoom,H/zoom
        x=max(0,min(W-cw,cx-cw/2));y=max(0,min(H-ch,cy-ch/2))
        im=im.transform((W,H),Image.Transform.EXTENT,(x,y,x+cw,y+ch),Image.Resampling.BICUBIC)
    d=ImageDraw.Draw(im)
    # Full-bleed headlines use the same visual rhythm as the spoken challenge.
    rr(d,(26,32,147,60),12,'#44372f')
    word(d,86,46,'STICKBITS',16,'#fff4d9')
    e=events[cue]
    title=next(block for block in reversed(direction[cue]['titles']) if block['after'] is None or u>=e[block['after']])
    after=title['after'];age=u-(e[after] if after else 0)
    dy=6*(1-smooth(age/.14))
    outlined(d,360,141+dy,title['top'],45,'#fff8e7',630,4)
    outlined(d,360,204+dy,title['bottom'],55,('#92f59b' if cue in ('balance','reveal','tag') else '#ffde55'),644,5)
    if cue=='choose':cards(d,['1 vs 1','3 vs 3','4 vs 4'],u,[e[k] for k in ['a','b','c']])
    if cue=='guess':cards(d,['7','8','9'],u,[e['vote']]*3)
    return im

def make_mix():
    with wave.open(str(OUT/'narration.wav'),'rb') as f:
        rate=f.getframerate()
        assert f.getnchannels()==1 and f.getsampwidth()==2
        voice=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
    fx=np.zeros_like(voice)
    def hit(t,frequency,duration,volume,decay):
        i=round(t*rate)
        n=min(round(duration*rate),len(fx)-i)
        if n<=0:return
        z=np.arange(n)/rate
        env=np.minimum(1,z/.008)*np.exp(-decay*z)
        tone=np.sin(2*math.pi*frequency*z)+.22*np.sin(2*math.pi*2.05*frequency*z)
        fx[i:i+n]+=volume*env*tone
    for row in timeline:
        t=row['start']
        cue=row['cue'];e=events[cue]
        cues={
            'hook':[('sweets',590),('filling',735)],'rules':[('box',295),('open',380)],
            'limit':[('scale',420),('two',640)],'choose':[('a',520),('b',565),('c',610)],
            'move':[('left_land',310),('right_land',360)],'balance':[('level',660)],
            'last':[('weigh',350)],'guess':[('level',540)],'reveal':[('winner',720),('answer',870)],
            'tag':[('never',480)]}
        for name,f in cues[cue]:hit(t+e[name],f,.24,.045,13)
    audio=voice+fx
    audio*=min(1,.88/np.max(np.abs(audio)))
    with wave.open(str(OUT/'mix.wav'),'wb') as f:
        f.setparams((1,2,rate,0,'NONE','not compressed'))
        f.writeframes(np.int16(audio*32767).tobytes())
def render(preview):
    make_mix()
    begin,end=(timeline[4]['start']-.4,timeline[5]['start']+.55) if preview else (0,timeline[-1]['end'])
    name=OUT/('motion-test.mp4' if preview else 'Nau_Laddoo.mp4')
    args=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r',str(FPS),'-i','-','-ss',str(begin),'-t',str(end-begin),'-i',str(OUT/'mix.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','3','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-af','loudnorm=I=-15:TP=-1.5:LRA=8,aresample=48000,alimiter=limit=0.78:level=0:attack=3:release=70:latency=1,volume=-1.8dB','-ar','48000','-movflags','+faststart',str(name)]
    with subprocess.Popen(args,stdin=subprocess.PIPE) as proc:
        for i in range(math.ceil((end-begin)*FPS)):proc.stdin.write(frame(begin+i/FPS).tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError('FFmpeg failed')
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--sheet',type=Path)
    args=parser.parse_args()
    if args.sheet:
        sheet=Image.new('RGB',(5*216,2*384))
        for i,s in enumerate(timeline):
            sheet.paste(frame((s['start']+s['end'])/2).resize((216,384),Image.Resampling.LANCZOS),(i%5*216,i//5*384))
        sheet.save(args.sheet)
    else:render(args.preview)
