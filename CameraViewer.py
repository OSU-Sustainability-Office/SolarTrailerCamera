# Filename: CameraViewer.py
# Info: Quick little script to take photos over a web-camera.
from subprocess import run
from os import path, remove
import sched, time
from datetime import datetime

# Constants for modifying script behavior
CAMERA_NAME = 'C270 HD WEBCAM'
USER_NAME = 'Milan Donhowe' # <-- change per PC
DELAY_MS = 900000 # 10 minutes * 60 seconds * 1000 ms = 15 minutes in ms
UPLOAD_PATH = path.join('C:\\', 'Users', USER_NAME, 'Box', 'Sustainability Photography', 'Programs', 'Solar Trailer', 'SolarTrailerCamera')

if not path.exists(UPLOAD_PATH):
  print("Couldn't check the path:", UPLOAD_PATH)
  print("Box upload path doesn't exist.  Is Box running?")
  exit(1)

class CommandCamError(Exception):
  """Custom exception for when the command camera program fails to take a picture"""
  def __init__(self, code, message="CommandCam did not return zero response code!"):
    self.return_code = code
    self.message = message
    super().__init__(self.message)
  
  def __str__(self):
    return f'CommandCam returned responsecode={self.return_code} -> {self.message}'

class Camera:
  def __init__(self, cameraName: str):
    self._WEBCAM_NAME = cameraName

  def takePhoto(self, filename):
    photoProgram = run(["CommandCam.exe", "/devname", self._WEBCAM_NAME, '/filename', filename], capture_output=True)
    if photoProgram.returncode != 0:
      raise CommandCamError(photoProgram.returncode)
    return filename


def write2box(filename: str):
  """upload file to box"""
  # Read the local photo image
  with open(filename, 'rb') as photoFile:
    photo = photoFile.read()
  try:
    # Write to Box folder
    with open(path.join(UPLOAD_PATH, filename), 'wb+') as f:
      f.write(photo)
    # delete local file if upload worked
    remove(filename)
    print(f'successfully uploaded {filename} to box')
  except:
    print(f'could not upload {filename}, keeping local image.')
camera = Camera(CAMERA_NAME)

s = sched.scheduler(time.time, time.sleep)


def cameraJob():
  """Takes photograph from photo & uploads to Box"""
  photoName = datetime.now().strftime("%d_%m_%Y@[%Hh_%Mm_%Ss].bmp")
  try:
    camera.takePhoto(photoName)
    write2box(photoName)
    s.enter(DELAY_MS, 1, cameraJob)
    s.run()
  except CommandCamError as err:
    print(f'Caught error: {err}')
    exit(2)

print('Starting loop')
cameraJob()