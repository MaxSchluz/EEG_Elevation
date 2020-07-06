import numpy as np
import random
import json
import os
import sys
import slab
from freefield import setup


def make_blocks(speakers, target_freq, n_reps, n_runs, expdir, subject):

    file_path = expdir+subject+"/" # abspeichern als json-file
    try:
        os.makedirs(file_path)
    except OSError:
        print("Creation of the directory %s failed" % file_path)
    else:
        print("Successfully created the directory %s" % file_path)
    for c in range(n_runs):
        seq = sequence(speakers, target_freq, n_reps)
        file_name= file_path+subject+"_run_"+str(c)+".seq"
        slab.LoadSaveJson.save_json(seq,file_name)

def sequence(speakers, target_freq, n_reps,space=5):

    speaker_list= setup.speakers_from_list(speakers)       
    seq=slab.Trialsequence(speaker_list,n_reps=n_reps,kind="non_repeating")
    n_targets = int((seq.n_trials)*target_freq) #5% targets
    ok = 0
    while ok == 0:
        choice = np.sort(np.random.randint(5, len(seq.trials), n_targets))
        if min(np.diff(choice))>=space:
            ok=1
        else:
           print("shuffeling again...")
    for idx in choice:
        index=choice.tolist().index(idx)
        seq.trials.pop(choice[index])
        seq.trials.insert(choice[index],4)
    seq=slab.Trialsequence(conditions=speaker_list, trials=seq.trials, kind="non_repeating")

    return seq

