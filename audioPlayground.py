from collections import deque
import matplotlib.pyplot as plt
import pyaudio
import wave
import sys
from scipy.io import wavfile  # get the api
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile  # get the api
from statistics import mean
import numpy as np


chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 0.2
filename = "output.wav"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print("Recording")

stream = p.open(
    format=sample_format,
    channels=channels,
    rate=fs,
    frames_per_buffer=chunk,
    input=True,
)

off = 0.0

minAmp = [float("inf")] * 5
maxAmp = [-1.0] * 5


def magic(data):
    global minAmp, maxAmp
    c = fft(data)
    d = len(c) / 2
    total = abs(c[: (int(d - 1))])
    sub_bass = mean(total[16:60])
    bass = mean(total[60:250])
    low_mids = mean(total[250:2000])
    hi_mids = mean(total[2000:4000])
    presence = mean(total[4000:6000])

    vals = [sub_bass, bass, low_mids, hi_mids, presence]

    for i in range(5):
        minAmp[i] = min(vals[i], minAmp[i])
        maxAmp[i] = max(vals[i], maxAmp[i])

    vals = [
        int(((val - minAmp[idx]) / maxAmp[idx]) * 1000) for idx, val in enumerate(vals)
    ]
    sys.stdout.write("\r" + ", ".join(map(str, vals)))
    sys.stdout.flush()


window = deque()  # Initialize array to store frames

# Store data in chunks for 3 seconds

for i in range(0, int(fs / chunk * seconds) * 100):
    data = stream.read(chunk)
    if sys.byteorder == "big":
        data = audioop.byteswap(data, p.get_sample_size(sample_format))
    interpretted = memoryview(data).cast("B")
    window.extend(interpretted)

    while len(window) > int(fs * seconds):
        window.popleft()

    if len(window) == int(fs * seconds):
        magic(window)


# Stop and close the stream
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()

print("Finished recording")

# Save the recorded data as a WAV file
