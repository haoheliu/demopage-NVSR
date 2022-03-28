from glob import glob
import librosa
import soundfile as sf
import numpy as np 
from tqdm import tqdm 

for file in tqdm(glob("*/*.wav") + glob("*/*/*.wav") + glob("*/*/*/*.wav")):
    x,rate = librosa.load(file, sr=None)
    x = x/np.max(np.abs(x))
    sf.write(file,x,samplerate=rate)