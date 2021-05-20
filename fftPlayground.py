import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile # get the api
from statistics import mean

fs, data = wavfile.read('output.wav') # load the data
c = fft(data)
d = len(c)/2
print(d)
total = abs(c[:(int(d-1))])

sub_bass = total[16:60]
bass = total[60:250]
low_mids = total[250:2000]
hi_mids = total[2000:4000]
presence = total[4000:6000]
