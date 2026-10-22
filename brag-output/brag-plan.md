# Launch video plan

20 seconds, 1920x1080, 30 fps. Tone: **polished**, matching the site itself:
dark navy, Cormorant Garamond display type, the blue-cyan-violet gradient.

## Answers

- **What is it?** Five LLM agents that research stocks for a beginner, then
  argue against their own picks before any survive.
- **Who for?** Someone who doesn't know where to start, and wants research
  they can check rather than a tip.
- **What sets it apart?** Every exit condition cites an article it read or a
  number it measured, and "nothing" is a first-class answer.
- **Most striking claim:** it attacks its own conclusions, and may recommend
  nothing at all.
- **Visual hook:** the hook line set in the site's display serif, with the
  twist line in the site's gradient italic.
- **Real UI shown:** the five step tiles, a recorded ASML brief with its
  `Check:` citation, the "Nothing is being recommended" card. All captured
  from the running app (`scripts/capture_ui.py`) from recorded gallery runs,
  so no model call, no quota and no personal data.
- **Share caption:** see `share-copy.txt`.

## Angle

An investment tool whose best feature is doubt. The joke tells itself: you
ask for a stock pick and it argues with you about it.

## Storyboard

| # | Time | Scene | On screen |
|---|------|-------|-----------|
| 1 | 0.0-4.0 | Hook | "Five AI agents research stocks for you." then, in gradient italic, "Then they argue against every pick." |
| 2 | 4.0-8.0 | Reveal | Real site title drops in; the five real step tiles land one by one; 04 Critique lifts and glows. |
| 3 | 8.0-12.8 | Highlight: grounded | Real ASML brief pans from thesis to exit conditions; a gradient box draws round the `Check:` citation. Caption: "Every claim cites what it read." |
| 4 | 12.8-16.6 | Highlight: nothing | Real "Nothing is being recommended" card rises in. Caption: "And when nothing holds up, it says so." |
| 5 | 16.6-20.0 | Outro | Site title, "Research, not advice.", repo URL. |

Transitions dip through the background (old out, then new in), never a
crossfade of two busy layouts.

## Sound

One synthesized piece (`scripts/audio.py`, numpy only): a slow D-minor pad at
84 bpm, a soft low pulse, quiet plucks in key as each step tile lands, a
swell into the citation box and a resolving D-major chord on the outro.

## Build

1. `python -m uvicorn frontend.app:app --port 8765`
2. `python brag-output/scripts/capture_ui.py brag-output/work/ui`
3. `python brag-output/scripts/build.py`: renders `composition.html` frame
   by frame with Playwright, synthesizes audio, encodes with the
   `imageio-ffmpeg` binary installed into `brag-output/work/tools`, and bakes
   the poster as frame 0.
