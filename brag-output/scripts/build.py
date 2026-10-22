"""Render brag-output/brag.mp4 and brag.jpg from composition.html.

    python brag-output/scripts/build.py --stills 1.0 3.5 ...   # check frames
    python brag-output/scripts/build.py                        # full render

Needs the UI captures (capture_ui.py) and ffmpeg from imageio-ffmpeg installed
into brag-output/work/tools:
    pip install --target brag-output/work/tools imageio-ffmpeg
"""
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent
WORK = OUT / "work"
sys.path.insert(0, str(WORK / "tools"))
import imageio_ffmpeg  # noqa: E402

import audio  # noqa: E402  (sibling script)

FPS, DURATION = 30, 20.0
POSTER_T = 11.5          # settled: citation boxed, caption fully in
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def frames(times, dest):
    dest.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto((OUT / "scripts" / "composition.html").as_uri())
        pg.evaluate("window.ready")
        for name, t in times:
            pg.evaluate(f"render({t})")
            pg.screenshot(path=str(dest / name))
        b.close()


def ff(*args):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *args], check=True)


def main():
    if "--stills" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]
        frames([(f"still-{t:05.2f}.png", t) for t in ts], WORK / "stills")
        return

    n = int(FPS * DURATION)
    frames([(f"{i:04d}.png", i / FPS) for i in range(n)], WORK / "frames")
    frames([("poster.png", POSTER_T)], WORK)
    ff("-i", str(WORK / "poster.png"), "-q:v", "2", str(OUT / "brag.jpg"))

    # Bake the poster in as frame 0 by replacing it, not prepending, so the
    # duration and audio sync are unchanged.
    (WORK / "frames" / "0000.png").write_bytes((WORK / "poster.png").read_bytes())

    wav = WORK / "audio.wav"
    audio.write(wav, DURATION)
    ff("-framerate", str(FPS), "-i", str(WORK / "frames" / "%04d.png"), "-i", str(wav),
       "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
       str(OUT / "brag.mp4"))
    print("wrote", OUT / "brag.mp4", "and", OUT / "brag.jpg")


if __name__ == "__main__":
    main()
