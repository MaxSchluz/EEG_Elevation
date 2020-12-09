from mne_addon import preprocessing
import mne
import os
import sys
sys.path.append("/home/max/Dokumente/Projects/mne_addon")
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor")
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor/deprecated")

# Run preprocessing pipeline to create epochs for every subject
# Parameters used for preprocessing:
parameters = {
              "rereference": {"n_resample": 50, "min_channels": 0.25, "min_corr": 0.9, "unbroken_time": 0.6, "n_jobs": 1, "random_state": 72},
              "interpolate": {"n_resample": 50, "min_channels": 0.25, "min_corr": 0.8, "unbroken_time": 0.5, "n_jobs": 1, "random_state": 54},
              "reject": {"n_interpolate": [1, 4, 32], "random_state": 42},
              "filtering":{"lowpass": 40, "highpass": 3, "fir_window": "blackman", "fir_design": "firwin",},
              "epochs": {"tmin": -0.1, "tmax": 1.5, "baseline": None, "event_id": {"t": 2, "mt": 3, "mb": 4, "b": 5}},
              "ica": {"reference": "/home/max/Dokumente/Projects/mne_addon/eye-artifact-reference-ica.fif", "n_components": 0.99, "random_state": 7}
              }

# Loop through subjects raw data and create epochs.
reject_headmotion = True  # Delete post-target trials.
for i in range(4, 34):  #  First three subjects were pilots.
    if i < 10:
        subject = "he0%s" % (i)
    else:
        subject = "he%s" % (i)
    raw = mne.io.read_raw_fif("/home/max/Dokumente/Projects/EEG_Bachelor/data/" + subject + "/raw_data/%s-raw.fif" % (subject), preload=True)
    out_folder = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs" % (subject)
    try:
        os.mkdir(out_folder)
    except OSError:
        print ("Creation of the directory %s failed" % out_folder)
    else:
        print ("Successfully created the directory %s " % out_folder)
    epochs, ica = preprocessing.run_pipeline(raw, parameters, out_folder, subject=subject, n_blocks=6, reject_headmotion=True)
    if reject_headmotion:
        fname_epochs = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs/epochs_rejected_headmotion.fif" % (subject)
        fname_ica = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs/ica_rejected_headmotion.fif" % (subject)
    else:
        fname_epochs = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs/epochs.fif" % (subject)
        fname_ica = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs/ica.fif" % (subject)
    epochs.save(fname_epochs)
    ica.save(fname_ica)
    del raw, epochs, ica


# Take epochs from every subject and convert them into evoked responses.
baseline = None
for i in range(4, 34):
    if i < 10:
        subject = "he0%s" % (i)
    else:
        subject = "he%s" % (i)
    if reject_headmotion:
        epochs_fname = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs/epochs_rejected_headmotion.fif" % (subject)
    else:
        epochs_fname = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/epochs/epochs.fif" % (subject)
    epochs = mne.read_epochs(epochs_fname, preload=True)
    if baseline:
        epochs.apply_baseline(baseline)
    probes = ["b", "mb", "mt", "t"]
    evokeds = [epochs[cond].average() for cond in probes]
    if baseline:
        evoked_fname = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s_baseline_%s-ave.fif" % (subject, subject, baseline)
    else:
        evoked_fname = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s-ave.fif" % (subject, subject)
    out_folder = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds" % (subject)
    try:
        os.mkdir(out_folder)
    except OSError:
        print ("Creation of the directory %s failed" % out_folder)
    else:
        print ("Successfully created the directory %s " % out_folder)
    mne.write_evokeds(evoked_fname, evokeds)
    del epochs, evokeds
