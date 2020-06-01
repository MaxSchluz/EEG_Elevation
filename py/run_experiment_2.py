import sys
sys.path.append("C:/Projects/freefield_toolbox")
sys.path.append("C:/Projects/soundtools")
import slab
from freefield import camera, setup
import numpy as np
import random
import time
import json

def init(): # Initialize processors and camera
    rx8="C:/Projects/max_elevation_eeg/bachelor_thesis_eeg/rcx/play_noise_binaural.rcx"
    rp2="C:/Projects/max_elevation_eeg/bachelor_thesis_eeg/rcx/button.rcx"
    setup.set_speaker_config("dome")
    setup.initialize_devices(ZBus=True, cam=True, RX8_file=rx8, RP2_file=rp2)
    camera.init()

# run experiment
def run_experiment(subject, path_cfg): #funktion für das ganze experiment

    with open (path_cfg, "r") as config_file: #konfigfile laden
        cfg = json.load(config_file)

    for i in range(cfg["n_runs"]): # für jeden block funktion run_block ausführen
        input("press any key to continue to next block") #input, um nächsten block zu starten
        run_block(i, subject, fs=cfg["fs"], dur_stim=cfg["dur_stim"], dur_adapter=cfg["dur_adap"], expdir=cfg["expdir"])    
    setup.halt()
    camera.deinit()    

def run_block(block, subject, fs, dur_stim, dur_adapter, expdir):
    seq = np.loadtxt(expdir+subject+"/"+subject+"_run_"+str(block)+".seq")

    n_adapter= int(dur_adapter * fs)
    n_target=int(dur_stim * fs)
    stim = slab.Sound.clicktrain()
    bi_rec_2=slab.Sound.read("binaural_recording_"+subject+"_"+str(2)+".wav")
    bi_rec_4=slab.Sound.read("binaural_recording_"+subject+"_"+str(4)+".wav")
    bi_rec_14=slab.Sound.read("binaural_recording_"+subject+"_"+str(14)+".wav")
    bi_rec_16=slab.Sound.read("binaural_recording_"+subject+"_"+str(16)+".wav")

	responses={}

    #set variables for RPvdsEx circuits that don't change
    setup.set_variable(variable="n_target", value=n_target, proc="RX8s")
    setup.set_variable(variable="n_adapter", value=n_adapter, proc="RX8s")
    setup.set_variable(variable="data", value=stim.data, proc="RX8s")
    setup.set_variable(variable="playbuflen", value=len(stim), proc="RX8s")

    for i, ch in enumerate(seq):#loop through sequence
        if ch==0:
    		target_index=i-1
    		target_ch=seq[target_index]
    		setup.set_variable(variable="chan", value=target_ch, proc="RX8s")
            setup.trigger(trig=1, proc="RX81")
            setup.wait_to_finish_playing()
            time.sleep(0.99951)
    		while not setup.get_variable(variable="response", proc="RP2"):
                time.sleep(0.01)
    		pose = camera.get_headpose()
    		responses.append({"target_index":target_i, "target_chchannel":target_ch, "elevation":ele, "azimuth":azi})
        else:
            setup.set_variable(variable="chan", value=25, proc="RX8s")
            setup.set_variable(variable="ch_nr", value=ch, proc="RX8s")
            if ch==2:
                setup.set_variable(variable="data_target", value=bi_rec_2.data, proc="RX8s")
                setup.set_variable(variable="data_adapter", value=bi_rec_2.data, proc="RX8s")
            elif ch==4:
                setup.set_variable(variable="data_target", value=bi_rec_4.data, proc="RX8s")
                setup.set_variable(variable="data_adapter", value=bi_rec_4.data, proc="RX8s")
            elif ch==14:
                setup.set_variable(variable="data_target", value=bi_rec_14.data, proc="RX8s")
                setup.set_variable(variable="data_adapter", value=bi_rec_14.data, proc="RX8s")
            elif ch==16:
                setup.set_variable(variable="data_target", value=bi_rec_16.data, proc="RX8s")
                setup.set_variable(variable="data_adapter", value=bi_rec_16.data, proc="RX8s")
            setup.trigger()
            setup.wait_to_finish_playing()
        time.sleep(0.4)#ISI

    return responses

    path= cfg["expdir"] + subject+"/"+subject+"_responses_" +str(block)+ ".txt"
    np.savetxt(path, np.asanyarray(responses, dtype=int), fmt='%i', delimiter=",")


#TEST: example run block
path_cfg = "C:/Projects/max_elevation_eeg/bachelor_thesis_eeg/cfg/test_experiment.cfg" # pfad des konfigurationsfiles
with open (path_cfg, "r") as config_file: #load config file
    cfg = json.load(config_file)
subject = "test" #name der testperson
run_block(block=0, subject=subject, fs=cfg["fs"], dur_stim=cfg["dur_stim"], dur_adapter=cfg["dur_adap"], expdir=cfg["expdir"])


if __name__ == "__main__":

    subject = "test" #name der testperson
    path_cfg = "C:/Projects/max_elevation_eeg/bachelor_thesis_eeg/cfg/test_experiment.cfg" # pfad des konfigurationsfiles
    init()
	run_experiment(subject,path_cfg)






