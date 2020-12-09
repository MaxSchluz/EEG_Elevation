import sys
sys.path.append("/home/max/Dokumente/Projects/mne_addon")
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor")
import mne
import numpy as np
from mne_addon import analysis
from mne import read_evokeds
from matplotlib import pyplot as plt
from scipy.stats import zscore, sem
from sklearn.linear_model import LinearRegression
import seaborn as sns

# Take evokeds of every subject and condition and average them.
evokeds = []
for i in range(4, 34):  # Loop through subjects
    if i < 10:
        subject = "he0%s" % (i)
    else:
        subject = "he%s" % (i)
    evoked = read_evokeds("/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s-ave.fif" % (subject, subject))
    evokeds.extend(evoked)
evokeds_average = mne.grand_average(evokeds)

# Get peak amplitude and latency
ch_name = ["TP10"]  # Pick electrode
TP9 = evokeds_average.pick_channels(ch_names=ch_name)
TP9.get_peak(return_amplitude=True, tmin=0.26, tmax=0.4)  # Choose time interval in which you seek for minimum or maximum amplitude.

# Iterate through subjects again, create list of evokeds for each condition
evokeds_b = []
evokeds_mb = []
evokeds_mt = []
evokeds_t = []

for i in range(4, 34):  # Loop through subjects
    if i < 10:
        subject = "he0%s" % (i)
    else:
        subject = "he%s" % (i)
    for probe in ["b", "mb", "mt", "t"]:
        if probe == "b":
            evoked = read_evokeds("/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s-ave.fif" % (subject, subject))[0]
            evokeds_b.append(evoked)
        if probe == "mb":
            evoked = read_evokeds("/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s-ave.fif" % (subject, subject))[1]
            evokeds_mb.append(evoked)
        if probe == "mt":
            evoked = read_evokeds("/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s-ave.fif" % (subject, subject))[2]
            evokeds_mt.append(evoked)
        if probe == "t":
            evoked = read_evokeds("/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/evokeds/%s-ave.fif" % (subject, subject))[3]
            evokeds_t.append(evoked)

# Average evoked responses.
evokeds_average_b = mne.grand_average(evokeds_b)
evokeds_average_mb = mne.grand_average(evokeds_mb)
evokeds_average_mt = mne.grand_average(evokeds_mt)
evokeds_average_t = mne.grand_average(evokeds_t)

# Make butterfly plot with topographical maps at peak gfp values.
times = (0.104, 0.176, 0.295, 0.7, 1.108, 1.169, 1.316)
evokeds_average_b.plot_joint(times=times, title=" ")  # Plot complete trial for one condition (-37.5° in this case).

# Show responses over all electrodes. Watch out for amplitude differences between conditions per electrode.
evokeds = [evokeds_average_b, evokeds_average_mb, evokeds_average_mt, evokeds_average_t]
mne.viz.plot_evoked_topo(evokeds)

# Plot evoked response at given electrode
ch_name = ["Cz "]  # pick electrode
channel = mne.pick_channels(ch_names=evokeds_average.ch_names, include=ch_name)
mne.viz.plot_compare_evokeds(dict(bottom=evokeds_b), picks=ch_name,                         truncate_xaxis=False,
                             colors=["seagreen"], legend=False, title="")

# Create dictionaries of evoked datasets named after their elevation. This is needed for the next plot.
average_adapter = {"-37.5°": evokeds_average_b, "-12.5°": evokeds_average_mb, "+12.5°": evokeds_average_mt, "+37.5°": evokeds_average_t}

# plot response at given electrode
ch_name = ["TP10"]  # I chose both Cz and TP10 for comparison
channel = mne.pick_channels(ch_names=evokeds_average_b.ch_names, include=ch_name)
mne.viz.plot_compare_evokeds(average_adapter, picks=channel, vlines=[1.0], title=" ")
