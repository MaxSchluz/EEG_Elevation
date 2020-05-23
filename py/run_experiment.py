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
    rx8="C:/Projects/max_elevation_eeg/bachelor_thesis_eeg/rcx/play_noise_test.rcx"
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
    #seq=[2,4,0,14,0,16]
    n_adapter= int(dur_adapter * fs)
    n_target=int(dur_stim * fs)
    stim = slab.Sound.clicktrain()
	response=[]

    #set variables for RPvdsEx circuits that don't change
    setup.set_variable(variable="n_target", value=n_target, proc="RX8s")
    setup.set_variable(variable="n_adapter", value=n_adapter, proc="RX8s")
    setup.set_variable(variable="data", value=stim.data, proc="RX8s")
    setup.set_variable(variable="playbuflen", value=len(stim), proc="RX8s")

    #time.sleep(10)
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
    		ele,azi = camera.get_headpose()
    		response.append([ch, ele, azi])
        else:
            setup.set_variable(variable="chan", value=25, proc="RX8s")
            setup.set_variable(variable="ch_nr", value=ch, proc="RX8s")
            setup.trigger()
            setup.wait_to_finish_playing()
        time.sleep(0.4)#ISI

    return response
    file_path= cfg["expdir"] + subject+"/"+subject+"_response_" + ".txt"
    np.savetxt(path, np.asanyarray(response, dtype=int), fmt='%i', delimiter=",")


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


#maybe needed for evalation of headpose?
def target_sequence(seq):
ch_target=[]#empty list for target channels
zeros=np.where(seq==0)
index_zeros=zeros[0].tolist()#search indeces of zeros
for s in range(len(index_zeros)):#loop through length of index_zeros
  index_target=index_zeros[s]-1#for every element, pick out element before target
  ch_target.append(seq[index_target])#append target indeces to ch_target list
return ch_target
