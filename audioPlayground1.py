from collections import deque
from functools import cache
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
import os

CHUNK_SIZE = 1024  # Record in chunks of 1024 samples
GPIO_CHANNELS = 8
POLYNOMIAL = 8
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
sample_rate = 44100


seconds = 0.2
filename = "output.wav"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print("Recording")

stream = p.open(
    format=sample_format,
    channels=channels,
    rate=fs,
    frames_per_buffer=CHUNK_SIZE,
    input=True,
)

off = 0.0

minAmp = [float("inf")] * 5
maxAmp = [-1.0] * 5


def display(data):
    os.system("clear")
    print(data)
    for i in data:
        print("".join((["-"] * int(i))))


def calculate_channel_frequency():
    min_frequency = 50
    max_frequency = 15000
    channel_length = GPIO_CHANNELS

    octaves = (np.log(max_frequency / min_frequency)) / np.log(2)
    octaves_per_channel = octaves / channel_length
    frequency_limits = []
    frequency_store = []

    frequency_limits.append(min_frequency)
    for i in range(1, GPIO_CHANNELS + 1):
        frequency_limits.append(frequency_limits[-1] * 2 ** octaves_per_channel)
    for i in range(0, channel_length):
        frequency_store.append((frequency_limits[i], frequency_limits[i + 1]))
    return frequency_store


frequency_limits = calculate_channel_frequency()

print(frequency_limits)

# Save the recorded data as a WAV file
def piff(val, sample_rate):
    """Return the power array index corresponding to a particular frequency."""
    return int(CHUNK_SIZE * val / sample_rate)


def fftransform(win):
    data = np.frombuffer(win, dtype=np.int16)
    # print(data)
    # data = np.empty(len(data) / 2)  # data has two channels and 2 bytes per channel
    window = np.hanning(len(data))
    data = data * window
    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)
    power = np.abs(fourier) ** POLYNOMIAL
    matrix = [0 for i in range(GPIO_CHANNELS)]
    for i in range(GPIO_CHANNELS):
        # take the log10 of the resulting sum to approximate how human ears perceive sound levels
        matrix[i] = np.log10(
            np.sum(
                power[
                    piff(frequency_limits[i][0], sample_rate) : piff(
                        frequency_limits[i][1], sample_rate
                    ) : 1
                ]
            )
        )

    return np.rint(matrix)


# def magic(data):
#     global minAmp, maxAmp
#     c = fft(data)
#     d = len(c) / 2
#     total = abs(c[: (int(d - 1))])
#     sub_bass = mean(total[16:60])
#     bass = mean(total[60:250])
#     low_mids = mean(total[250:2000])
#     hi_mids = mean(total[2000:4000])
#     presence = mean(total[4000:6000])

#     vals = [sub_bass, bass, low_mids, hi_mids, presence]

#     for i in range(5):
#         minAmp[i] = min(vals[i], minAmp[i])
#         maxAmp[i] = max(vals[i], maxAmp[i])

#     vals = [
#         int(((val - minAmp[idx]) / maxAmp[idx]) * 1000) for idx, val in enumerate(vals)
#     ]
#     sys.stdout.write("\r" + ", ".join(map(str, vals)))
#     sys.stdout.flush()


window = deque()  # Initialize array to store frames

# Store data in chunks for 3 seconds

for i in range(0, int(fs / CHUNK_SIZE * seconds) * 10000):
    data = stream.read(CHUNK_SIZE)
    if sys.byteorder == "big":
        data = audioop.byteswap(data, p.get_sample_size(sample_format))
    interpretted = memoryview(data).cast("B")
    window.extend(interpretted)

    while len(window) > int(fs * seconds):
        window.popleft()

    if len(window) == int(fs * seconds):
        display(fftransform(data))


# Stop and close the stream
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()

print("Finished recording")
