import sys
sys.path.append("/home/max/Dokumente/python_scripts/mne_addon")
from mne_addon import preprocessing
import mne
import numpy as np
from mne_addon import plotting
from mne_addon import analysis
from mne import read_evokeds
from matplotlib import pyplot as plt
from scipy.stats import zscore


"""
Run preprocessing pipeline to create epochs for every subject
"""

#set parameters
parameters={"filtering": {"highpass":1, "lowpass":40,"fir_window":"hamming"}, "epochs": {"tmin": -0.1, "tmax": 1.0, "baseline": (-0.1, 0), "event_id": {"t-mt": 2, "t-mb": 3, "t-b": 4, "b-t": 5, "b-mt": 6, "b-mb": 7}}, "rereference": {"n_resample": 50, "min_channels": 0.25, "min_corr": 0.8, "unbroken_time": 0.5, "n_jobs": 1}, "ica":{"reference": "/home/max/Dokumente/python_scripts/mne_addon/eye-artifact-reference-ica.fif", "n_components": 0.99}, "interpolate": {"n_resample": 50, "min_channels": 0.25, "min_corr": 0.8, "unbroken_time": 0.5, "n_jobs": 1},"reject":{"n_interpolate": [3, 6, 12], "cv": 50, "n_jobs": 1, "random_state": 42}}
#loop through subjects and create epochs
for i in range(1,4):
	subject="eegl0%s" % (i)
	for eye_fixation in ["down","mid","up"]:
		raw=mne.io.read_raw_fif("/home/max/Dokumente/python_scripts/eeg_data/%s/%s_%s-raw.fif" % (subject,subject,eye_fixation), preload=True)
		out_folder="/home/max/Dokumente/python_scripts/mne_addon/mne_addon/epochs/%s/%s" % (subject, eye_fixation)
		epochs,ica=preprocessing.run_pipeline(raw,parameters,out_folder)
		fname_epochs="/home/max/Dokumente/python_scripts/mne_addon/mne_addon/epochs/%s/%s/epochs.fif" % (subject, eye_fixation)
		fname_ica="/home/max/Dokumente/python_scripts/mne_addon/mne_addon/epochs/%s/%s/ica.fif" % (subject, eye_fixation)
		epochs.save(fname_epochs)
		ica.save(fname_ica)


"""
create evokeds for every subject
save evokeds
"""

for i in range(1,4):
	subject="eegl0%s" % (i)
	for eye_fixation in ["down","mid","up"]:
		epochs_fname = "/home/max/Dokumente/python_scripts/mne_addon/mne_addon/epochs/%s/%s/epochs.fif" % (subject, eye_fixation)
		epochs = mne.read_epochs(epochs_fname, preload=True)
		baseline = (0.5,0.6) #apply baseline for probe response (optional)
		epochs.apply_baseline(baseline) #apply baseline for probe response (optional)
		for adaptor in ["t","b"]:
			if adaptor=="t":
				probes = ["mt","mb","b"]
				for probe in probes:
					evoked_adaptor_top=epochs["%s-%s" % (adaptor, probe)].average()
					evoked_fname="/home/max/Dokumente/python_scripts/mne_addon/mne_addon/evokeds/%s/%s_%s-%s-%s-ave.fif" % (subject, subject, eye_fixation, adaptor, probe)
					evoked_adaptor_top.save(evoked_fname)
			elif adaptor == "b":
				probes = ["mt","mb","t"]
				for probe in probes:
					evoked_adaptor_bot=epochs["%s-%s" % (adaptor, probe)].average()
					evoked_fname="/home/max/Dokumente/python_scripts/mne_addon/mne_addon/evokeds/%s/%s_%s-%s-%s-ave.fif" % (subject, subject, eye_fixation, adaptor, probe)
					evoked_adaptor_bot.save(evoked_fname)
		