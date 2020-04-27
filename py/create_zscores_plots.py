import sys
sys.path.append("/home/max/Dokumente/python_scripts/mne_addon")
import mne
import numpy as np
from mne_addon import analysis
from mne import read_evokeds
from matplotlib import pyplot as plt
from scipy.stats import zscore, sem


"""
put evokeds of every subject into list and plot data
"""

rms_integral={"t-mt":np.zeros(4), "t-mb":np.zeros(4),
			  "t-b":np.zeros(4), "b-mt":np.zeros(4),
			  "b-mb":np.zeros(4), "b-t":np.zeros(4)}
evokeds=[]
for i in range(1,4): #loop through subjects
	if i < 10:
		subject="eegl0%s" % (i)
	else:
		subject="eegl%s" % (i)
	for eye_fixation in ["mid"]: #choose line of sight	
		for adaptor in ["t","b"]:
			if adaptor == "t":
				probes = ["mt","mb","b"]
			elif adaptor == "b":
				probes = ["mb","mt","t"]
			for probe in probes:
						evoked = read_evokeds("/home/max/Dokumente/python_scripts/mne_addon/mne_addon/evokeds/%s/%s_%s-%s-%s-ave.fif"
									  		% (subject, subject, eye_fixation, adaptor, probe)) [0]
						evoked.crop(0.65,0.9)
						evokeds.append(evoked)
						rms=analysis.global_estimate(evoked, mode="rms")
						rms_integral["%s-%s" % (adaptor, probe)][i]=np.trapz(rms)


"""
lineplot zscores
"""

#put z-scores of same condition from all subjects into one list
t_mt=list(rms_integral["t-mt"][i] for i in [1,2,3])
t_mb=list(rms_integral["t-mb"][i] for i in [1,2,3])
t_b=list(rms_integral["t-b"][i] for i in [1,2,3])
b_mt=list(rms_integral["b-mt"][i] for i in [1,2,3])
b_mb=list(rms_integral["b-mb"][i] for i in [1,2,3])
b_t=list(rms_integral["b-t"][i] for i in [1,2,3])
#create median of zscores of one condition
t_mt_median=np.median(t_mt)
t_mb_median=np.median(t_mb)
t_b_median=np.median(t_b)
b_mt_median=np.median(b_mt)
b_mb_median=np.median(b_mb)
b_t_median=np.median(b_t)
#create standard error of the mean
t_mt_sem=sem(t_mt)
t_mb_sem=sem(t_mb)
t_b_sem=sem(t_b)
b_mt_sem=sem(b_mt)
b_mb_sem=sem(b_mb)
b_t_sem=sem(b_t)
#create lineplots
fig,ax = plt.subplots()
x= [1,3,5]
x2 = [1.1, 3.1, 5.1]
y_upper= [t_mt_median, t_mb_median, t_b_median]
y_lower= [b_mb_median, b_mt_median, b_t_median]
yerr_upper = [t_mt_sem,t_mb_sem,t_b_sem]
yerr_lower = [b_mt_sem,b_mb_sem,b_t_sem]
plt.errorbar (x=x,y=y_upper,yerr=yerr_upper,color="darkred",capsize=5,marker="x", label=("upper adaptor"))
plt.errorbar (x=x2,y=y_lower,yerr=yerr_lower, color = "darkblue",capsize=5,marker="x", label=("lower adaptor"))
ax.set_ylabel("z-scores")
ax.set_xlabel("Probeposition")
ax.set_xticks(x)
ax.set_xticklabels(("25°", "50°", "75°"))
plt.legend()
plt.show()


"""
boxplot
"""

#boxplot upper adaptor
data_norm = [zscore(rms_integral["t-mt"]),zscore(rms_integral["t-mb"]),zscore(rms_integral["t-b"])]
fig1, ax1 = plt.subplots()
ax1.boxplot(data_norm)
ax1.set_title("Upper Adaptor")
ax1.set_ylabel('z-scores')
ax1.set_ylim(-2.5, 2)
label = ["-25°", "-50°", "-75°"]
ax1.set_xticklabels(label)
ax1.set_xlabel("adaptor-probe separation")
plt.show()

#boxplot lower adaptor
data_norm = [zscore(rms_integral["b-mb"]),zscore(rms_integral["b-mt"]),zscore(rms_integral["b-t"])]
fig2, ax2 = plt.subplots()
ax2.boxplot(data_norm)
ax2.set_title("Lower Adaptor")
ax2.set_ylabel('z-scores')
ax2.set_ylim(-2.5, 2)
label=["+25°","+50°","+75°"]
ax2.set_xticklabels(label)
ax1.set_xlabel("adaptor-probe separation")
plt.show()

#lineplot medians of zscores for adaptors and probes
data_norm = [np.median((zscore(rms_integral["b-mb"]),zscore(rms_integral["b-mt"]),zscore(rms_integral["b-t"])))]
fig, ax = plt.subplots()
plt.plot(data_norm)
ax.set_ylabel("z-scores")
ax.set_xlabel("Probeposition")
ax.set_xticklabels(("25°", "50°", "75°"))
plt.legend()
fig.show()