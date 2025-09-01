# assets/ — Organized asset folders for YTPDeluxe (YTPGen)

This folder is the central place to store media and helper files used by the YTPDeluxe generator.

Structure
- sounds/         — short meme SFX, stingers, vocal drops (wav, mp3, ogg)
- soundos/        — UI sounds: startup, shutdown, button clicks (wav)
- errors/         — short "computer/console" error clips or glitch sounds
- advert/         — short commercial/parody ad clips and jingles
- memes/          — transparent overlays, meme PNGs, GIFs (use 25% alpha convention if desired)
- overlays/       — decorative overlays (rainbow PNG/GIF, static/dynamic overlays)
- sources/        — raw source videos to be used for remixing (mp4, mkv, mov, webm)
- temp/           — temporary working files, cached renders, autosaves (ignored by VCS)
- templates/      — project templates / preset edit chains
- presets/        — export / encoding presets (JSON or simple text)
- autosave/       — autosave project dumps and recovery files
- examples/       — small example assets (optional; put tiny, permissively-licensed files here)
- manifest.json   — optional machine-readable inventory of assets

Guidelines
- Keep short sounds under ~10s for quick overlaying.
- Overlays should match your expected output resolution (or be larger) and use transparency when needed.
- Name files descriptively: "meme_sfx_uwu.wav", "rainbow_overlay_1080p.png", "error_beep_1.mp3".
- Avoid committing large binary assets to the repository. Use an external assets zip or release if you want to share many large files.
- Add your own overlays and sounds to their respective folders. The GUI will show the files present in assets/ when importing.

Privacy / Licensing
- Only include assets you have the right to distribute.
- For sample assets in examples/, include license text in a README inside examples/ stating their provenance (public domain, CC0, or link to author + license).

How to use
- Put source clips into assets/sources/.
- Put PNG/GIF overlays into assets/overlays/ or assets/memes/ (if meme-specific).
- Put short SFX into assets/sounds/ and UI sounds into assets/soundos/.
- Start the GUI (python ytpgen.py). Use "Import All from assets/sources" to add all source clips to the project quickly.

Notes
- temp/, autosave/, and similar runtime folders should be added to .gitignore in your repo root to avoid committing transient data.
```
