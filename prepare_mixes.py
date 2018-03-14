import os
import subprocess
import fnmatch
import wget 
import shutil
import zipfile
from random import randint

# create data directory
if not os.path.exists('data'):
    os.makedirs('data')

# download DSD100 dataset
if not os.path.isfile('data/DSD100.zip'):
    # Note: This will download a ~15GB .zip file.
    wget.download("http://liutkus.net/DSD100.zip", "data/DSD100")

# Unzip dataset
if not os.path.isdir("data/DSD100"):
    print("Unzipping dataset...")
    zip_ref = zipfile.ZipFile("data/DSD100.zip", 'r')
    zip_ref.extractal("data/DSD100")
    zip_ref.close()

# Downmix and convert mixtures to 16k
if not os.path.isdir('data/mixed_trainset_wav_16k'):
    print("Downmixing and downsampling mixtures to 16k...")
    os.makedirs('data/mixed_trainset_wav_16k')
    for directory in ['Dev', 'Test']:
        for root, dirnames, filenames in os.walk('data/DSD100/Mixtures/'+directory):
            for filename in fnmatch.filter(filenames, '*.wav'):
                filepath = os.path.join(root, filename)
                index = root.split('/')[4][0:3]
                print("Converting " + index + "...")
                sox_call = """sox "{0}" --norm=-1 -r 16k data/mixed_trainset_wav_16k/{1}_mixed.wav channels 1""".format(filepath, index)
                subprocess.call(sox_call, shell=True)

# Downmix and convert sources to 16k
if not os.path.isdir('data/unmixed_trainset_wav_16k'):
    print("Downmixing and downsampling sources to 16k...")
    os.makedirs('data/unmixed_trainset_wav_16k')
    os.makedirs('data/unmixed_trainset_wav')
    for directory in ['Dev', 'Test']:
        for track in os.listdir('data/DSD100/Sources/'+directory):
            if os.path.isdir('data/DSD100/Sources/'+directory+"/"+track):
                index = track[0:3]
                print("Converting " + index + "...")
                stems = [] # list to store track stems
                for root, dirnames, filenames in os.walk('data/DSD100/Sources/'+directory+"/"+track):
                    for filename in fnmatch.filter(filenames, '*.wav'):
                        filepath = os.path.join(root, filename)
                        stems.append('data/unmixed_trainset_wav/'+filename)
                        ### Try randomizing the gain values by a few dB here - then we see if it can learn that
                        sox_call = """sox "{0}" data/unmixed_trainset_wav/{2} vol {1}dB""".format(filepath, randint(-6,3) ,filename)
                        subprocess.call(sox_call, shell=True)
                sox_call = """sox -M "{0}" "{1}" "{2}" "{3}" --norm=-1 -r 16k \
                 data/unmixed_trainset_wav_16k/{4}_mixed.wav channels 1""".format(stems[0], stems[1], stems[2], stems[3], index)
                subprocess.call(sox_call, shell=True)
    shutil.rmtree('data/unmixed_trainset_wav')