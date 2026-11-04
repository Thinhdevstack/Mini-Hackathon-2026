"""Create Vietnamese narration locally with the installed macOS Linh voice."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import re

ROOT = Path(__file__).resolve().parents[1]
SCENES = json.loads((ROOT / 'source/scenes.json').read_text())

def create(scene):
    path = ROOT / 'audio' / (scene['id'] + '.aiff')
    subprocess.run(['say', '-v', 'Linh', '-r', '180', '-o', str(path), scene['voice']], check=True)
    metadata = subprocess.check_output(['afinfo', str(path)], text=True)
    duration = float(re.search(r'estimated duration: ([0-9.]+)', metadata)[1])
    if duration < 1:
        raise RuntimeError('No speech generated: ' + scene['id'])
    print(f"{scene['id']}: {duration:.2f}s", flush=True)
    return scene['id'], duration

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        durations = dict(pool.map(create, SCENES))
    (ROOT / 'audio/durations.json').write_text(json.dumps(durations, indent=2))
    print('Narration:', round(sum(durations.values()), 2), 'seconds')
