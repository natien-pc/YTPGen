# YTPDeluxe (YTPGen) — Python + Tkinter YTP Generator (Windows 8.1 friendly)

YTPDeluxe is a Python/Tkinter GUI for randomly generating nonsensical video remixes / mashups (aka "YouTube Poop" style edits). This project is a modern Python recreation of the classic Java and older Python GUI versions, with a focus on compatibility with older Windows systems (Windows 8.1) when paired with a local FFmpeg binary.

IMPORTANT: Some combinations of effects may produce rapid flashing or disorienting visuals. Use with caution.

Contents
- ytpgen.py — main entry (launch GUI)
- gui.py — Tkinter GUI logic
- effects.py — effect definitions and FFmpeg filter builders
- ffmpeg_utils.py — helpers to build and run FFmpeg commands
- requirements.txt — optional Python dependencies
- assets/ — organized directories for sounds, overlays, sources, etc.
- temp/ — temporary working files
- README.md — this file

Quick setup (Windows 8.1)
1. Install Python 3.8+ for Windows (make sure `python` is on PATH).
2. Download a statically built FFmpeg compatible with Windows 8.1 and place `ffmpeg.exe` in a folder on PATH or edit the path in the GUI settings.
   - Example: https://www.gyan.dev/ffmpeg/builds/ (use the "essentials" build)
3. Install optional Python packages (Pillow is used for some overlay handling):
   - pip install -r requirements.txt
4. Extract the repository somewhere convenient.
5. Prepare your assets:
   - assets/sounds/ — meme SFX and stingers
   - assets/overlays/ — PNG/GIF overlays (memes)
   - assets/sources/ — raw video sources you want YTPGen to use
6. Launch:
   - python ytpgen.py

What it does
- Let you add source video files, toggle effects, set probabilities/strengths.
- Build randomized effect chains and run FFmpeg to produce previews and final exports.
- Basic set of implemented effects: invert colors, flip, mirror, reverse, speed up / slow down, stutter loop, chorus (aecho), vibrato/pitch-bend approximation, earrape (gain), rainbow overlay (user-provided overlay recommended).
- Many features are scaffolded so you can extend them: Shuffle Frames, Loop Frames, Auto-Tune Chaos, etc.

Notes and limitations
- This tool delegates all heavy processing to FFmpeg. The GUI simply constructs filterchains and runs ffmpeg.exe. Make sure your FFmpeg build supports the filters used (most modern builds do).
- Some effects require overlay assets (rainbow/memes). The README's assets folder includes recommended structure; add your own files.
- Frame-precise effects (Loop Frames, Shuffle Frames) are provided as scaffolds and may be slow on large files. They rely on image sequence extraction—optimize for your content.
- This is a starting project scaffold. Many "chaos" features are intentionally randomized with placeholders to be refined.

Safety
- Use `Earrape Mode` and high-gain audio effects carefully — use headphones or speakers at low volume when testing.

License
- MIT-style permissive license. Use responsibly.

If you want, I can:
- Create an installer/batch to bundle ffmpeg.exe and a portable Python runtime.
- Add more complete implementations for frame shuffling and Auto-Tune integration (requires third-party tools).
- Generate a sample assets pack with permissively licensed sounds/overlays.
