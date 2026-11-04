"""Render the recorded Interna walkthrough, title cards, captions and local voiceover.

Run with the bundled Python runtime (Pillow, numpy). Captured browser frames are
real UI frames collected using cua_repl; no UI response is generated here.
"""
import json, math, re, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source/vendor'))
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
SCENES = json.loads((ROOT / 'source/scenes.json').read_text())
DURATIONS = json.loads((ROOT / 'audio/durations.json').read_text())
W, H, FPS, SPEED = 1920, 1080, 24, 1.0
CREAM, GREEN, INK, MINT, MUTED = '#f4f5ee', '#214f40', '#18392f', '#bfd69b', '#69786f'
FONTS = Path('/System/Library/Fonts/Supplemental')
ASSETS = ROOT / 'assets'
RENDER = ROOT / 'source/render'
ASSETS.mkdir(exist_ok=True)
RENDER.mkdir(exist_ok=True)

def run(args):
    p = subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', *map(str,args)], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace')[-5000:])

def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ('Arial Bold.ttf' if bold else 'Arial.ttf')), size)

def label(d, xy, text, size=28, fill=INK, bold=False):
    d.text(xy, text, font=font(size,bold), fill=fill)

def wrapped(d, text, x, y, width, size=34, color=INK, bold=False, spacing=12):
    words, line = text.split(), ''
    for word in words:
        candidate = (line+' '+word).strip()
        if d.textlength(candidate, font=font(size,bold)) > width and line:
            label(d,(x,y),line,size,color,bold); y += size+spacing; line=word
        else: line=candidate
    if line: label(d,(x,y),line,size,color,bold); y+=size+spacing
    return y

def base(scene, dark=False):
    im=Image.new('RGB',(W,H),GREEN if dark else CREAM);d=ImageDraw.Draw(im)
    label(d,(90,42),scene['chapter'],22,MINT if dark else GREEN,True)
    label(d,(1690,38),'interna',32,CREAM if dark else GREEN,True)
    d.line((90,93,1830,93),fill='#527566' if dark else '#dce3d8',width=2)
    return im,d

def bullet(d, x,y,title,body,width=660,dark=False):
    d.ellipse((x,y+8,x+12,y+20),fill=MINT if dark else GREEN)
    label(d,(x+30,y),title,31,CREAM if dark else INK,True)
    return wrapped(d,body,x+30,y+48,width,27,'#d7e4d5' if dark else MUTED)+28

def card(scene, variant=0):
    kind=scene['kind'];dark=kind in ['title','outro','solution'];im,d=base(scene,dark)
    if kind=='title':
        label(d,(100,178),'AI MENTOR AGENT',27,MINT,True)
        wrapped(d,scene['title'],100,264,1000,99,CREAM,True,10)
        wrapped(d,'Không gian đào tạo và kèm cặp thực tập sinh công nghệ.',105,531,880,39,'#dce9dc',False,16)
        d.rounded_rectangle((105,704,650,775),22,fill=MINT)
        label(d,(132,723),'MVP 30%  /  MINI HACKATHON 2026',24,INK,True)
        for k,(t,n) in enumerate([('Nhận việc','01'),('Tự tìm hiểu','02'),('Nhận phản hồi','03')]):
            yy=255+k*172;d.rounded_rectangle((1230,yy,1810,yy+126),24,fill='#386351')
            label(d,(1264,yy+35),n,38,MINT,True);label(d,(1352,yy+41),t,32,CREAM,True)
    elif kind=='problem':
        wrapped(d,scene['title'],95,158,1690,71,INK,True)
        for x,title,tag,body in [(95,'Mentor / Tech Lead','01','Câu hỏi lặp lại\nKhó theo sát quá trình\nThiếu minh chứng để trao đổi'),(1000,'Thực tập sinh','02','Bỡ ngỡ với quy chuẩn\nThiếu hướng dẫn sát sao\nDễ sao chép mà chưa hiểu')]:
            d.rounded_rectangle((x,337,x+825,827),30,fill='white',outline='#dce3d8',width=2)
            label(d,(x+42,375),tag,52,GREEN,True);label(d,(x+42,465),title,44,INK,True)
            for i,line in enumerate(body.split('\n')):label(d,(x+44,563+i*67),'•  '+line,32,MUTED)
    elif kind=='solution':
        wrapped(d,scene['title'],95,156,1700,77,CREAM,True)
        items=[('01','NHIỆM VỤ','Học qua công việc thực tế'),('02','AI MENTOR','Gợi mở theo quy chuẩn'),('03','MENTOR','Phản hồi có minh chứng')]
        for i,(n,title,sub) in enumerate(items):
            x=95+i*597;d.rounded_rectangle((x,395,x+553,719),28,fill='#386351')
            label(d,(x+35,428),n,57,MINT,True);label(d,(x+35,529),title,37,CREAM,True)
            wrapped(d,sub,x+35,600,470,28,'#dbe7d8')
        label(d,(100,815),'Đọc yêu cầu  →  Tự thực hiện  →  Giải trình  →  Cải thiện',35,MINT,True)
    elif kind=='roadmap':
        wrapped(d,scene['title'],95,143,1700,64,INK,True)
        data=[('30%','MVP HIỆN TẠI','Hai vai trò · Nộp & duyệt bài','RAG / ChromaDB','Ollama hoặc Gemini'),('60%','DỰ KIẾN','PostgreSQL tập trung','Container Docker','Google Cloud Run'),('100%','ĐỊNH HƯỚNG','Multi-Agent chuyên trách','Code review & bảo mật','Báo cáo năng lực')]
        for i,items in enumerate(data):
            x=95+i*597;active=i==variant;bg=GREEN if active else 'white';fg=CREAM if active else INK
            d.rounded_rectangle((x,315,x+553,848),26,fill=bg,outline=GREEN if active else '#dce3d8',width=3)
            label(d,(x+34,349),items[0],83,MINT if active else GREEN,True)
            label(d,(x+37,465),items[1],25,fg,True)
            for k,txt in enumerate(items[2:]):wrapped(d,txt,x+37,548+k*88,470,29,fg)
        label(d,(100,889),'Mốc tiếp theo là kế hoạch phát triển, chưa phải tính năng đã triển khai.',25,MUTED)
    elif kind=='future':
        wrapped(d,scene['title'],95,151,1710,66,INK,True)
        y=340
        for title,body in [('Multi-Agent trong quy trình Git','Code Reviewer và Security Gatekeeper hỗ trợ kiểm tra thay đổi.'),('Báo cáo năng lực / Skill Radar','Tổng hợp bài làm và tương tác, hỗ trợ mentor đánh giá cuối kỳ.'),('Dịch vụ cho tổ chức','Dữ liệu tập trung, phân quyền và quy trình onboarding thống nhất.')]:
            d.rounded_rectangle((95,y,1825,y+152),24,fill='white',outline='#dce3d8',width=2)
            bullet(d,130,y+25,title,body,1580);y+=179
    elif kind=='outro':
        label(d,(100,202),'INTERNA',100,CREAM,True)
        wrapped(d,scene['title'],100,363,1710,84,CREAM,True)
        label(d,(106,563),'Nhận việc  /  Tự học  /  Thực hành  /  Phản hồi',37,MINT,True)
        label(d,(106,727),'Cảm ơn bạn đã theo dõi.',43,CREAM,True)
        label(d,(106,805),'Mini Hackathon 2026 · Bản giới thiệu MVP 30%',27,'#d2dfcf')
    return im

def screen(scene,path):
    im,d=base(scene)
    label(d,(90,111),scene['title'],32,INK,True)
    shot=Image.open(path).convert('RGB').resize((1440,810),Image.Resampling.LANCZOS)
    # A dedicated video frame keeps the whole UI visible above the caption area.
    im.paste(shot,(240,170))
    d=ImageDraw.Draw(im);d.rounded_rectangle((239,169,1681,981),15,outline='#c4d1c5',width=2)
    label(d,(90,311),'DEMO',24,GREEN,True)
    label(d,(90,351),'LOCAL',24,GREEN,True)
    label(d,(90,884),'MVP',24,MUTED,True);label(d,(90,921),'30%',34,GREEN,True)
    return im

def focus(scene,kind):
    im,d=base(scene,True)
    strict=kind=='strict';path=ROOT/'captures'/('05-strict.png' if strict else '07-rag.png')
    # Crop only for editorial magnification; original response pixels stay intact.
    crop=Image.open(path).convert('RGB').crop((1027,96 if strict else 65,1567,707 if strict else 674))
    crop=crop.resize((723,816),Image.Resampling.LANCZOS);im.paste(crop,(1097,133))
    label(d,(100,173),'01' if strict else '02',95,MINT,True)
    wrapped(d,'AI không làm bài thay bạn.' if strict else 'Quy chuẩn có nguồn để đối chiếu.',100,320,870,68,CREAM,True)
    yy=580
    for title,body in ([('Giữ vai trò hướng dẫn','Nhắc quy tắc tự học và đặt câu hỏi gợi mở.'),('Lưu dấu vết tương tác','Mentor có thêm ngữ cảnh khi review.')] if strict else [('Dựa trên tài liệu nội bộ','Nguồn intern_portal.md xuất hiện trong phản hồi.'),('Người học tiếp tục suy nghĩ','Tự đề xuất cách kiểm tra và xử lý mã trùng.')]):
        yy=bullet(d,104,yy,title,body,800,True)
    label(d,(101,916),'PHẢN HỒI THỰC TẾ  /  OLLAMA · STRICTMENTOR',22,MINT,True)
    return im

def normalized(text):
    return text.replace('In tơ na','Interna').replace('Ô la ma','Ollama').replace('Chroma DB','ChromaDB')

def subtitle_chunks(text):
    words=normalized(text).split();chunks=[];current=[]
    for word in words:
        current.append(word)
        if len(current)>=17 or (len(current)>=8 and word.endswith(('.', '!', '?', ':', ';'))):
            chunks.append(' '.join(current));current=[]
    if current:chunks.append(' '.join(current))
    return chunks

def stamp(sec,ass=False):
    if ass:
        cs=round(sec*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
    ms=round(sec*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'

ASS_HEADER='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,32,&H00FFFFFF,&H00FFFFFF,&H00152E25,&H00152E25,0,0,0,0,100,100,0,0,3,10,0,2,210,210,23,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''

def build():
    SCENES[9]['clips']=['12-logout','13-overview','14-activity']
    SCENES[10]['clips']+=['17b-result']
    SCENES[11]['clips']=['18-add-form','18b-add-fill','19-add-confirm']
    absolute=0;srt=[];chapterlines=[];concat=[];allsubs=[]
    for idx,scene in enumerate(SCENES):
        duration=math.ceil((DURATIONS[scene['id']]/SPEED+0.65)*FPS)/FPS
        audiodur=DURATIONS[scene['id']]/SPEED
        scene['duration']=duration;scene['start']=absolute
        chapterlines.append(f"{int(absolute)//60:02d}:{int(absolute)%60:02d} {scene['title']}")
        events=[];chunks=subtitle_chunks(scene['voice']);weights=[len(c.split())+0.4*c.count(',')+0.7*c.count('.') for c in chunks];ws=sum(weights);cursor=.22
        for txt,weight in zip(chunks,weights):
            end=min(audiodur+.25,cursor+audiodur*weight/ws)
            # Split the on-screen caption into at most two balanced lines.
            ww=txt.split();mid=len(ww)//2
            if len(txt)>78:txt=' '.join(ww[:mid])+r'\N'+' '.join(ww[mid:])
            events.append(f'Dialogue: 0,{stamp(cursor,True)},{stamp(end,True)},Default,,0,0,0,,{txt}')
            srt.append((absolute+cursor,absolute+end,txt.replace(r'\N','\n')));cursor=end
        ass=RENDER/(scene['id']+'.ass');ass.write_text(ASS_HEADER+'\n'.join(events)+'\n')
        frames=[]
        def still(image,name,seconds):
            p=ASSETS/(name+'.png');image.save(p);frames.append((p,seconds))
        if scene['kind']!='screen':
            if scene['kind']=='roadmap':
                for k,fraction in enumerate([.49,.25,.26]):still(card(scene,k),scene['id']+f'-{k}',duration*fraction)
            else:still(card(scene),scene['id'],duration)
        else:
            names=scene['clips'];focus_time=duration*.49 if 'focus' in scene else 0
            slots=(duration-focus_time)/len(names)
            for name in names:
                info=json.loads((ROOT/'captures'/name/'timing.json').read_text());raw=info['frames']
                # Preserve recorded timing, then hold the final frame for the narration.
                scale=min(1,slots/max(info['duration'],.1));used=0
                for j,f in enumerate(raw):
                    p=RENDER/(scene['id']+'-'+name+'-'+f['file'])
                    screen(scene,ROOT/'captures'/name/f['file']).save(p)
                    dt=((raw[j+1]['t']-f['t']) if j+1<len(raw) else max(.12,info['duration']-f['t']))*scale
                    frames.append((p,dt));used+=dt
                if slots>used:frames[-1]=(frames[-1][0],frames[-1][1]+slots-used)
            if focus_time:still(focus(scene,scene['focus']),scene['id']+'-focus',focus_time)
        fc=RENDER/(scene['id']+'.ffconcat');fc.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\nduration {dt:.6f}\n" for p,dt in frames)+f"file '{frames[-1][0]}'\n")
        output=RENDER/(scene['id']+'.mp4')
        filters=f"fps={FPS},ass='{ass}',fade=t=in:st=0:d=0.24,fade=t=out:st={duration-.22}:d=0.22,format=yuv420p"
        run(['-f','concat','-safe','0','-i',fc,'-i',ROOT/'audio'/(scene['id']+'.aiff'),'-vf',filters,'-af',f'atempo={SPEED},loudnorm=I=-16:TP=-1.5:LRA=7,adelay=220|220,apad','-t',duration,'-r',FPS,'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',output])
        concat.append(output);absolute+=duration
        print(f"Rendered {idx+1}/{len(SCENES)}: {scene['id']} ({duration:.2f}s)",flush=True)
    (ROOT/'INTERNA_REVIEW_VI.srt').write_text('\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{t}\n' for i,(a,b,t) in enumerate(srt,1)))
    (ROOT/'CHAPTERS.txt').write_text('\n'.join(chapterlines)+'\n')
    (ROOT/'source/timeline.json').write_text(json.dumps(SCENES,ensure_ascii=False,indent=2))
    allclips=RENDER/'all.ffconcat';allclips.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\n" for p in concat))
    run(['-f','concat','-safe','0','-i',allclips,'-c','copy',RENDER/'joined.mp4'])
    music(absolute)
    chapters=RENDER/'chapters.ffmetadata'
    meta=';FFMETADATA1\ntitle=Interna — AI Mentor Agent | Mini Hackathon 2026\ncomment=Real local browser walkthrough with Vietnamese synthetic narration.\n'
    for scene in SCENES:meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(scene['start']*1000)}\nEND={round((scene['start']+scene['duration'])*1000)}\ntitle={scene['title']}\n"
    chapters.write_text(meta)
    run(['-i',RENDER/'joined.mp4','-i',ROOT/'audio/music-original.wav','-i',chapters,'-filter_complex','[1:a]volume=0.10,afade=t=in:d=2,afade=t=out:st='+str(absolute-4)+':d=4[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.96[a]','-map','0:v','-map','[a]','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',ROOT/'INTERNA_REVIEW_1080p_VI.mp4'])
    # A separate narration file supports later editing in any video editor.
    run(['-i',RENDER/'joined.mp4','-vn','-c:a','aac','-b:a','192k',ROOT/'audio/THUYET_MINH_VI.m4a'])
    card(SCENES[0]).save(ROOT/'INTERNA_POSTER.png')
    print(f'Finished: {absolute:.3f}s',flush=True)

def music(duration):
    rate=32000;chords=[(130.81,164.81,196),(110,130.81,164.81),(87.31,110,130.81),(98,123.47,146.83)]
    with wave.open(str(ROOT/'audio/music-original.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate)
        for start in range(0,math.ceil(duration),6):
            count=min(6,duration-start);t=np.arange(int(count*rate))/rate;env=np.minimum(t/1.1,1)*np.minimum((count-t)/1.5,1);signal=np.zeros_like(t)
            for hz in chords[(start//6)%4]:signal+=.025*np.sin(2*np.pi*hz*t)+.009*np.sin(2*np.pi*(hz*2+.18)*t)
            signal*=env;right=signal*.94
            w.writeframes((np.column_stack((signal,right))*32767).astype('<i2').tobytes())

if __name__=='__main__':build()
