#!/usr/bin/env python3
"""
Entry point for YTPDeluxe / YTPGen.
Creates assets folders and launches the GUI.
"""
import os
import sys
from pathlib import Path

# Ensure script directory is working dir
HERE = Path(__file__).resolve().parent
ASSETS_DIR = HERE / "assets"
TEMP_DIR = HERE / "temp"

REQUIRED_DIRS = [
    ASSETS_DIR / "sounds",
    ASSETS_DIR / "overlays",
    ASSETS_DIR / "errors",
    ASSETS_DIR / "advert",
    ASSETS_DIR / "memes",
    ASSETS_DIR / "sources",
    TEMP_DIR,
]

def ensure_dirs():
    for d in REQUIRED_DIRS:
        d.mkdir(parents=True, exist_ok=True)

def main():
    ensure_dirs()
    # Lazy import GUI so we can create dirs first
    try:
        from gui import YTPGui
    except Exception as e:
        print("Failed to import GUI modules:", e)
        sys.exit(1)

    app = YTPGui(root_dir=str(HERE))
    app.run()

if __name__ == "__main__":
    main()