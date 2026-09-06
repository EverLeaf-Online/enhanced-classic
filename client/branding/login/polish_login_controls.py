#!/usr/bin/env python3
"""Regenerate editable login controls with alpha corners; compose existing logo."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
src,out=map(Path,sys.argv[1:3]);out.mkdir(parents=True,exist_ok=True)
S=4
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def surface(w,h): return Image.new('RGBA',(w*S,h*S),(0,0,0,0))
def rr(d,b,r,**kw):
    if 'width' in kw:kw['width']*=S
    d.rounded_rectangle(tuple(int(x*S) for x in b),radius=r*S,**kw)
def text(d,b,t,size):
    f=ImageFont.truetype(fontpath,size*S)
    q=d.textbbox((0,0),t,font=f)
    x=(b[0]+b[2])*S/2-(q[2]-q[0])/2
    y=(b[1]+b[3])*S/2-(q[3]-q[1])/2-q[1]
    d.text((x,y),t,font=f,fill=(250,248,226,255),stroke_width=S,stroke_fill=(15,26,8,255))
def save(im,name):im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS).save(out/name)
im=surface(368,236);d=ImageDraw.Draw(im)
rr(d,(2,2,365,233),12,fill=(18,31,15,202),outline=(201,195,137,230),width=4)
rr(d,(7,7,360,228),9,fill=(28,47,20,185),outline=(140,171,84,188),width=2)
rr(d,(11,10,356,80),7,fill=(10,23,14,200),outline=(180,204,115,190),width=1)
for label,y in [('Login ID',18),('Password',53)]:
    d.text((17*S,y*S),label,font=ImageFont.truetype(fontpath,10*S),fill=(248,244,218,255),stroke_width=S,stroke_fill=(14,22,8,255))
for y in (10,45):rr(d,(63,y,213,y+31),5,fill=(10,23,14,210),outline=(168,190,99,230),width=2)
for y in (88,126):d.line((12*S,y*S,356*S,y*S),fill=(163,180,98,175),width=S)
save(im,'signboard.png')
palette={'normal':((54,101,20,255),(158,207,66,255)),'mouseOver':((74,132,24,255),(205,236,91,255)),'pressed':((37,74,13,255),(125,174,42,255)),'disabled':((61,78,46,255),(112,132,84,255))}
for name,t,w,h,fs in [('login','LOG IN',89,42,14),('save-id','SAVE ID',76,23,9),('find-id','FIND ID',82,23,9),('reset-password','RESET',66,23,9),('register','REGISTER',92,38,11),('homepage','HOMEPAGE',93,38,10),('quit','QUIT',84,38,11)]:
    for state,(fill,edge) in palette.items():
        im=surface(w,h);d=ImageDraw.Draw(im)
        rr(d,(1,1,w-2,h-2),max(4,h//6),fill=fill,outline=(14,30,7,255),width=2)
        rr(d,(4,4,w-5,h-5),max(3,h//8),outline=edge,width=1)
        text(d,(4,2,w-4,h-2),t,fs)
        save(im,name+'-'+state+'.png')
logo=Image.open(src/'logo.png').convert('RGBA')
assert logo.size==(397,219)
clean=Image.new('RGBA',logo.size)
clean.alpha_composite(logo.crop((0,0,397,150)),(0,20))
clean.save(out/'logo.png')
Image.open(src/'panorama-extended-source.png').convert('RGBA').resize((1400,3240),Image.Resampling.LANCZOS).save(out/'background.png')
for p in out.glob('*.png'):
    if p.name=='background.png':continue
    im=Image.open(p)
    assert im.mode=='RGBA'
    assert all(im.getpixel(x)[3]==0 for x in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]),p
print('Generated controls; all outer corner pixels fully transparent.')
