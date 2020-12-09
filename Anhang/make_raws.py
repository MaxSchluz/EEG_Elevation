import mne
import os

# This script serves the purpose of converting files that come out of the EEG into raw .fif files.
for i in range(4, 34):
  if i < 10:
    subject = "he0%s" % (i)
  else:
    subject = "he%s" % (i)
  path = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/raw_dir/" % (subject)
  raw_filenames = []

  for block in range(6):
    raw_filename = "%sblock%s.vhdr" % (path, str(block))
    raw_filenames.append(raw_filename)

  raws = []
  for i in range(6):
    raw = mne.io.read_raw_brainvision(raw_filenames[i], preload=True)
    raws.append(raw)

  raw = mne.concatenate_raws(raws)

  mapping = {"1":"Fp1", "2":"Fp2", "3":"F7", "4":"F3","5":"Fz",         "6":"F4", "7":"F8","8":"FC5", "9":"FC1",
             "10":"FC2", "11":"FC6", "12":"T7", "13":"C3", "14":"Cz ", "15":"C4", "16":"T8", "17":"TP9", "18":"CP5", "19":"CP1",
             "20":"CP2","21":"CP6","22":"TP10","23":"P7", "24":"P3", "25":"Pz", "26":"P4", "27":"P8", "28":"PO9", "29":"O1",
            "30":"Oz", "31":"O2", "32":"PO10", "33":"AF7", "34":"AF3", "35":"AF4", "36":"AF8", "37":"F5", "38":"F1", "39":"F2",
           "40":"F6", "41":"FT9","42":"FT7", "43":"FC3", "44":"FC4", "45":"FT8", "46":"FT10", "47":"C5", "48":"C1", "49":"C2",
             "50":"C6", "51":"TP7", "52":"CP3", "53":"CPz", "54":"CP4", "55":"TP8", "56":"P5", "57":"P1", "58":"P2", "59":"P6",
             "60":"PO7", "61":"PO3", "62":"POz", "63":"PO4", "64":"PO8"}

  raw.rename_channels(mapping)

  montage_path = "/home/max/Dokumente/Projects/EEG_Bachelor/"
  montage_file= "AS-96_REF"
  montage= mne.channels.read_montage(kind=montage_file,path=montage_path, unit="auto")

  raw.set_montage(montage)

  folder = "/home/max/Dokumente/Projects/EEG_Bachelor/data/%s/raw_data" % (subject)
  if not os.path.isdir(folder):
      os.makedirs(folder)
  raw.save(folder+"/%s-raw.fif" % (subject),
           overwrite=True)
  del raw
