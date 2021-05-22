import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile  # get the api
from statistics import mean

fs, data = wavfile.read("output.wav")  # load the data
# print(len(data))
c = fft(data)
d = len(c) / 2
total = abs(c[: (int(d - 1))])

sub_bass = mean(total[16:60])
bass = mean(total[60:250])
low_mids = mean(total[250:2000])
hi_mids = mean(total[2000:4000])
presence = mean(total[4000:6000])

vals = [sub_bass, bass, low_mids, hi_mids, presence]
print(vals)
