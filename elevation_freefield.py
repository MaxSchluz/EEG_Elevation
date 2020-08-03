import numpy as np
import slab
from freefield import camera, setup
import time
import sys
import json
import pandas as pd
sys.path.append("D:/Projects/freefield_toolbox")
sys.path.append("D:/Projects/soundtools")

# load config file with all the experiment variables:
with open('D:/Projects/EEG_Elevation_Max/exp_config.json') as f:
    cfg = json.load(f)

_isinit = False

warning = slab.Sound.vowel(duration=0.4, vowel="oe", samplerate=cfg["fs"])
warning.level -= 15
warning.ramp("both")
warning = warning.data

start = slab.Sound.read("D:/Projects/freefield_toolbox/freefield/localization_test_start.wav")
start.level -= 15
start = start.channel(0)
start = start.data


def init():
    global _isinit
    setup.set_speaker_config("dome")
    setup.initialize_devices(
        ZBus=True, cam=True, RX8_file=cfg["rx8_file"], RP2_file=cfg["rp2_file"])
    # set the processor variables:
    setup.set_variable(variable="n_adapter", value=int(
        cfg["dur_adapter"]*cfg["fs"]), proc="RX8s")
    setup.set_variable(variable="n_target", value=int(
        cfg["dur_target"]*cfg["fs"]), proc="RX8s")
    setup.set_variable(variable="playbuflen", value=int(
        cfg["dur_adapter"]*cfg["fs"]), proc="RX8s")
    setup.set_variable(variable="t_delay",
                       value=(cfg["dur_adapter"]-cfg["dur_ramp"])*1000, proc="RX8s")
    _isinit = True


def run_block(target_seq, trial_seq):
    if not _isinit:
        init()
    response = pd.DataFrame(columns=["ele_target", "azi_target", "ele_response", "azi_response"])

    # play starting sound from headphone loudspeakers
    setup.set_variable(variable="signal_len", value=len(start), proc="RX8s")
    setup.set_variable(variable="signal", value=start, proc="RX8s")
    setup.trigger(trig=2, proc="RX81")
    setup.wait_to_finish_playing()
    while not setup.get_variable(variable="response", proc="RP2"):
        time.sleep(0.01)

    while target_seq.n_remaining > 0:  # go through the target sequence
        target_seq.__next__()
        # if not 1 its a regular trial --> get the next element from the trial sequence
        if target_seq.this_trial != 1:
            # generate the sounds for this trial:
            stim = slab.Sound.pinknoise(duration=int(cfg["dur_target"]*cfg["fs"]))
            stim.ramp(when="both", duration=cfg["dur_ramp"], envelope=None)
            adapter_l, adapter_r = make_adapter(sound=slab.Sound.pinknoise(
                duration=int(cfg["dur_adapter"]*cfg["fs"])))
            trial_seq.__next__()
            speaker, ch, proc, azi_t, ele_t, _, _ = trial_seq.this_trial
            trig_nr = cfg["trig"][str(int(speaker))]
            setup.set_variable(variable="trigcode", value=trig_nr, proc="RX82")
            setup.set_signal_and_speaker(signal=stim, speaker=speaker,
                                         apply_calibration=True)
            setup.set_variable(variable="data_adapter_l", value=adapter_l.data, proc="RX8s")
            setup.set_variable(variable="data_adapter_r", value=adapter_r.data, proc="RX8s")
            setup.trigger()
            setup.wait_to_finish_playing()
            time.sleep(cfg["dur_intertrial"])  # wait until next trial
        # if 1 its a target trial --> play warning sound and get headpose
        elif target_seq.this_trial == 1:
            setup.trigger(trig=1, proc="RX81")
            while not setup.get_variable(variable="response", proc="RP2"):
                time.sleep(0.01)
            ele_r, azi_r = camera.get_headpose(convert=True, average=True)
            trial = {"azi_target": azi_t, "ele_target": ele_t,
                     "azi_response": azi_r, "ele_response": ele_r}
            response = response.append(trial, ignore_index=True)
            head_in_position = 0  # check if the head is in position for next trial
            while head_in_position == 0:
                while not setup.get_variable(variable="response", proc="RP2"):
                    time.sleep(0.01)
                ele, azi = camera.get_headpose(convert=True, average=True)
                if ele is np.nan:
                    ele = 0
                if azi is np.nan:
                    azi = 0
                if (np.abs(ele-cfg["fixation_point"][1]) < cfg["fixation_accuracy"] and
                        np.abs(azi-cfg["fixation_point"][0]) < cfg["fixation_accuracy"]):
                    head_in_position = 1
                else:
                    print(np.abs(ele-cfg["fixation_point"][1]),
                          np.abs(azi-cfg["fixation_point"][0]))
                    setup.set_variable(variable="signal_len", value=len(warning), proc="RX8s")
                    setup.set_variable(variable="signal", value=warning, proc="RX8s")
                    setup.trigger(trig=2, proc="RX81")

    return response


def make_adapter(sound):
    adapter_l, adapter_r = slab.Sound.pinknoise(), slab.Sound.pinknoise()
    adapter_l.ramp(when="both", duration=cfg["dur_ramp"], envelope=None)
    adapter_r.ramp(when="both", duration=cfg["dur_ramp"], envelope=None)
    adapter_l.level *= setup._calibration_lvls[cfg["headphone_left_ch"]]
    adapter_r.level *= setup._calibration_lvls[cfg["headphone_right_ch"]]
    adapter_l.level = adapter_l.level - 6
    adapter_r.level = adapter_r.level - 6
    adapter_r = setup._calibration_freqs.channel([cfg["headphone_right_ch"]]).apply(adapter_r)
    adapter_l = setup._calibration_freqs.channel([cfg["headphone_left_ch"]]).apply(adapter_l)
    return adapter_l, adapter_r


def localization_test_adapter(n_reps, speakers=None, visual=False):

    setup.set_speaker_config("dome")
    setup.initialize_devices(ZBus=True, cam=True, RX8_file=cfg["rx8_file_test"], RP2_file=cfg["rp2_file"])

    setup.set_variable(variable="n_adapter", value=int(
        cfg["dur_adapter"]*cfg["fs"]), proc="RX8s")
    setup.set_variable(variable="n_target", value=int(
        cfg["dur_target"]*cfg["fs"]), proc="RX8s")
    setup.set_variable(variable="playbuflen", value=int(
        cfg["dur_adapter"]*cfg["fs"]), proc="RX8s")
    setup.set_variable(variable="t_delay",
                       value=(cfg["dur_adapter"]-cfg["dur_ramp"])*1000, proc="RX8s")
    if visual is True:
        speakers = setup.all_leds()
    else:
        speakers = setup.speakers_from_list(speakers)
    seq = slab.Trialsequence(speakers, n_reps, kind="non_repeating")
    response = pd.DataFrame(columns=["ele_target", "azi_target", "ele_response", "azi_response"])
    setup.set_variable(variable="signal_len", value=len(start), proc="RX8s")
    setup.set_variable(variable="signal", value=start, proc="RX8s")
    setup.trigger(trig=2, proc="RX81")
    setup.wait_to_finish_playing()
    while not setup.get_variable(variable="response", proc="RP2"):
        time.sleep(0.01)
    while seq.n_remaining > 0:
        speaker, ch, proc_ch, azi, ele, bit, proc_bit = seq.__next__()
        stim = slab.Sound.pinknoise(duration=int(cfg["dur_target"]*cfg["fs"]))
        stim.ramp(when="both", duration=cfg["dur_ramp"], envelope=None)
        adapter_l, adapter_r = make_adapter(sound=slab.Sound.pinknoise(
            duration=int(cfg["dur_adapter"]*cfg["fs"])))
        setup.set_signal_and_speaker(signal=stim, speaker=speaker,
                                     apply_calibration=True)
        setup.set_variable(variable="data_adapter_l", value=adapter_l.data, proc="RX8s")
        setup.set_variable(variable="data_adapter_r", value=adapter_r.data, proc="RX8s")
        if visual is True:
            setup.set_variable(variable="bitmask", value=bit, proc=proc_bit)
        setup.trigger()
        setup.wait_to_finish_playing()
        while not setup.get_variable(variable="response", proc="RP2"):
            time.sleep(0.01)
        ele_r, azi_r = camera.get_headpose(convert=True, average=True)
        if visual is True:
            setup.set_variable(variable="bitmask", value=0, proc=proc_bit)
        trial = {"azi_target": azi, "ele_target": ele,
                 "azi_response": azi_r, "ele_response": ele_r}
        response = response.append(trial, ignore_index=True)
        head_in_position = 0  # check if the head is in position for next trial
        while head_in_position == 0:
            while not setup.get_variable(variable="response", proc="RP2"):
                time.sleep(0.01)
            ele, azi = camera.get_headpose(
                n_images=1, convert=True, average=True)
            if ele is np.nan:
                ele = 0
            if azi is np.nan:
                azi = 0
            if (np.abs(ele-cfg["fixation_point"][1]) < cfg["fixation_accuracy"] and
                    np.abs(azi-cfg["fixation_point"][0]) < cfg["fixation_accuracy"]):
                head_in_position = 1
            else:
                print(np.abs(ele-cfg["fixation_point"][1]),
                      np.abs(azi-cfg["fixation_point"][0]))
                setup.set_variable(variable="signal_len", value=len(warning), proc="RX8s")
                setup.set_variable(variable="signal", value=warning, proc="RX8s")
                setup.trigger(trig=2, proc="RX81")
    return response
