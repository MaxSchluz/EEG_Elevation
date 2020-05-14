import sys
sys.path.append("C:/Projects/freefield_toolbox")
sys.path.append("C:/Projects/soundtools")
import slab
from freefield import camera, setup
import time
_location = setup._location
# Initialize
setup.set_speaker_config("dome")
setup.initialize_devices(RP2_file=_location.parent/"rcx"/"button.rcx",
                         RX8_file=_location.parent/"rcx"/"play_buf.rcx",
                         connection='GB')
camera.init()
speakers = [(0, 50), (0, 37.5), (0, 25), (0, 12.5), (0, 0),
            (0, -12.5), (0, -25), (0, -37.5), (0, -50)]

stim = slab.Sound.whitenoise(duration=1.0)

response=[]
world_coordinates, camera_coordinates=camera.calibrate_camera()
camera.camera_to_world(world_coordinates, camera_coordinates)
for s in speakers:
    _, ch, proc = setup.speaker_from_direction(azimuth=s[0], elevation=s[1])
    setup.set_variable(variable="chan", value=ch, proc="RX8%s"% int(proc))
    setup.set_variable(variable="playbuflen", value=48828, proc="RX8s")
    setup.set_variable(variable="data", value=stim.data, proc="RX8s")
    setup.trigger()
    while setup.get_variable(variable="playback", proc="RX81"):
        time.sleep(0.01)
    while not setup.get_variable(variable="response", proc="RP2"):
        time.sleep(0.01)
    ele,azi = camera.get_headpose()
    response.append([s, ele, azi])






camera.deinit()
setup.halt()
