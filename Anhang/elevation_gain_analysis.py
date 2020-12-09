from pandas import read_csv
import pandas as pd
import seaborn as sns
import scipy
from scipy.stats import linregress
import numpy as np
from matplotlib import pyplot as plt
import pickle
from scipy.stats import spearmanr
pd.set_option("display.max_rows", None, "display.max_columns", None)

# read response csv files from a single subject
pca_peaks = pd.read_csv("/home/max/Dokumente/Projects/EEG_Bachelor/DataFrames/pca_peaks.csv", index_col=0)
z_score = pd.read_csv("/home/max/Dokumente/Projects/EEG_Bachelor/DataFrames/zscore.csv", index_col=0)
with open('rms_dict.p', 'rb') as fp:
    rms = pickle.load(fp)
with open('amp_mean.p', 'rb') as fp:
    amp_mean = pickle.load(fp)
results_amplitude = pd.read_csv("/home/max/Dokumente/Projects/EEG_Bachelor/DataFrames/results_amlitude.csv", index_col=0)

# Take z_scores for every condition out of pd.DataFrame and make put them into separate lists.
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

amplitude_t = []
amplitude_mt = []
amplitude_mb = []
amplitude_b = []

for i in range(len(results_amplitude)):
    if results_amplitude.elevation[i] == "t":
        amplitude_t.append(results_amplitude.peak_amplitude[i])
    elif results_amplitude.elevation[i] == "mt":
        amplitude_mt.append(results_amplitude.peak_amplitude[i])
    elif results_amplitude.elevation[i] == "mb":
        amplitude_mb.append(results_amplitude.peak_amplitude[i])
    elif results_amplitude.elevation[i] == "b":
        amplitude_b.append(results_amplitude.peak_amplitude[i])

# Take response files for one subject before and durin EEG measures.
for i, s in enumerate(range(11, 12)):  # Choose subject.
    response = pd.DataFrame(columns=["ele_target",
                                 "ele_response"])
    if s < 10:
        subject = "he0%s" % (s)
    else:
        subject = "he%s" % (s)
    for block in range(6):
        file_path = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/responses/" % (subject)
        block_response = read_csv(file_path +
            "%s_freefield_block_%s.csv" %
            (subject, block), index_col=0)
        block_response = block_response.drop(columns=
                         ["azi_target", "azi_response"])
        response = response.append(block_response,
                                   ignore_index=True)
    response_test = read_csv(file_path +
            "%s_freefield_test.csv" %
            (subject), index_col=0)
    response_test = response_test.drop(columns=
                         ["azi_target",
                          "azi_response"])
response = response.dropna()
response_test = response_test.dropna()

# Calculate elevation gain before and during eeg measures for a single subject.
fig, ax = plt.subplots(2, sharex="col", sharey="col")
x1 = response_test.ele_target
y1 = response_test.ele_response
x2 = response.ele_target
y2 = response.ele_response

# Plot linear regression between actual and perceived elevation for the chosen subject.
sns.regplot(x="ele_target",
            y="ele_response",
            ci=None,
            data=response_test,
            scatter_kws={"color": "dimgray"},
            line_kws={"color": "darkcyan"}, marker=".", ax=ax[0])
sns.regplot(x="ele_target",
            y="ele_response",
            ci=None,
            data=response,
            scatter_kws={"color": "dimgray"},
            line_kws={"color": "darkcyan"}, marker=".", ax=ax[1])
ax[0].set_ylabel("Response elevation [°]")
ax[0].set_xlabel(" ")
ax[1].set_ylabel("Response elevation [°]")
ax[1].set_xlabel("Target elevation [°]")
fig.tight_layout()
plt.show()

# Calculate elevation gain plus mean absolute error over all subjects.
eg = []  # Elevation gain.
mae = []  # Mean absolute error.
for s in range(4, 34):
    response = pd.DataFrame(columns=["ele_target",
                                 "ele_response"])
    if s < 10:
        subject = "he0%s" % (s)
    else:
        subject = "he%s" % (s)
    for block in range(6):
        file_path = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/responses/" % (subject)
        block_response = read_csv(file_path +
            "%s_freefield_block_%s.csv" %
            (subject, block), index_col=0)
        block_response = block_response.drop(columns=
                         ["azi_target", "azi_response"])
        response = response.append(block_response,
                                   ignore_index=True)
    response = response.dropna()
    x = response.ele_target
    y = response.ele_response
    slope, intercept, rv, pv, stderr = linregress(x, y)
    eg.append(slope)
    mae.append((response.ele_target-response.ele_response).abs().mean())

# Localization test elevation gain for all subjects.
eg_test = []  # Elevation gain before EEG recordings.
for s in range(4, 34):
    response = pd.DataFrame(columns=["ele_target",
                                 "ele_response"])
    if s < 10:
        subject = "he0%s" % (s)
    else:
        subject = "he%s" % (s)

    file_path = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/responses/" % (subject)
    response = read_csv(file_path +
        "%s_freefield_test.csv" %
        (subject), index_col=0)
    response = response.drop(columns=
                     ["azi_target", "azi_response"])
    response = response.append(response,
                                   ignore_index=True)
    response = response.dropna()
    x = response.ele_target
    y = response.ele_response
    slope, intercept, rv, pv, stderr = linregress(x, y)
    eg_test.append(slope)

# Get EG mean value plus standard deviation.
mean = np.mean(eg)
sem = scipy.stats.sem(eg)

# Compare EG with slopes of tuning curves.
elevations = [-37.5, -12.5, 12.5, 37.5]
eg_tc = []  # Tuning curve eg
eg_comparison = pd.DataFrame()
for i, sub in enumerate(range(4, 34)):
    y2 = np.array([zscore_b[i],
                   zscore_mb[i],
                   zscore_mt[i],
                   zscore_t[i]]).flatten()
    slope, intercept, rv, pv, stderr = linregress(elevations, y2)
    eg_tc.append(slope)

# For better comparison, put all three EGs into one pd.DataFrame.
eg_comparison["Behavioral EG"] = eg
eg_comparison["Tuning curve EG"] = eg_tc
eg_comparison["Localization test EG"] = eg_test

# Plot correlation between behavioral and tuning curve EG.
sns.lmplot(x="Behavioral EG",
           y="Localization test EG",
           data=eg_comparison,
           scatter_kws={"color": "chocolate"},
           line_kws={"color": "teal"},
           ci=None)
plt.gca().invert_yaxis()
plt.show()

# Calculate Spearman correlation coefficient plus Wilcoxon signed-rank test for any EG.
spearmanr(eg_comparison["Behavioral EG"],
          eg_comparison["Localization test EG"])
wilcoxon(eg_test, eg)
