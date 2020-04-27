import sys
sys.path.append("C:/Users/maxsc_000/Desktop/python_scripts/soundtools/")
sys.path.append("C:/Users/maxsc_000/Desktop/python_scripts/freefield_toolbox/")
import slab
from freefield import camera, setup
import numpy as np
import random
import time

# Initialize
rx8="C:\\Users\\maxsc_000\\Desktop\\python_scripts\\rcx\\play_noise.rcx"
setup.set_speaker_config("dome")
setup.initialize_devices(RX8_file=rx8)

sequence = np.repeat([1,3,15],10)
random.shuffle(sequence)

for i in sequence:
    setup.set_variable(variable="ch_nr",value=i, proc="RX81")
    setup.trigger()
    #if i==0:
        #get headpose
    while setup.get_variable("playback",proc="RX81"):
        time.sleep(0.01)

setup.halt()
