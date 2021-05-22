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
from statistics import mean, stdev
import numpy as np
import os
import atexit
import time


CHUNK_SIZE = 1024
GPIO_CHANNELS = 8
POLYNOMIAL = 8
SAMPLE_FORMAT = pyaudio.paInt16
MIN_FREQUENCY = 20
MAX_FREQUENCY = 15000
MUSIC_START_THRESHOLD = 2
MUSIC_END_THRESHOLD = 2
ON_OFF_THRESHOLD = 30

channels = 1
fs = 44100  # Record at 44100 samples per second
sample_rate = 44100
seconds = 0.1

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print("Recording")
stream = p.open(
    format=SAMPLE_FORMAT,
    channels=channels,
    rate=fs,
    frames_per_buffer=CHUNK_SIZE,
    input=True,
)


def display(values):

    for i in values:
        if i != float("-inf"):
            print("".join((["-"] * int(i))))
        else:
            print("-")


def calculate_channel_frequency():

    octaves = (np.log(MAX_FREQUENCY / MIN_FREQUENCY)) / np.log(2)
    octaves_per_channel = octaves / GPIO_CHANNELS
    frequency_limits = []
    frequency_store = []

    frequency_limits.append(MIN_FREQUENCY)
    for i in range(1, GPIO_CHANNELS + 1):
        frequency_limits.append(frequency_limits[-1] * 2 ** octaves_per_channel)
    for i in range(0, GPIO_CHANNELS):
        frequency_store.append((frequency_limits[i], frequency_limits[i + 1]))
    return frequency_store


def piff(val, sample_rate):
    """Return the power array index corresponding to a particular frequency."""
    return int(CHUNK_SIZE * val / sample_rate)


def equalizer(castedData):
    data = np.frombuffer(castedData, dtype=np.int16)
    window = np.hanning(len(data))
    data = data * window
    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)
    power = np.abs(fourier) ** POLYNOMIAL
    matrix = [0 for i in range(GPIO_CHANNELS)]
    for i in range(GPIO_CHANNELS):
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


startTime = time.time()
endTime = time.time()
def isMusicPlaying(values):
    global startTime, endTime
    avg = np.mean(values)
    now = time.time()
    if avg > ON_OFF_THRESHOLD:
        if startTime +  MUSIC_START_THRESHOLD < now:
            endTime = now
            return True
        else:
            return False
    else: 
        if endTime +  MUSIC_END_THRESHOLD < now:
            startTime = now
            return False
        else:
            return True


bassWindow = deque([35.0] * 512)
smoothingWindow = deque([False] * 5)
def bassline(values):
    prev = mean(bassWindow)
    new = values[0] + values [1]
    bassWindow.append(new)
    bassWindow.popleft()
    if (new - 4.0 > prev):
        smoothingWindow.append(True)
    else: 
        smoothingWindow.append(False)
    smoothingWindow.popleft()
    
    res = True
    for i in smoothingWindow:
        res = i and res

    return res


TIMING_SAMPLES = 1000
timingSmoother = deque([0.01] * TIMING_SAMPLES)
timingAverage = 0.01
def measureTiming(start, end):
    global timingSmoother, timingAverage
    new = end - start
    timingSmoother.append(new)
    old = timingSmoother.popleft()
    timingAverage = timingAverage - (old/TIMING_SAMPLES)
    timingAverage = timingAverage + (new/TIMING_SAMPLES)
    return timingAverage

def exit():
    stream.stop_stream()
    stream.close()
    p.terminate()  # Terminate the PortAudio interface
    print("Finished recording")


atexit.register(exit)

frequency_limits = calculate_channel_frequency()


while True:

    cycleStart = time.time()

    data = stream.read(CHUNK_SIZE)
    if sys.byteorder == "big":
        data = audioop.byteswap(data, p.get_sample_size(SAMPLE_FORMAT))

    casted = np.asarray(memoryview(data).cast("B"))
    values = equalizer(casted)

    os.system("clear")
    if bassline(values):
        print("Boom")
    else:
        print("-")

    if isMusicPlaying(values):
        print("Now Playing")
    else:
        print("Waiting")
    print(values)

    display(values)

    cycleEnd = time.time()
    print(measureTiming(cycleStart, cycleEnd))