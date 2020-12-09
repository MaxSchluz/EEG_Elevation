import sys
sys.path.append("/home/max/Dokumente/Projects/mne_addon")
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor")
from mne_addon import analysis
import numpy as np
import matplotlib.pyplot as plt
import mne
from sklearn.linear_model import LinearRegression
import seaborn as sns
import pandas as pd
from statsmodels.stats.anova import AnovaRM
from scipy.stats import wilcoxon
from scipy.stats import zscore, sem, ttest_rel
import pickle
pd.set_option("display.max_rows", None, "display.max_columns", None)

# Lines 18 - 56 are for generating lists, dictionaries and Pandas DataFrames that are needed for storing several data.
results_amplitude = pd.DataFrame(columns={"participant",
                                          "elevation",
                                          "peak_amplitude"})
results_rms = pd.DataFrame(columns={"participant",
                                    "elevation",
                                    "rms"})
pca_evokeds_b = []
pca_evokeds_mb = []
pca_evokeds_mt = []
pca_evokeds_t = []

pca_evokeds = {"t": np.NaN, "mt": np.NaN,
               "mb": np.NaN, "b": np.NaN}

pca_peaks = {"t": np.zeros(30), "mt": np.zeros(30),
             "mb": np.zeros(30), "b": np.zeros(30)}

rms_dict = {"t": np.zeros(30), "mt": np.zeros(30),
            "mb": np.zeros(30), "b": np.zeros(30)}

z_score = pd.DataFrame(columns=["participant",
                                "elevation"])

z_score_list = []

z_score_new = pd.Series([])

# Do pca on all epoched data,
# afterwards use calculated rotation matrix on every
# condition separately.
# Determine peak amplitude of averaged pca components for every condition, together with z scores and root mean squares.
for i, subject in enumerate(range(4, 34)):
    if subject < 10:
        subject = "he0%s" % (subject)
    else:
        subject = "he%s" % (subject)
    epochs_fname = "/home/max/Dokumente/Projects/" \
                   "EEG_Bachelor/data/%s/epochs/" \
                   "epochs_rejected_headmotion.fif" % (subject)
    epochs = mne.read_epochs(epochs_fname, preload=True).crop(0.9, 1.5)
    n_epochs, n_channels, n_times = epochs._data.shape
    X = epochs._data  # sensor data
    X -= np.expand_dims(X.mean(axis=2), axis=2)  # center data on 0
    X = np.transpose(epochs._data,
                     (1, 0, 2)).reshape(n_channels,
                                        n_epochs * n_times).T  # concatenate
    C0 = X.T @ X  # Data covariance Matrix
    n_components = 5
    D, P = np.linalg.eig(C0)  # eigendecomposition of C0
    idx = np.argsort(D)[::-1][0:n_components]   # sort array
                                                # by descending magnitude
    D = D[idx]
    P = P[:, idx]  # rotation matrix
    Y = X @ P  # get principle components
    probes = ["t", "mt", "mb", "b"]
    for probe in probes:
        # use rotation matrix on every single condition
        n_epochs, n_channels, n_times = epochs[probe]._data.shape
        X = epochs[probe]._data
        X -= np.expand_dims(X.mean(axis=2), axis=2)  # center data on 0
        X = np.transpose(epochs[probe]._data,
                         (1, 0, 2)).reshape(n_channels, n_epochs * n_times).T
        Y = X @ P  # get principle components
        pca = np.reshape(Y.T, [-1, n_epochs, n_times]).transpose([1, 0, 2])
        pca_evoked = mne.EvokedArray(np.mean(pca, axis=0),
                                     mne.create_info(
                                     n_components, epochs[probe].info["sfreq"],
                                     ch_types="eeg"),
                                     tmin=epochs[probe].tmin)
        pca_evoked.pick_channels(ch_names=["0"])
        pca_evokeds[probe] = pca_evoked
        _, _, amplitude = pca_evoked.get_peak(tmin=1.05,
                                              tmax=1.2,
                                              return_amplitude=True,
                                              mode="pos")
        amplitude = amplitude * 10**6  # From volts to
                                       # microvolts
        pca_peaks[probe][i] = amplitude
        if probe == "b":
            pca_evokeds_b.append(pca_evoked)
        elif probe == "mb":
            pca_evokeds_mb.append(pca_evoked)
        elif probe == "mt":
            pca_evokeds_mt.append(pca_evoked)
        elif probe == "t":
            pca_evokeds_t.append(pca_evoked)
        results_amplitude = results_amplitude.append(
                                 {"elevation": probe,
                                  "participant": i,
                                  "peak_amplitude": amplitude},
                                                     ignore_index=True)
        pca_cropped = pca_evoked.copy().crop(1.05, 1.3)
        data = pca_cropped.data  # get data from evokeds
        mean = np.mean(data)
        rms = np.sqrt(np.mean(data**2))  # make rms
        rms = rms * 10**6
        rms_dict["%s" % (probe)][i] = rms
        results_rms = results_rms.append({"elevation": probe,
                                          "participant": i,
                                          "rms": rms_dict
                                          ["%s" % (probe)][i]},
                                         ignore_index=True)
        z_score = z_score.append({"elevation": probe,
                                  "participant": i},
                                  ignore_index=True)
    zscore_t, zscore_mt, zscore_mb, zscore_b = zscore([pca_peaks["t"][i],
        pca_peaks["mt"][i],
        pca_peaks["mb"][i],
        pca_peaks["b"][i]])
    z_score_list.append(zscore_t)
    z_score_list.append(zscore_mt)
    z_score_list.append(zscore_mb)
    z_score_list.append(zscore_b)

    del epochs

for x in range(len(z_score_list)):
    z_score_new[x] = z_score_list[x]

z_score.insert(2, "zscore", z_score_new)

pca_evokeds_b = mne.grand_average(pca_evokeds_b)
pca_evokeds_mb = mne.grand_average(pca_evokeds_mb)
pca_evokeds_mt = mne.grand_average(pca_evokeds_mt)
pca_evokeds_t = mne.grand_average(pca_evokeds_t)
evokeds = {"-37.5°": pca_evokeds_b, "-12.5°": pca_evokeds_mb,
           "+12.5°": pca_evokeds_mt, "+37.5°": pca_evokeds_t}

mne.viz.plot_compare_evokeds(evokeds,
                             vlines=[1.0],
                             title=" ")

zscore_t = []
zscore_mt = []
zscore_mb = []
zscore_b = []

for i in range(len(z_score)):
    if z_score.elevation[i] == "t":
        zscore_t.append(z_score.zscore[i])
    elif z_score.elevation[i] == "mt":
        zscore_mt.append(z_score.zscore[i])
    elif z_score.elevation[i] == "mb":
        zscore_mb.append(z_score.zscore[i])
    elif z_score.elevation[i] == "b":
        zscore_b.append(z_score.zscore[i])

# Do repeated measures Anova on z-scores.
print(AnovaRM(data=z_score,
              depvar="zscore",
              subject="participant",
              within=["elevation"]).fit())

# test for significant differences between elevations.
wilcoxon(zscore_b, zscore_t)  # Choose conditions you want to compare.

# Plot z score tuning curves.
x = np.array([37.5, 12.5, -12.5, -37.5] * 30)
y = np.array(z_score.zscore)
fig1 = sns.lineplot(x, y, color="slategrey")
fig1.set_ylabel("Standardized activation (z-scores)")
fig1.set_xlabel("Elevation [°]")
fig2 = sns.regplot(x,y, scatter=False, ci=False, line_kws={"color": "black", "linestyle": "dotted"})
plt.show()

# Save any given dictionary.
with open('rms_dict.p', 'wb') as fp:
    pickle.dump(rms_dict, fp, protocol=pickle.HIGHEST_PROTOCOL)  # Choose which dictionary you want to save.
