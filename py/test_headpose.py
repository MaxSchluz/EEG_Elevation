import sys
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
import time
from pathlib import Path
import numpy
sys.path.append("C:/Users/maxsc_000/Desktop/python_scripts/soundtools/")
sys.path.append("C:/Users/maxsc_000/Desktop/python_scripts/freefield_toolbox/")
from freefield import setup, camera
import slab


linear_regressor = LinearRegression()
rp2_file = setup._location.parents[0] / Path("rcx/button_response.rcx")
rx8_file = setup._location.parents[0] / Path("rcx/leds.rcx")

n_reps = 5  # --> Wie oft wird jede led position wiederholt
n_images = 3  # --> Wie viele Bilder werden gemacht um die headpose zu ermitteln

setup.set_speaker_config("dome")
setup.initialize_devices(RX8_file=rx8_file, RP2_file=rp2_file, ZBus=True, cam=True)

leds = setup.all_leds()  # Lautsprecher an denen eine LED ist
# randomisierete sequenz erstellen:
seq = slab.psychoacoustics.Trialsequence(
    name="camera calibration", n_reps=n_reps, conditions=range(len(leds)))
# Liste mit zwei arrays (eins für jede Kamera):
results = \
    [numpy.zeros([seq.n_trials, 4]) for i in range(2)]

while not seq.finished:
    row = leds[seq.__next__()]  # nächstes element aus der sequenz
    setup.printv("trial nr %s: speaker at azi: %s and ele: of %s" %
                 (seq.this_n, row[3], row[4]))
    # Bit-wert setzen - die oberste LED funktioniert immer noch nicht
    setup.set_variable(variable="bitmask", value=row[5], proc=int(row[2]))
    while not setup.get_variable(variable="response", proc="RP2",
                                 supress_print=True):
        time.sleep(0.1)  # auf knopfdruck warten
    headpose, std = camera.get_headpose(n=n_images)  # headpose berechnen
    # led wieder ausschalten:
    setup.set_variable(variable="bitmask", value=0, proc=int(row[2]))
    for i, h in enumerate(headpose):
        # spalten 0 & 1: azimuth und elevation des lautsprechers
        # spalten 2&3: azimuthund elevatio n der headpose
        results[i][seq.this_n][0:2] = row[3:5]
        results[i][seq.this_n][2:] = h[0:2].round(2)  # estimated x and y


    # alle NaN Einträge rauswerfen:
    results[i] = results[i][~numpy.isnan(results[i]).any(axis=1)]

    # Regressionsgerade fitten und daten plotten:
    fig, ax = plt.subplots(camera._cam_list.GetSize(), sharex=True)
    fig.suptitle("Vertical")
    for i, r in enumerate(results):
        r = r[~numpy.isnan(r).any(axis=1)]
        linear_regressor.fit(r[:, 1].reshape(-1, 1), r[:, 3].reshape(-1, 1))
        pred = linear_regressor.predict(r[:, 1].reshape(-1, 1))
        ax[i].scatter(r[:, 1], r[:, 3])
        ax[i].plot(r[:, 1], pred[:, 0])
