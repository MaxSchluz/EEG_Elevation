import numpy as np
import slab
from freefield import camera, setup
import time
import sys
import json
from copy import deepcopy
sys.path.append("D:/Projects/freefield_toolbox")
sys.path.append("D:/Projects/soundtools")

# load config file with all the experiment variables:
with open('D:/Projects/EEG_Elevation_Max/exp_config.json') as f:
    cfg = json.load(f)

_isinit = False


def init():
    global _isinit
    setup.set_speaker_config("dome")
    setup.initialize_devices(mode="localization_test_headphones")
    _isinit = True


def run_block(sounds, positions):

    # set the processor variables:
    setup.set_variable(variable="playbuflen", value=int(
        cfg["dur_adapter"]*cfg["fs"]), proc="RP2")


def prepare_stimuli(speaker):
    if setup._mode != "binaural_recording":
        setup.initialize_devices(mode="binaural_recording")
    speaker_nr = setup.speaker_from_direction(speaker[0], speaker[1])[0]
    probe = []  # only the probe
    adapter_probe = []  # adapter and probe crossfaded
    for _ in range(cfg["n_recs"]):
        sound = slab.Sound.pinknoise(duration=cfg["dur_target"], samplerate=cfg["fs"])
        adapter = slab.Sound.pinknoise(duration=cfg["dur_adapter"], samplerate=cfg["fs"], nchannels=2)
        sound.level = cfg["dB_level"]
        rec = setup.play_and_record(
            speaker_nr, sound, compensate_delay=True, apply_calibration=False)
        rec.level += sound.level-rec.level.max()  # compensate attenuation, keep iid
        probe.append(rec)
        adapter.level = rec.level
        adapter_probe.append(slab.Sound.crossfade(adapter, rec, overlap=cfg["dur_ramp"]))
    adapter_probe = slab.psychoacoustics.Precomputed(adapter_probe)
    probe = slab.psychoacoustics.Precomputed(probe)
    return probe, adapter_probe
