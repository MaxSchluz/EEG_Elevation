dur_experiment = 45
n_speakers = 4

# These are the variables for the experiment plan
dur_adapter = 1.0
dur_stim = 0.1
isi = 0.4
target_frequency = 0.1

n_trials = dur_experiment*60 / (dur_adapter+dur_stim+isi)
n_trials_per_target = n_trials / n_speakers
n_targets = n_trials*target_frequency

print("given a experiment duration of %s minutes, adapter and stimulus"
      " durations of %s and %s seconds and an ISI of 0.4 seconds \n we can get "
      "%s trials. This means there are %s trials for each of the %s speakers.\n"
      "Of the %s trials, %s will be targets. This means there are %s targets\n"
      "per condition."
      %(dur_experiment, dur_adapter, dur_stim, n_trials, n_trials_per_target, n_speakers, n_trials, n_targets, n_targets/n_speakers))
