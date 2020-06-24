from freefield import camera, setup
import slab
import os
import sys
import pandas as pd
sys.path.append("C:/Projects/freefield_toolbox")
sys.path.append("C:/Projects/soundtools")
_location = setup._location

# Initialize
setup.set_speaker_config("dome")
camera.init(type="freefield")

# Define relevant variables for setup.localization_test()
speakers = [(0, 37.5), (0, 25), (0, 12.5), (0, 0), (0, -12.5), (0, -25), (0, -37.5)]
sound = slab.Sound.pinknoise(duration=0.3)

#  TODO: increase sound duration and level


def make_dir(expdir):
    try:
        os.makedirs(expdir)
    except OSError:
        print("Creation of the directory %s failed" % expdir)
    else:
        print("Successfully created the directory %s" % expdir)


def save_response(response_path):
    response_path = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"localization_test_responses/result.pkl"
    response.to_pickle(response_path)
    print("Saved responses as \n %s!" % response_path)


def read_response(response_path):
    response_path = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"localization_test_responses/result.pkl"
    response = pd.read_pickle(response_path)
    print("Responses loaded!")
    return response


if __name__ == "__main__":

    subject = "Max_get_headpose_n=5_dur=0.3"  # name der testperson
    expdir = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
        "/"+"localization_test_responses"  # speicherort
    make_dir(expdir)
    coords = camera.calibrate_camera(n_reps=3)  # calibrate camera
    response = setup.localization_test(sound, speakers, n_reps=3)
    response_path = "C:/Projects/EEG_Elevation_Max/data/"+subject + \
                    "/"+"localization_test_responses/result.pkl"
    save_response(response_path)
    # response = read_response(response_path)
    mae = (response.ele_target-response.ele_response).abs().mean()
