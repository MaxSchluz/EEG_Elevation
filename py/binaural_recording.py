import sys
sys.path.append("/home/max/Dokumente/Projects/freefield_toolbox")
sys.path.append("/home/max/Dokumente/Projects/soundtools")
import time
from freefield import setup, camera
import numpy as np
import slab


def init():
	# Initialize
	setup.set_speaker_config("dome")
	setup.initialize_devices(mode="binaural_recording")
	camera.init()


def record_binaurals(subject,speakers,sig):

	recordings=[]

	for speaker_nr in speakers:
	    bi_rec=setup.play_and_record(speaker_nr,sig,binaural=True)
	    if speaker_nr==20:
	    	speaker_ch=4
	    elif speaker_nr==22:
	    	speaker_ch=2
	    elif speaker_nr==24:
	    	speaker_ch=16
	    elif speaker_nr==26:
	    	speaker_ch=14
	    bi_rec.write("binaural_recording_"+subject+"_"+str(speaker)+".wav")


if __name__ == "__main__":
	subject="test"#define name of participant
	speakers=[20,22,24,26]#define speakers with relevant coordinates
	sig = slab.Sound.whitenoise(duration=1.0, samplerate=48828)


