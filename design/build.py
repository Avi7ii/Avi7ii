"""Generate compact research cards adapted from OP Bento (GPL-3.0).
No external requests, scripts, embedded HTML, bitmap dependencies or font loaders.
Text outlines use Space Grotesk (OFL-1.1); ornaments reuse OP Bento's SVG paths.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from html import escape
import re
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parent
NS={'s':'http://www.w3.org/2000/svg'}
base=TTFont(ROOT/'source'/'SpaceGrotesk.ttf')
fonts={w:instantiateVariableFont(base,{'wght':w},inplace=False) for w in (400,500,600)}
checks=[]
def txt(s,x,y,size,color,weight=500,spacing=0):
    f=fonts[weight]; units=f['head'].unitsPerEm; scale=size/units; cmap=f.getBestCmap(); glyphs=f.getGlyphSet(); cursor=0; parts=[]
    for char in s:
        name=cmap[ord(char)]; pen=SVGPathPen(glyphs, ntos=lambda n: format(n,".2f").rstrip("0").rstrip(".") if n else "0");glyphs[name].draw(pen);d=pen.getCommands()
        if d: parts.append(f'<path d="{d}" transform="translate({x+cursor:.3f} {y}) scale({scale:.7f} {-scale:.7f})"/>')
        cursor+=f['hmtx'][name][0]*scale+spacing
    checks.append((s,x,y,cursor,size))
    return f'<g fill="{color}" aria-label="{escape(s,quote=True)}">'+''.join(parts)+'</g>'
def rect(x,y,w,h,fill,stroke,r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
def grad(id,a,b):
    return f'<linearGradient id="{id}" x2="1" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
def ornament(name,x,y,w,color,opacity,clip):
    root=ET.fromstring((ROOT/'source'/(name+'.svg')).read_text());tag='polygon' if name=='blocks' else 'path';nodes=root.findall('.//s:'+tag,NS);paths=[]
    for n in nodes:
        prop='points' if tag=='polygon' else 'd';paths.append(f'<{tag} {prop}="{n.attrib[prop]}" opacity="{n.attrib.get("opacity","1")}"/>')
    return f'<g clip-path="url(#{clip})"><g transform="translate({x} {y}) scale({w/800})" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" opacity="{opacity}">'+''.join(paths)+'</g></g>'
def icon(name,x,y,w,color):
    root=ET.fromstring((ROOT/'source'/(name+'.svg')).read_text());children=''.join(ET.tostring(n,encoding='unicode') for n in root)
    return f'<g transform="translate({x} {y}) scale({w/24})" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{children}</g>'
def render(theme,mobile):
    dark=theme=='dark';W,H=(374,388) if mobile else (840,256)
    fg,muted,border,canvas,card=('#edf1f7','#a6afbf','#2b3443','#0d1117','#171c25') if dark else ('#202838','#58647b','#dce2ec','#ffffff','#f3f5fa')
    blue,green,gold=('#b7c9ff','#9ddec8','#d6bf8e') if dark else ('#425ba6','#236c57','#82662f')
    qmc,dmrg=('#c2ecdb','#eadbbd') if dark else ('#296752','#6c5329')
    defs=grad('identity','#354a75','#2d3051')+grad('matter',card,canvas)+grad('qmc','#1a302e' if dark else '#e1f0e9',card)+grad('dmrg','#302e29' if dark else '#efe6d2',card)
    # Compact geometric arrangement; research occupies the largest card.
    if mobile: boxes={'identity':(8,8,175,76),'school':(191,8,175,76),'matter':(8,92,358,130),'qmc':(8,230,175,72),'dmrg':(191,230,175,72),'learning':(8,310,358,70)}
    else: boxes={'identity':(8,8,201,152),'school':(8,170,201,78),'matter':(219,8,335,152),'learning':(219,170,335,78),'methods':(564,8,268,64),'qmc':(564,82,268,78),'dmrg':(564,170,268,78)}
    for key in ('matter','learning'):
        x,y,w,h=boxes[key];defs+=f'<clipPath id="clip-{key}">{rect(x,y,w,h,"white","none")}</clipPath>'
    parts=[f'<rect width="{W}" height="{H}" fill="{canvas}"/>']
    for key,(x,y,w,h) in boxes.items():
        fill={'identity':'url(#identity)','school':'#ece5d6' if dark else '#eee8db','matter':'url(#matter)','learning':'url(#matter)','methods':card,'qmc':'url(#qmc)','dmrg':'url(#dmrg)'}[key]
        parts.append(rect(x,y,w,h,fill,'#455477' if key=='identity' else 'none' if key=='school' else border))
    x,y,w,h=boxes['matter'];parts.append(ornament('blocks',x+w-165,y-10,190,blue,.18 if dark else .12,'clip-matter'))
    x,y,w,h=boxes['learning'];parts.append(ornament('surf',x+w-150,y-65,220,green,.16 if dark else .12,'clip-learning'))
    if mobile:
        parts+= [txt('PHYSICS / COMPUTATION',21,28,8.5,'#c8d5ef',600,.85),txt('Avi7ii',21,64,28,'#fff',600,-1),txt('Yanshan University',204,34,14.5,'#3e392f',600,-.3),txt('Applied Physics',204,55,11.5,'#5e5749'),txt('Undergraduate',204,69,11.5,'#5e5749')]
        parts+=[txt('RESEARCH INTERESTS',22,115,9.5,blue,600,1.1),txt('Quantum',22,147,25,fg,600,-.7),txt('many-body physics',22,175,25,fg,600,-.7),txt('Strongly correlated electron systems',22,206,11.5,muted)]
        for key,label,c1,c2,color in [('qmc','QMC','Quantum Monte Carlo','',qmc),('dmrg','DMRG','Density-matrix','renormalization group',dmrg)]:
            x,y,_,_=boxes[key];parts.append(txt(label,x+13,y+31,25,color,600,-.7));parts.append(txt(c1,x+13,y+51,11.2,color,400));
            if c2:parts.append(txt(c2,x+13,y+64,11.2,color,400))
        parts+=[txt('Physics × machine learning',22,339,20,green,600,-.5),txt('Exploring machine learning algorithms.',22,363,11.3,muted)]
    else:
        parts+=[txt('PHYSICS / COMPUTATION',24,34,9.5,'#c8d5ef',600,1.2),txt('Avi7ii',24,86,38,'#fff',600,-1.5),txt('Exploring quantum matter.',24,116,12.5,'#c8d5ef'),icon('atom',24,131,20,'#c8d5ef')]
        parts+=[txt('Yanshan University',24,196,16,'#3e392f',600,-.3),txt('Applied Physics',24,219,12,'#5e5749'),txt('Undergraduate',24,235,12,'#5e5749')]
        parts+=[txt('RESEARCH INTERESTS',235,34,9.5,blue,600,1.2),txt('Quantum',235,72,27,fg,600,-.8),txt('many-body physics',235,101,27,fg,600,-.8),txt('Strongly correlated',235,132,12.5,muted),txt('electron systems',235,149,12.5,muted),txt('01 / MATTER',461,145,9,muted,400,.9)]
        parts+=[txt('Physics × machine learning',235,202,21,green,600,-.5),txt('Exploring machine learning algorithms.',235,230,12,muted)]
        parts+=[txt('Numerical methods',580,36,18,fg,600,-.4),txt('Tools for quantum matter',580,55,12,muted),icon('sigma',799,27,19,gold)]
        parts+=[txt('QMC',580,132,30,qmc,600,-1),txt('Quantum',744,116,12,qmc),txt('Monte Carlo',744,133,12,qmc)]
        parts+=[txt('DMRG',580,220,30,dmrg,600,-1),txt('Density-matrix',732,192,12,dmrg),txt('renormalization',732,209,12,dmrg),txt('group',732,226,12,dmrg)]
    desc='Avi7ii. Applied Physics undergraduate at Yanshan University. Interests: quantum many-body physics, strongly correlated electron systems, QMC, DMRG, and machine learning algorithms at the intersection of physics and AI.'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">Avi7ii — physics and computation</title><desc id="desc">{desc}</desc><defs>{defs}</defs>'+''.join(parts)+'</svg>'
    # Reuse outlined glyphs inside the SVG; every reference is local.
    glyphs={}
    def reuse(match):
        d,transform=match.groups()
        if d not in glyphs: glyphs[d]=f'g{len(glyphs)}'
        return f'<use href="#{glyphs[d]}" transform="{transform}"/>'
    svg=re.sub(r'<path d="([^"]+)" transform="([^"]+)"/>',reuse,svg)
    glyphdefs=''.join(f'<path id="{id}" d="{d}"/>' for d,id in glyphs.items())
    svg=svg.replace('</defs>',glyphdefs+'</defs>',1)
    ET.fromstring(svg)
    for s,x,y,w,size in checks:
        assert x>=0 and x+w<=W+1,(s,x,w,W)
        assert y<=H,(s,y,H)
    checks.clear()
    name=f'profile-{"mobile" if mobile else "desktop"}-{theme}'
    (ROOT.parent/'assets'/(name+'.svg')).write_text(svg)
for theme in ('dark','light'):
    for mobile in (False,True):render(theme,mobile)
print('Four pure-SVG assets validated; outlined text, no external resources.')
