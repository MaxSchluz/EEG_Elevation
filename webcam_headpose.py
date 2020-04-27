# append the paths to the freefield_toolbox and soundtools folders:
import sys
sys.path.append("/home/max/Dokumente/python_scripts/soundtools/")
sys.path.append("/home/max/Dokumente/python_scripts/freefield_toolbox/")
from freefield import camera


camera.init(type="web")  # initialize the camera
# define some target coordinates:
target_coordinates = [(0, -20), (0, 0), (0, 20), (20, 0), (-20, 0)]
# do the camera calibration:
camera.calibrate_camera(target_coordinates)

# get the headpose in camera coordinates
elevation, azimuth = camera.get_headpose()

# get the headpose in world coordinates
elevation, azimuth = camera.get_headpose(convert_coordinates=True)


camera.deinit()  # de-initialize the camera
