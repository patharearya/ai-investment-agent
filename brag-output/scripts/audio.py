"""Synthesize the soundtrack: one piece, music and effects in the same key.

D minor at 84 bpm. A soft pad walks Dm - Bb - F - C and resolves to D major
on the outro; quiet plucks land with each step tile, a chime marks the
citation box. Everything shares one reverb so the effects sit inside the music
rather than on top of it. Cue times match render() in composition.html.
"""
import wave

import numpy as np

SR = 44100
BEAT = 60 / 84


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def soft_saw(f, t, detune):
    # Additive, band-limited, with a steep roll-off: a warm saw without a filter.
    out = np.zeros_like(t)
    for k in range(1, 14):
        if f * k > SR / 2:
            break
        out += np.sin(2 * np.pi * f * k * t * (1 + detune)) / k * np.exp(-k / 3.5)
    return out


def tone(f, dur, decay, partials=((1, 1.0), (2, .35), (3, .12))):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t / decay) * np.minimum(1, t / .004)
    return sum(a * np.sin(2 * np.pi * f * m * t) for m, a in partials) * env


def add(buf, sig, at, gain, pan=0.0):
    i = int(at * SR)
    sig = sig[: max(0, buf.shape[1] - i)]
    buf[0, i:i + len(sig)] += sig * gain * (1 - pan) ** .5
    buf[1, i:i + len(sig)] += sig * gain * (1 + pan) ** .5


def write(path, duration):
    n = int(duration * SR)
    t = np.arange(n) / SR
    dry = np.zeros((2, n))

    # Pad: (start, end, midi notes). Overlapping 0.6s fades between chords.
    chords = [(0, 4.0, [50, 57, 62, 65]),        # Dm
              (4.0, 8.0, [46, 58, 62, 65]),      # Bb
              (8.0, 12.8, [53, 57, 60, 65]),     # F
              (12.8, 16.6, [48, 55, 60, 64]),    # C
              (16.6, duration, [50, 57, 62, 66])]  # D major: the resolve
    for a, b, notes in chords:
        env = np.clip((t - a + .3) / .6, 0, 1) * np.clip((b + .3 - t) / .6, 0, 1)
        for ch, det in ((0, -.0025), (1, .0025)):
            dry[ch] += env * sum(soft_saw(hz(m), t, det) for m in notes) * .05

    # Low pulse on each beat from the reveal on: felt more than heard.
    root = {0: 38, 4.0: 34, 8.0: 41, 12.8: 36, 16.6: 38}
    for i in range(int(duration / BEAT)):
        at = i * BEAT
        if at < 4.0 - .01 or at > duration - 1.0:
            continue
        r = max(k for k in root if k <= at + 1e-9)
        add(dry, tone(hz(root[r]), .6, .18, ((1, 1), (2, .2))), at, .16)

    # Hook: a single soft note as the second line lands.
    add(dry, tone(hz(74), 2.5, .9), 1.45, .05, -.2)
    # Step tiles: an ascending D-minor pentatonic pluck per tile, gently panned.
    for i, m in enumerate([62, 65, 67, 69, 72]):
        add(dry, tone(hz(m + 12), 1.2, .35), 4.5 + .2 * i, .05, -.5 + .25 * i)
    add(dry, tone(hz(86), 2.5, .8), 6.0, .07)            # Critique lifts
    # Swell into the citation box, then a two-note chime as it draws.
    sw = np.clip((t - 9.2) / .8, 0, 1) ** 2 * (t < 10.05)
    for m in (69, 74, 77):
        dry += sw * np.sin(2 * np.pi * hz(m) * t) * .025
    add(dry, tone(hz(81), 2.5, .9), 10.0, .06, -.15)
    add(dry, tone(hz(88), 2.5, .9), 10.12, .045, .15)
    add(dry, tone(hz(74), 2.5, 1.0), 13.4, .05)           # the "nothing" card
    for m, p in ((62, -.3), (66, 0), (69, .3), (74, 0)):  # outro D major bell
        add(dry, tone(hz(m + 12), 4.0, 1.4), 16.75, .05, p)

    # One shared reverb: exponentially decaying noise, convolved by FFT.
    rng = np.random.default_rng(7)
    ir_t = np.arange(int(2.2 * SR)) / SR
    wet = np.zeros_like(dry)
    for ch in (0, 1):
        ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / .55)
        ir /= np.sqrt((ir ** 2).sum())
        m = n + len(ir) - 1
        wet[ch] = np.fft.irfft(np.fft.rfft(dry[ch], m) * np.fft.rfft(ir, m), m)[:n]
    mix = dry * .8 + wet * .45

    mix *= np.clip(t / .4, 0, 1) * np.clip((duration - t) / .8, 0, 1)
    mix = np.tanh(mix / np.abs(mix).max() * 1.1) * .85    # gentle limiter, ~-1.4 dBFS

    pcm = (mix.T * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    import sys
    write(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 20.0)
