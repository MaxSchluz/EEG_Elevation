import sys
sys.path.append("/home/max/Dokumente/python_scripts/freefield_toolbox")
sys.path.append("/home/max/Dokumente/python_scripts/soundtools")
import slab
from freefield import camera, setup
import numpy as np
import random
import time

# Initialize processors and camera
rx8="/home/max/Dokumente/python_scripts/rcx/play_noise.rcx"
setup.set_speaker_config("dome")
setup.initialize_devices(ZBus=False,cam=True)
camera.init(type="web")

probes=[35,33,31,29]#choose speakers as probes
rep = 10#choose amount of repititions per block
adaptor=5#choose adaptor channel
n_blocks_per_run = 12#choose blocks per run -> 4 probes x 10 reps => 1 block=40seconds
n_runs=4#choose amount of runs per experiment



sequence = np.repeat(probes,rep)
random.shuffle(sequence)

for i in sequence:
    setup.set_variable(variable="ch_nr",value=i, proc="RX81")
    setup.trigger()
    if i==0:
        camera.get_headpose(cams="all")
    while setup.get_variable("playback",proc="RX81"):
        time.sleep(0.01)

setup.halt()




probes=[0,35,33,31,29]
dur_adapter = 1.0
dur_stim = 0.1
isi = 0.4
target_frequency = 0.1