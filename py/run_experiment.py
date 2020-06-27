import sys
sys.path.append("/home/max/Dokumente/Projects/EEG_Bachelor/py")
sys.path.append("/home/max/Dokumente/Projects/freefield_toolbox")
sys.path.append("/home/max/Dokumente/Projects/soundtools")
from freefield import camera, setup
import localization_test
import sequences
import elevation_freefield


subject = "subject" # enter name of subject


# STEP 1: Initialize
setup.set_speaker_config("dome")
camera.init(type="freefield")

# STEP 2: Generate folders for localization test responses
expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
         "/"+"localization_test_responses/"  # saving path
localization_test.make_dir(expdir)

# STEP 3: Calibrate cameras
coords = camera.calibrate_camera(n_reps=3)

# STEP 4: Calibrate speakers, so that frequency and level is constant for every speaker
speakers = [(0, 37.5), (0, 25), (0, 12.5), (0, 0), (0, -12.5), (0, -25), (0, -37.5)]
rec, rec_filt = setup.equalize_speakers(speakers, plot=True)

# STEP 5: Localization test under freefield conditions
sound = slab.Sound.pinknoise(duration=0.1) # choose pinknoise of 0.1s duration
response = setup.localization_test(sound, speakers, n_reps=3)

# STEP 6: Save localization test responses,
# 		calculate mean absolute error, load responses if necessary
response_path = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
                "/"+"localization_test_responses/result.pkl"
localization_test.save_response(response_path)
# OPTIONAL: response = localization_test.read_response(response_path)
mae = (response.ele_target-response.ele_response).abs().mean()

# STEP 7: Generate sequences for each participant
expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
         "/"+"sequences"
probes=[14,16,2,4] # choose speakers as probes
rep = 8 # choose amount of repititions per block
n_blocks_per_run = 9 # choose blocks
# per run -> 4 probes x 1,5s = 6s x 8 reps # = 48s x 9blocks= 7.2 min x 4 =
# 28.8 min experiment duration
n_runs=4 # choose amount of runs per experiment
sequences.make_blocks(probes, rep, n_blocks_per_run, n_runs, expdir, subject)

# STEP 8: Generate folders for headpose responses during experiment
expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
    	 "/"+"headpose_responses/"   #folder path
elevation_freefield.make_dir(expdir)

# STEP 9: Execute freefield experiment under real stimuli conditions
rx8 = "C:/Projects/EEG_Elevation_Max/rcx/play_noise_buf.rcx"
rp2 = "C:/Projects/EEG_Elevation_Max/rcx/button.rcx"
setup.initialize_devices(ZBus=True, cam=True, RX8_file=rx8, RP2_file=rp2)
elevation_freefield.run_experiment(subject)
