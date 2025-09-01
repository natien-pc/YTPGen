"""
Effect builders: each effect returns pieces of FFmpeg filtergraph (video and/or audio).
Effects are simple functions that accept parameters (strength, seed, etc.)
and return dict with keys: 'vfilters' (list), 'afilters' (list), 'extra_inputs' (list).
"""

import random
from typing import Dict, List

def _seed_random(seed):
    if seed is not None:
        random.seed(seed)

def effect_invert(params) -> Dict:
    # Invert colors via lutrgb or negate
    return {"vfilters": ["lutrgb=r=negval:g=negval:b=negval"], "afilters": [], "extra_inputs": []}

def effect_flip(params) -> Dict:
    # Random flip direction: horiz, vert, both
    dir = params.get("direction") or random.choice(["h", "v", "hv"])
    if dir == "h":
        vf = "hflip"
    elif dir == "v":
        vf = "vflip"
    else:
        vf = "vflip,hflip"
    return {"vfilters": [vf], "afilters": [], "extra_inputs": []}

def effect_mirror(params) -> Dict:
    # Mirror horizontally with split and overlay
    # Use hflip + blend; simpler: use split and overlay to mirror right half over left
    vf = "split [a][b]; [b] hflip [bf]; [a][bf] overlay=W/2:0"
    # Note: overlay expression may vary depending on input - simple approximation
    return {"vfilters": [vf], "afilters": [], "extra_inputs": []}

def effect_reverse(params) -> Dict:
    # Reverse both video and audio
    # We will tell caller to add -vf reverse -af areverse (ffmpeg can support)
    return {"vfilters": ["reverse"], "afilters": ["areverse"], "extra_inputs": []}

def effect_stutter_loop(params) -> Dict:
    # Duplicate the clip N times (2-4)
    times = int(params.get("times") or random.randint(2, 4))
    # For video: concat filter with n copies — caller must use -filter_complex concat
    # We'll return a marker instructing higher-level builder to use concat duplication
    return {"vfilters": [], "afilters": [], "extra_inputs": [], "stutter_times": times}

def effect_speed(params) -> Dict:
    # speed factor affecting video and audio
    factor = float(params.get("factor") or random.choice([0.5, 0.75, 1.25, 1.5, 2.0]))
    # Video: setpts=PTS/<factor>
    # Audio: atempo supports 0.5-2.0; for >2.0 chain multiple atempo filters
    v = f"setpts={1.0/ factor}*PTS"
    # build atempo chain:
    f = factor
    atempo_chain = []
    # atempo supports 0.5 to 2.0 inclusive; break factor into multiplicative pieces
    if f <= 0:
        f = 1.0
    target = f
    pieces = []
    # for slowdown (factor <1), use atempo between 0.5 and 2
    if target < 0.5:
        # approximate via asetrate + atempo chain later (scaffold)
        pieces = [str(max(0.5, target))]
    else:
        while target > 2.0:
            pieces.append("2.0")
            target /= 2.0
        pieces.append(str(target))
    atempo = ",".join(f"atempo={p}" for p in pieces)
    return {"vfilters": [v], "afilters": [atempo], "extra_inputs": [], "speed_factor": factor}

def effect_chorus(params) -> Dict:
    # Approximate chorus with aecho (this is not perfect but fun)
    # aecho=in_gain:out_gain:delays:decays
    delays = params.get("delays") or "0.8|0.9"
    decays = params.get("decays") or "0.5|0.3"
    af = f"aecho=0.8:0.9:{delays}:{decays}"
    return {"vfilters": [], "afilters": [af], "extra_inputs": []}

def effect_vibrato(params) -> Dict:
    # approximate vibrato by changing sample rate then tempo back (asetrate + atempo)
    depth = float(params.get("depth") or 1.02)  # 1.02 -> slight pitch shift
    af = f"asetrate=44100*{depth},atempo=1/{depth}"
    return {"vfilters": [], "afilters": [af], "extra_inputs": []}

def effect_earrape(params) -> Dict:
    # extreme gain boost
    gain = float(params.get("gain") or 20.0)
    # Use volume filter (dB or linear)
    af = f"volume={gain}"
    return {"vfilters": [], "afilters": [af], "extra_inputs": []}

def effect_audio_crust(params) -> Dict:
    # Slight gain and bitcrush-like effect using acompressor and equalizer approximations
    gain = params.get("gain") or 1.4
    af = f"volume={gain},acompressor"
    return {"vfilters": [], "afilters": [af], "extra_inputs": []}

def effect_rainbow_overlay(params) -> Dict:
    # This effect expects an overlay PNG/GIF in assets/overlays and will overlay it.
    overlay = params.get("overlay") or "assets/overlays/rainbow.png"
    # Caller should attach overlay as an extra input and use overlay filter.
    return {"vfilters": [f"[0:v][1:v] overlay=0:0:format=auto"], "afilters": [], "extra_inputs": [overlay]}

# Simple registry
EFFECT_REGISTRY = {
    "Invert": effect_invert,
    "Flip": effect_flip,
    "Mirror": effect_mirror,
    "Reverse": effect_reverse,
    "StutterLoop": effect_stutter_loop,
    "Speed": effect_speed,
    "Chorus": effect_chorus,
    "Vibrato": effect_vibrato,
    "Earrape": effect_earrape,
    "AudioCrust": effect_audio_crust,
    "RainbowOverlay": effect_rainbow_overlay,
}

def build_effect_chain(effect_list, params_list=None, seed=None):
    """
    Build a simple combined vfilters and afilters from a list of effect names.
    effect_list: list of effect names (strings)
    params_list: list of dicts aligned with effect_list, optional
    Returns dict: {vfilters, afilters, extra_inputs, metadata}
    """
    _seed_random(seed)
    vfilters = []
    afilters = []
    extra_inputs = []
    metadata = {}
    for i, eff in enumerate(effect_list):
        params = (params_list[i] if params_list and i < len(params_list) else {}) or {}
        fn = EFFECT_REGISTRY.get(eff)
        if not fn:
            continue
        built = fn(params)
        if not built:
            continue
        vfilters += built.get("vfilters", [])
        afilters += built.get("afilters", [])
        for ei in built.get("extra_inputs", []):
            extra_inputs.append(ei)
        # propagate special items
        if "stutter_times" in built:
            metadata["stutter_times"] = built["stutter_times"]
        if "speed_factor" in built:
            metadata["speed_factor"] = built["speed_factor"]
    return {"vfilters": vfilters, "afilters": afilters, "extra_inputs": extra_inputs, "metadata": metadata}