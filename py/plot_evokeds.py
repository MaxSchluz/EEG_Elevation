import mne
from mne import read_evokeds
from matplotlib import pyplot as plt


"""
create list of evokeds for one condition and average
choose eye fixation, adaptor and probe position
"""


evokeds=[]
for i in range(1,4): #loop through subjects
	if i < 10:
		subject="eegl0%s" % (i)
	else:
		subject="eegl%s" % (i)
	for eye_fixation in ["mid"]: #choose eye fixation
		for adaptor in ["b"]: #choose adaptor
			probes = ["t"] #choose probe
			for probe in probes:
					evoked = read_evokeds("/home/max/Dokumente/python_scripts/mne_addon/mne_addon/evokeds/%s/%s_%s-%s-%s-ave.fif"
									  % (subject, subject, eye_fixation, adaptor, probe))[0]
					evokeds.append(evoked)
evokeds_average=mne.grand_average(evokeds)


"""
take evokeds_average to plot evokeds of every subject into one topo plot
"""

baseline_adaptor_onset=(0.108,0.170) #baseline -0.1,0
baseline_probe_onset=(0.676,0.739,0.822) #baseline 0.5,0.6
evokeds_average.plot_joint(times=baseline_probe_onset) #plot complete trial


"""
plot evoked response at given electrode averaged over all subjects
"""

ch_name = ["Fz"] #pick electrode
channel = mne.pick_channels(ch_names=evokeds_average.ch_names, include=ch_name)
mne.viz.plot_compare_evokeds([evokeds], picks=channel,truncate_xaxis=False,colors=["darkgreen"])


"""
create list of evokeds of all conditions and one line of sight
"""

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
				probes = ["mt","mb","t"]
			for probe in probes:
					evoked = read_evokeds("/home/max/Dokumente/python_scripts/mne_addon/mne_addon/evokeds/%s/%s_%s-%s-%s-ave.fif"
									  % (subject, subject, eye_fixation, adaptor, probe)) [0]
					evoked.crop(tmin=0.5, tmax=1)
					evokeds.append(evoked)



"""
pick single conditions out of evokeds list
"""

b_mt=list(evokeds[i] for i in [0,6,12])
b_mb=list(evokeds[i] for i in [1,7,13])
b_t=list(evokeds[i] for i in [2,8,14])
t_mt=list(evokeds[i] for i in [3,9,15])
t_mb=list(evokeds[i] for i in [4,10,16])
t_b=list(evokeds[i] for i in [5,11,17])
b_mt_average=mne.grand_average(b_mt)
b_mb_average=mne.grand_average(b_mb)
b_t_average=mne.grand_average(b_t)
t_mt_average=mne.grand_average(t_mt)
t_mb_average=mne.grand_average(t_mb)
t_b_average=mne.grand_average(t_b)



"""
take lists and plot effects of adaptor and probe
"""

#create dictionaries of pairs of adaptors and probes
average_adaptor_t = {"-25°": t_mt, "-50°": t_mb, "-75°": t_b}
average_adaptor_b = {"+25°": b_mb, "+50°": b_mt, "+75°": b_t}

#choose plot colors
colors_1= ['darkred','lightcoral','mistyrose']
colors_2=['darkblue','blue', 'cornflowerblue']

#choose electrode
ch_name = ["Fz"]
channel = mne.pick_channels(ch_names=t_b_average.ch_names, include=ch_name)
mne.viz.plot_compare_evokeds(average_adaptor_t, picks=channel, vlines=[0.6], colors=colors_1)
ch_name = ["Fz"]
channel = mne.pick_channels(ch_names=b_t_average.ch_names, include=ch_name)
mne.viz.plot_compare_evokeds(average_adaptor_b, picks=channel, vlines=[0.6], colors=colors_2)


# all channels
mne.viz.plot_compare_evokeds(average_adaptor_t, vlines=[0.6], colors=colors_1)
mne.viz.plot_compare_evokeds(average_adaptor_b, vlines=[0.6], colors=colors_2)