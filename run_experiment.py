import sys
import json
import os
from pathlib import Path
sys.path.append("D:/Projects/freefield_toolbox")
sys.path.append("D:/Projects/soundtools")
sys.path.append("D:/Projects/EEG_Elevation_Max/py")
import sequences
import elevation_freefield, elevation_headphones
import slab
from freefield import camera, setup
EXPDIR = Path("D:/Projects/EEG_Elevation_Max")
with open(EXPDIR/Path('exp_config.json')) as f:
    cfg = json.load(f)
setup.set_speaker_config("dome")
setup._dB_level = cfg["dB_level"]

subject = "he02"  # ENTER subject name
SUBJECTDIR = Path(EXPDIR/"data"/subject)
experiment = "freefield"  # ENTER "freefield" or "headphones"

# STEP 1: make subject folder(s) and generate stimulus sequences:
if Path(SUBJECTDIR).is_dir():
    print("#### WARNING! Directory already exists ####")
else:
    os.makedirs(SUBJECTDIR)
    os.makedirs(SUBJECTDIR/"binaural_recordings")
    os.makedirs(SUBJECTDIR/"responses")
    os.makedirs(SUBJECTDIR/"sequences")
    for i in range(cfg["n_blocks"]):  # put for loop into else loop so that no sequences will be overwritten
        mmn_seq, trial_seq = sequences.sequence(speakers=cfg["target_speakers"], target_freq=cfg["target_freq"],
                                                n_reps=cfg["n_reps_per_block"])
        mmn_seq.save_json(SUBJECTDIR/"sequences"/("%s_mmn%s.seq" % (subject, i)))
        trial_seq.save_json(SUBJECTDIR/"sequences"/("%s_trials%s.seq" % (subject, i)))

# STEP 1.1: test loudspeaker equalization (once a week)
setup.initialize_devices(mode="play_and_record")
setup.test_equalization(slab.Sound.chirp(duration=0.05, samplerate=cfg["fs"]), cfg["test_speakers"])

# STEP 1.2: if not freefield experiment, make binaural recordings
if experiment == "headphones":
    for s in cfg["test_speakers"]+cfg["target_speakers"]:
        probes, adapter_probes = elevation_headphones.prepare_stimuli(s)
        probes.write(SUBJECTDIR/"binaural_recordings"/("%s_azi%s_ele%s_probes.zip" % (subject, s[0], s[1])))
        adapter_probes.write(SUBJECTDIR/"binaural_recordings"/("%s_azi%s_ele%s_adapter_probes.zip"
                             % (subject, s[0], s[1])))

# STEP 2: calibrate the camera:
camera.init()
camera.set(n_images=5, resolution=0.5)
camera.calibrate_camera(n_reps=4)

# STEP 3: run audiovisual training
if experiment == "headphones":
    sound = {}
    speakers = None
    for s in cfg["test_speakers"]:
        fname = "%s_azi%s_ele%s_binaural.wav" % (subject, s[0], s[1])
        sound[SUBJECTDIR/"binaural_recordings"/fname] = (s[0], s[1])
    setup.localization_test_headphones(sound=sound, n_reps=cfg["n_reps_training"], duration=1.0,
                                       speakers=cfg["test_speakers"], visual=True)
elif experiment == "freefield":
    setup.localization_test_freefield(duration=cfg["dur_loctest"], n_reps=cfg["n_reps_training"],
                                      speakers=cfg["test_speakers"], visual=True)

# STEP 4: run sound localization test
if experiment == "headphones":
    response = setup.localization_test_headphones(sound=sound, n_reps=cfg["n_reps_training"], duration=1.0,
                                                  speakers=cfg["test_speakers"], visual=False)
elif experiment == "freefield":
    response = setup.localization_test_freefield(duration=cfg["dur_loctest"], n_reps=cfg["n_reps_training"],
                                                 speakers=cfg["test_speakers"], visual=False)

response.to_csv(SUBJECTDIR/"responses"/("%s_%s_test.csv" % (subject, experiment)))
print((response.ele_target-response.ele_response).abs().mean())  # print mean error

# STEP 5:run audiovisual training with adapter and probe:
elevation_freefield.localization_test_adapter(n_reps=cfg["n_reps_training"], visual=True)

# STEP 6: run experiment
for block in range(cfg["n_blocks"]):
    input("### press enter to start block %s ###" % (block))
    # Load previously generated stimulus sequence:
    target_seq, trial_seq = slab.Trialsequence(), slab.Trialsequence()
    target_seq.load_json(file_name=SUBJECTDIR/"sequences"/("%s_mmn%s.seq" % (subject, block)))
    trial_seq.load_json(file_name=SUBJECTDIR/"sequences"/("%s_trials%s.seq" % (subject, block)))
    # Run block and save the response:
    response = elevation_freefield.run_block(target_seq, trial_seq)
    response_path = SUBJECTDIR/"responses"/("%s_%s_block_%s.csv" % (subject, experiment, block))
    response.to_csv(response_path)
    print("Saved responses as \n %s" % (response_path))
