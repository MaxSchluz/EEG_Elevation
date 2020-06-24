import slab
from freefield import camera, setup
import os
import time
import sys
import numpy as np
import pandas as pd
sys.path.append("C:/Projects/freefield_toolbox")
sys.path.append("C:/Projects/soundtools")


# TODO: change responses to pandas dataframe, see setup.localization_task

# Set variables for kind plus length of adapter, target and buffer
n_runs = 4  # how many runs per participant
fs = 48828.125  # sample frequency
n_adapter = 1.0 * fs
n_target = 0.1 * fs
n_buf = 1.0 * fs
stim_target = slab.Sound.whitenoise()
stim_adapter = slab.Sound.whitenoise()
stim_adapter.level = 70  # not needed after speaker calibration
response = pd.DataFrame(columns=["ele_target", "azi_target", "ele_response", "azi_response"])


# Initialize processors and camera
rx8 = "C:/Projects/EEG_Elevation_Max/rcx/play_noise_buf.rcx"
rp2 = "C:/Projects/EEG_Elevation_Max/rcx/button.rcx"
setup.set_speaker_config("dome")
setup.initialize_devices(ZBus=True, cam=True, RX8_file=rx8, RP2_file=rp2)
camera.init()


def make_dir(expdir):
    try:
        os.makedirs(expdir)
    except OSError:
        print("Creation of the directory %s failed" % expdir)
    else:
        print("Successfully created the directory %s" % expdir)


# run experiment
def run_experiment(subject):  # function for executing whole experiment

    for i in range(n_runs):  # execute run_block for amount of n_runs
        input("press any key to continue to next block")
        run_block(i, subject, fs=fs, dur_stim=n_target,
                  dur_adapter=n_adapter, dur_buf=n_buf)
    setup.halt()


def run_block(block, subject, fs, dur_stim, dur_adapter, dur_buf):

    seq = np.loadtxt("C:/Projects/EEG_Elevation_Max/data/"+subject+"/sequences/"+"sequences_"+subject+"_run_"+str(block)
                     + ".seq")
    # seq = [2, 0, 4, 0, 14, 0]

    # set variables for RPvdsEx circuits that remain the same during the experiment.
    setup.set_variable(variable="n_target", value=n_target, proc="RX8s")
    setup.set_variable(variable="n_adapter", value=n_adapter, proc="RX8s")
    setup.set_variable(variable="playbuflen", value=n_buf, proc="RX8s")
    setup.set_variable(variable="data_target", value=stim_target.data, proc="RX8s")
    setup.set_variable(variable="data_adapter", value=stim_adapter.data, proc="RX8s")
    # time.sleep(10)
    for i, ch in enumerate(seq):  # loop through sequence
        if ch == 0:
            target_i = i-1
            target_ch = seq[target_i]
            if target_ch == 2:
                azi, ele = setup._speaker_table[22][3], setup._speaker_table[22][4]
            elif target_ch == 4:
                azi, ele = setup._speaker_table[20][3], setup._speaker_table[20][4]
            elif target_ch == 14:
                azi, ele = setup._speaker_table[26][3], setup._speaker_table[26][4]
            elif target_ch == 16:
                azi, ele = setup._speaker_table[24][3], setup._speaker_table[24][4]
            trial = {"azi_target": azi, "ele_target": ele}
            setup.set_variable(variable="chan_l", value=10, proc="RX8s")
            setup.set_variable(variable="chan_r", value=9, proc="RX8s")
            setup.trigger(trig=1, proc="RX81")
            setup.wait_to_finish_playing()
            while not setup.get_variable(variable="response", proc="RP2"):
                time.sleep(0.01)
                ele, azi = camera.get_headpose(convert=True, average=True)
                trial["azi_response"], trial["ele_response"] = azi, ele
                response.append(trial, ignore_index=True)
            while not setup.get_variable(variable="response", proc="RP2"):
                time.sleep(0.01)
        else:
            setup.set_variable(variable="chan_l", value=30, proc="RX8s")
            setup.set_variable(variable="chan_r", value=30, proc="RX8s")
            setup.set_variable(variable="ch_nr", value=ch, proc="RX8s")
            setup.trigger()
            setup.wait_to_finish_playing()
        time.sleep(0.4)  # ISI

    response_path = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"headpose_response/" + "headpose_response_run_"+str(block)+".pkl"
    response.to_pickle(response_path)
    print("Saved responses as \n %s!" % response_path)

    return response


# TEST: example run block

subject = "Paul"  # name der testperson
expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
    "/"+"headpose_responses/"  # speicherort
make_dir(expdir)
responses = run_block(block=0, subject=subject, fs=fs, dur_stim=n_target,
                      dur_adapter=n_adapter, dur_buf=n_buf)


if __name__ == "__main__":

    subject = "test"  # name der testperson
    expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"headpose_responses/"
    make_dir(expdir)
    run_experiment(subject)
