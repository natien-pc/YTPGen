"""
Tkinter GUI for YTPDeluxe (YTPGen).
This is a beginner-friendly GUI scaffold that allows:
- Adding source files
- Selecting effects and simple parameters
- Generating a randomized preview
- Rendering a final output

This GUI intentionally keeps complexity low so it's compatible with older Windows.
"""
import threading
import random
import time
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ffmpeg_utils import check_ffmpeg, run_ffmpeg, build_preview
from effects import EFFECT_REGISTRY, build_effect_chain

class YTPGui:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.temp_dir = self.root_dir / "temp"
        self.assets_dir = self.root_dir / "assets"
        self.sources_dir = self.assets_dir / "sources"
        self.root = tk.Tk()
        self.root.title("YTPDeluxe — YTP Generator")
        self._build_ui()
        self.sources = []  # list of file paths
        self.ffmpeg_path = check_ffmpeg()
        if not self.ffmpeg_path:
            messagebox.showwarning("FFmpeg not found", "FFmpeg was not found on PATH. Please install FFmpeg and restart.")
        self.is_processing = False

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.grid(column=0, row=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Sources list
        self.sources_list = tk.Listbox(frm, width=60, height=8)
        self.sources_list.grid(column=0, row=0, columnspan=3, pady=(0,8))
        add_btn = ttk.Button(frm, text="Add Source(s)...", command=self.add_sources)
        add_btn.grid(column=0, row=1, sticky="w")
        remove_btn = ttk.Button(frm, text="Remove Selected", command=self.remove_selected)
        remove_btn.grid(column=1, row=1, sticky="w")
        import_btn = ttk.Button(frm, text="Import All from assets/sources", command=self.import_all_sources)
        import_btn.grid(column=2, row=1, sticky="e")

        # Effects toggles
        effects_frame = ttk.LabelFrame(frm, text="Effects")
        effects_frame.grid(column=0, row=2, columnspan=3, sticky="ew", pady=(8,0))
        self.effect_vars = {}
        col = 0
        row = 0
        for name in sorted(EFFECT_REGISTRY.keys()):
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(effects_frame, text=name, variable=var)
            chk.grid(column=col, row=row, sticky="w", padx=4, pady=2)
            self.effect_vars[name] = var
            col += 1
            if col >= 4:
                col = 0
                row += 1

        # Probability slider
        prob_frame = ttk.Frame(frm)
        prob_frame.grid(column=0, row=3, columnspan=3, sticky="ew", pady=(8,0))
        ttk.Label(prob_frame, text="Randomization seed (optional):").grid(column=0, row=0, sticky="w")
        self.seed_entry = ttk.Entry(prob_frame, width=20)
        self.seed_entry.grid(column=1, row=0, sticky="w", padx=(4,0))
        ttk.Label(prob_frame, text="Global effect probability (%):").grid(column=0, row=1, sticky="w", pady=(6,0))
        self.prob_scale = tk.Scale(prob_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.prob_scale.set(80)
        self.prob_scale.grid(column=1, row=1, sticky="ew", padx=(4,0))

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(column=0, row=4, columnspan=3, pady=(12,0))
        preview_btn = ttk.Button(btn_frame, text="Generate Preview", command=self.on_preview)
        preview_btn.grid(column=0, row=0, padx=6)
        render_btn = ttk.Button(btn_frame, text="Render Final", command=self.on_render)
        render_btn.grid(column=1, row=0, padx=6)
        open_temp_btn = ttk.Button(btn_frame, text="Open temp folder", command=self.open_temp)
        open_temp_btn.grid(column=2, row=0, padx=6)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(frm, textvariable=self.status_var, relief=tk.SUNKEN)
        status.grid(column=0, row=5, columnspan=3, sticky="ew", pady=(8,0))

    def add_sources(self):
        paths = filedialog.askopenfilenames(title="Select source videos",
                                            filetypes=[("Video files", "*.mp4 *.mov *.mkv *.webm *.avi"), ("All files", "*.*")])
        for p in paths:
            if p not in self.sources:
                self.sources.append(p)
                self.sources_list.insert(tk.END, p)

    def remove_selected(self):
        sel = list(self.sources_list.curselection())
        sel.reverse()
        for i in sel:
            self.sources_list.delete(i)
            del self.sources[i]

    def import_all_sources(self):
        # Add everything in assets/sources
        files = list(Path(self.sources_dir).glob("*.*"))
        for f in files:
            fstr = str(f)
            if fstr not in self.sources:
                self.sources.append(fstr)
                self.sources_list.insert(tk.END, fstr)

    def open_temp(self):
        p = str(self.temp_dir)
        if os.name == "nt":
            os.startfile(p)
        else:
            try:
                import subprocess
                subprocess.Popen(["xdg-open", p])
            except Exception:
                messagebox.showinfo("Open", f"Temp folder: {p}")

    def run(self):
        self.root.mainloop()

    def _choose_effects_randomized(self):
        # Choose active effects based on toggles and global probability
        chosen = []
        seeds = []
        p = self.prob_scale.get() / 100.0
        seed_val = self.seed_entry.get().strip()
        seed = int(seed_val) if seed_val.isdigit() else None
        for name, var in self.effect_vars.items():
            if not var.get():
                continue
            if random.random() <= p:
                chosen.append(name)
                seeds.append({"seed": seed})
        return chosen, seeds

    def on_preview(self):
        if self.is_processing:
            messagebox.showinfo("Busy", "Already processing. Please wait.")
            return
        if not self.sources:
            messagebox.showwarning("No sources", "Please add at least one source file.")
            return
        src = random.choice(self.sources)
        chosen, params = self._choose_effects_randomized()
        self.status_var.set("Building preview...")
        t = threading.Thread(target=self._do_preview, args=(src, chosen, params))
        t.daemon = True
        t.start()

    def _do_preview(self, src, chosen, params):
        self.is_processing = True
        try:
            seed = int(self.seed_entry.get()) if self.seed_entry.get().isdigit() else None
            chain = build_effect_chain(chosen, params_list=None, seed=seed)
            # Make a short preview cut
            preview_cut = self.temp_dir / "preview_cut.mp4"
            preview_out = self.temp_dir / "preview_out.mp4"
            preview_cut_str = str(preview_cut)
            preview_out_str = str(preview_out)
            build_preview(src, preview_cut_str, duration=6)
            # Build ffmpeg command for filters
            cmd = ["-y", "-hide_banner", "-loglevel", "warning", "-i", preview_cut_str]
            extra_inputs = chain.get("extra_inputs", [])
            for ei in extra_inputs:
                cmd += ["-i", ei]
            vf = chain.get("vfilters", [])
            af = chain.get("afilters", [])
            filter_complex = []
            if vf:
                # Join simple vfilters with commas
                filter_complex.append(",".join(vf))
            if af:
                # join audio filters
                # audio filters apply to stream 0:a, so we can set -af "..."
                pass
            if filter_complex:
                cmd += ["-vf", ",".join(vf)]
            if af:
                cmd += ["-af", ",".join(af)]
            cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-c:a", "aac", "-b:a", "128k", preview_out_str]
            run_ffmpeg(cmd)
            self.status_var.set(f"Preview ready: {preview_out_str}")
            try:
                if os.name == "nt":
                    os.startfile(preview_out_str)
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", preview_out_str])
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Preview Error", str(e))
            self.status_var.set("Error during preview")
        finally:
            self.is_processing = False

    def on_render(self):
        if self.is_processing:
            messagebox.showinfo("Busy", "Already processing. Please wait.")
            return
        if not self.sources:
            messagebox.showwarning("No sources", "Please add at least one source file.")
            return
        # For render, build a chain across multiple files (random clip shuffle / sentence mixing)
        # We'll select up to 4 random sources and build simple concatenation + effects
        chosen_sources = random.sample(self.sources, min(4, len(self.sources)))
        chosen_effects, _ = self._choose_effects_randomized()
        self.status_var.set("Starting render...")
        t = threading.Thread(target=self._do_render, args=(chosen_sources, chosen_effects))
        t.daemon = True
        t.start()

    def _do_render(self, sources, effects):
        self.is_processing = True
        try:
            seed = int(self.seed_entry.get()) if self.seed_entry.get().isdigit() else None
            # Create intermediate cut segments: extract 4s from each start at random offsets
            segment_files = []
            for i, s in enumerate(sources):
                out = self.temp_dir / f"seg_{i}.mp4"
                # pick a random start between 0 and 10s for short files
                start = random.uniform(0, 6)
                build_preview(s, str(out), duration=4, start_time=start)
                segment_files.append(str(out))
            # Concatenate segments using ffmpeg concat demuxer
            list_file = self.temp_dir / "concat_list.txt"
            with open(list_file, "w", encoding="utf-8") as f:
                for p in segment_files:
                    f.write(f"file '{p.replace(\"'\", \"'\\\\''\")}'\n")
            concat_out = self.temp_dir / "concat.mp4"
            cmd_concat = ["-y", "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(concat_out)]
            run_ffmpeg(cmd_concat)
            # Now apply effects to concat_out
            chain = build_effect_chain(effects, params_list=None, seed=seed)
            final_out = self.root_dir / f"ytp_render_{int(time.time())}.mp4"
            cmd = ["-y", "-hide_banner", "-loglevel", "warning", "-i", str(concat_out)]
            for ei in chain.get("extra_inputs", []):
                cmd += ["-i", ei]
            vf = chain.get("vfilters", [])
            af = chain.get("afilters", [])
            if vf:
                cmd += ["-vf", ",".join(vf)]
            if af:
                cmd += ["-af", ",".join(af)]
            cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "192k", str(final_out)]
            run_ffmpeg(cmd)
            self.status_var.set(f"Render complete: {final_out}")
            try:
                if os.name == "nt":
                    os.startfile(str(final_out))
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", str(final_out)])
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Render Error", str(e))
            self.status_var.set("Error during render")
        finally:
            self.is_processing = False