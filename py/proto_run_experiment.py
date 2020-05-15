import sys
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor/freefield_toolbox")
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor/soundtools")
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor/py")
from slab.sound import Sound
from freefield import camera, setup
import numpy as np
import random
import time
import json

# Initialize processors and camera
rx81="/home/max/Dokumente/Projects/EEG Bachelor/rcx/play_noise.rcx"
rp2="/home/max/Dokumente/Projects/EEG Bachelor/rcx/button.rcx"
rx82="/home/max/Dokumente/Projects/EEG Bachelor/rcx/play_buf.rcx"
setup.set_speaker_config("dome")
setup.initialize_devices(ZBus=False,cam=True, RX81_file=rx81, RX82_file=rx82, RP2_file=rp2)
camera.init()

# run experiment
def run_experiment(subject, path_cfg): #funktion für das ganze experiment

    with open (path_cfg, "r") as config_file: #konfigfile laden
        cfg = json.load(config_file)

    for i in range(cfg["n_runs"]): # für jeden block funktion run_block ausführen
        input("press any key to continue to next block") #input, um nächsten block zu starten
        run_block(i, subject, fs=cfg["fs"], dur_stim=cfg["dur_stim"], dur_adapter=cfg["dur_adap"], expdir=cfg["expdir"])


def run_block(block, subject, fs, dur_stim, dur_adapter, expdir):
    """
    :param block:
    :param fs:
    :param dur_adapter:
    :param expdir:
    :return:
    """

    seq = np.loadtxt(expdir+subject+"/"+subject+"_run_"+str(block)+".seq")
    n_adapter= int(dur_adapter * fs)
    n_target=int(dur_stim * fs)
    stim = slab.Sound.tone(frequency=440)
	response_box=[]


    for i, ch in enumerate(seq):
    	print(i,ch)
    	setup.set_variable(variale="n_adapter", value=n_adapter, proc="RX81")
    	setup.set_variable(variable="ch_nr", value=ch, proc="RX81")
    	setup.set_variable(variable="n_target", value=n_target, proc="RX81")
    	setup.trigger()
    	if ch==0:
			target_index=i-1
			target_ch=seq[target_index]
			setup.set_variable(variable="chan", value=target_ch, proc="RX82")
			setup.set_variable(variable="playbuflen", value=48828, proc="RX82")
			setup.set_variable(variable="data", value=stim.data, proc="RX82")
			setup.trigger()
		    while setup.get_variable(variable="playback", proc="RX82"):
		        time.sleep(0.01)
		    while not setup.get_variable(variable="response", proc="RP2"):
		        time.sleep(0.01)
		    ele,azi = camera.get_headpose()
		    response_box.append([i, ele, azi])

    	time.sleep(0.4)#ISI
        

	setup.halt()
	camera.deinit()

#TEST: implement target channel
for i, ch in enumerate(seq):
	if ch==0:
		target_index=i-1
		target_ch=seq[target_index]
		print(target_ch)






def target_sequence(seq):
	ch_target=[]#empty list for target channels
	zeros=np.where(seq==0)
	index_zeros=zeros[0].tolist()#search indeces of zeros
	for s in range(len(index_zeros)):#loop through length of index_zeros
		index_target=index_zeros[s]-1#for every element, pick out element before target
		ch_target.append(seq[index_target])#append target indeces to ch_target list
	return ch_target
	




if __name__ == "__main__":

    subject = "Max" #name der testperson
    path_cfg = "/home/max/Dokumente/Projects/EEG_Bachelor/test_experiment.cfg" # pfad des konfigurationsfiles
	

	run_experiment(subject, path_cfg)
