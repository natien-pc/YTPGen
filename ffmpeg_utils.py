"""
Utility helpers to run ffmpeg and build commands.

This module provides:
- check_ffmpeg(): finds ffmpeg on PATH or at an explicit location
- run_ffmpeg(): run ffmpeg command and stream output
- build_preview(): helper to cut a short preview segment
"""

import subprocess
import shutil
import os
from pathlib import Path
import shlex

FFMPEG_BIN = shutil.which("ffmpeg") or "ffmpeg"  # Users may need to set PATH

def check_ffmpeg():
    """Return full path to ffmpeg binary or None."""
    if shutil.which("ffmpeg"):
        return shutil.which("ffmpeg")
    # fallback: if user left a local 'ffmpeg.exe' in repo root:
    local = Path(__file__).resolve().parent / "ffmpeg.exe"
    if local.exists():
        return str(local)
    return None

def run_ffmpeg(cmd_args, capture_output=False):
    """
    Run ffmpeg with a list of arguments (not a shell string).
    Streams stdout/stderr to console. Returns exit code.
    """
    ff = check_ffmpeg()
    if not ff:
        raise EnvironmentError("ffmpeg not found. Please install FFmpeg and add to PATH.")
    full_cmd = [ff] + cmd_args
    # For debugging:
    print("Running ffmpeg:", " ".join(shlex.quote(a) for a in full_cmd))
    if capture_output:
        proc = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, proc.stdout, proc.stderr
    else:
        proc = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        return proc.returncode, out, err

def build_preview(input_path, output_path, duration=6, start_time=None):
    """
    Create a short preview cut of `duration` seconds from input_path.
    If start_time is None, ffmpeg will pick start at 0s.
    """
    args = ["-y", "-hide_banner", "-loglevel", "warning"]
    if start_time is not None:
        args += ["-ss", str(start_time)]
    args += ["-i", str(input_path), "-t", str(duration), "-c", "copy", str(output_path)]
    return run_ffmpeg(args)