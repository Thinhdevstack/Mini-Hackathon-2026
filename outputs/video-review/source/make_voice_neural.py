"""Create high-definition natural Vietnamese narration using Edge TTS Neural Voice."""
import asyncio
import json
from pathlib import Path
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source/vendor'))
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()

SCENES = json.loads((ROOT / 'source/scenes.json').read_text())
VOICE = "vi-VN-HoaiMyNeural"

async def generate_scene(scene, voice=VOICE):
    mp3_path = ROOT / 'audio' / (scene['id'] + '.mp3')
    aiff_path = ROOT / 'audio' / (scene['id'] + '.aiff')
    
    for attempt in range(6):
        try:
            import edge_tts
            comm = edge_tts.Communicate(scene['voice'], voice=voice, rate='+2%')
            await comm.save(str(mp3_path))
            break
        except Exception as e:
            print(f"[{scene['id']}] Attempt {attempt+1} failed: {e}. Retrying in 1.5s...", flush=True)
            await asyncio.sleep(1.5)
    else:
        raise RuntimeError(f"Failed to generate speech for {scene['id']}")
    
    # Master audio to 48kHz stereo with vocal enhancement
    subprocess.run([
        FF, '-hide_banner', '-loglevel', 'error', '-y',
        '-i', str(mp3_path),
        '-af', 'highpass=f=80,equalizer=f=400:t=q:w=1:g=-2,equalizer=f=4500:t=q:w=1:g=+2',
        '-ar', '48000', '-ac', '2',
        str(aiff_path)
    ], check=True)
    
    metadata = subprocess.check_output(['afinfo', str(aiff_path)], text=True)
    duration = float(re.search(r'estimated duration: ([0-9.]+)', metadata)[1])
    if duration < 1:
        raise RuntimeError('No speech generated: ' + scene['id'])
    print(f"✓ {scene['id']}: {duration:.2f}s", flush=True)
    return scene['id'], duration

async def main():
    print(f"Generating studio-grade Neural narration for {len(SCENES)} scenes with {VOICE}...")
    durations = {}
    for scene in SCENES:
        sid, dur = await generate_scene(scene)
        durations[sid] = dur
        await asyncio.sleep(0.3)
    
    (ROOT / 'audio/durations.json').write_text(json.dumps(durations, indent=2))
    total_seconds = round(sum(durations.values()), 2)
    print(f"\nAll scenes generated successfully! Total narration: {total_seconds} seconds ({total_seconds//60:.0f}m {total_seconds%60:.1f}s)")

if __name__ == '__main__':
    asyncio.run(main())
