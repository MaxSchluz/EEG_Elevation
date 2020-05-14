import numpy as np
import random
import json
import os
import sys
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor/soundtools/slab")


def make_blocks(probes, rep, n_blocks_per_run, n_runs, expdir, subject):

    directory_path = expdir+subject
    try:
        os.makedirs(directory_path)
    except OSError:
        print("Creation of the directory %s failed" % directory_path)
    else:
        print("Successfully created the directory %s" % directory_path)
    for c in range(n_runs):
        seq = []
        for i in range(n_blocks_per_run):
            seq.extend(sequence(probes, rep))
        target_seq = add_targets(seq,target_freq=0.1,space=3)
        file_path = expdir+subject+"/"+subject+"_run_"+str(c)+".seq" # abspeichern als json-file
        np.savetxt(file_path, np.asanyarray(target_seq,dtype=int),fmt='%i', delimiter=",")


def sequence(probes, rep):

    seq = []  # Dictionary für erstellte Sequenz
    sequence = np.repeat(probes,rep)
    random.shuffle(sequence)
    seq.extend(sequence)

    return seq


def add_targets(seq,target_freq, space):

    n_targets = int((len(seq)*target_freq))#10% targets
    ok = 0
    while ok == 0:
        choice = np.sort(np.random.randint(5, len(seq), n_targets))
        if min(np.diff(choice))>=space:
            ok=1
        else:
           print("shuffeling again...")

    target_seq = np.insert(seq,choice,0)

    return target_seq


if __name__ == "__main__":
	probes=[14,16,2,4]#choose speakers as probes
	rep = 8#choose amount of repititions per block
	n_blocks_per_run = 9#choose blocks per run -> 4 probes x 1,5s = 6s x 8 reps = 48s x 9blocks= 7.2 min
	n_runs=4#choose amount of runs per experiment
	subject ="Max" # name der versuchsperson
	expdir ="/home/max/Dokumente/Projects/EEG_Bachelor/eeg_data/test/" #speicherort

	make_blocks(probes, rep, n_blocks_per_run, n_runs, expdir, subject)



