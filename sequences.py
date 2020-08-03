import os
import slab
from freefield import setup
import numpy as np


def make_blocks(speakers, target_freq, n_reps, n_blocks, expdir, subject):

    file_path = expdir  # abspeichern als json-file
    try:
        os.makedirs(expdir)
    except OSError:
        print("Creation of the directory %s failed" % expdir)
    else:
        print("Successfully created the directory %s" % expdir)
    for c in range(n_blocks):
        seq, trialsequence = sequence(speakers, target_freq, n_reps)
        file_name_seq = file_path+subject+"_seq_"+str(c)+".seq"
        slab.LoadSaveJson_mixin.save_json(seq, file_name_seq)
    file_name_trials = file_path+subject+"_trialsequence"+".seq"
    slab.LoadSaveJson_mixin.save_json(trialsequence, file_name_trials)


def mmn_sequence(n_trials, deviant_freq):

    seq = [0]*n_trials
    n_targets = len(seq)*deviant_freq
    ok = 0
    while ok == 0:
        target_idx = np.sort(np.random.randint(5, len(seq), int(n_targets)))
        if min(np.diff(target_idx)) >= 3:
            ok = 1
        else:
            print("shuffeling again...")
    for element in target_idx:
        index = target_idx.tolist().index(element)
        seq.pop(target_idx[index])
        seq.insert(target_idx[index], 1)

    return slab.Trialsequence(conditions=2, n_reps=1, trials=seq)


def sequence(speakers, target_freq, n_reps):

    speaker_list = setup.speakers_from_list(speakers)
    seq = mmn_sequence(n_trials=len(speakers)*n_reps, deviant_freq=target_freq)
    n_trials = seq.n_trials - seq.n_trials*target_freq
    if n_trials/len(speaker_list) % 1:
        print("Warning! uneven number of trials!")

    trialsequence = slab.Trialsequence(speaker_list, n_reps=n_trials/len(speaker_list))

    return seq, trialsequence
