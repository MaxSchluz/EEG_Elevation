import numpy as np
import random
import json
import os
import sys
import slab
from freefield import setup


def make_blocks(speakers, target_freq, n_runs, expdir, subject):

    file_path = expdir+subject+"/" # abspeichern als json-file
    try:
        os.makedirs(file_path)
    except OSError:
        print("Creation of the directory %s failed" % file_path)
    else:
        print("Successfully created the directory %s" % file_path)
    for c in range(n_runs):
        seq = sequence(speakers, target_freq)
        file_name= file_path+subject+"_run_"+str(c)+".seq"
        slab.LoadSaveJson.save_json(seq,file_name)

def sequence(speakers, target_freq, space=5):

    speaker_list= setup.speakers_from_list(speakers)       
    seq=slab.Trialsequence(speaker_list,n_reps=88,kind="non_repeating")
    n_targets = int((seq.n_trials)*target_freq) #5% targets
    ok = 0
    while ok == 0:
        choice = np.sort(np.random.randint(5, len(seq.trials), n_targets))
        if min(np.diff(choice))>=space:
            ok=1
        else:
           print("shuffeling again...")
    target_seq = np.insert(seq.trials,choice, 4)
    target_seq = target_seq.tolist()      
    seq=slab.Trialsequence(conditions=speaker_list, n_reps=88, trials=target_seq, kind="non_repeating")

    return seq

