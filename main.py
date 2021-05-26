import requests
from collections import deque
import pyaudio
import sys
from statistics import mean, stdev, variance
import numpy as np
import os
import atexit
import time
import json
import base64
from panelController import bassLight, rainbowLight, panels
from cfg import strip

CHUNK_SIZE = 1024
GPIO_CHANNELS = 8
POLYNOMIAL = 8
SAMPLE_FORMAT = pyaudio.paInt16
MIN_FREQUENCY = 20
MAX_FREQUENCY = 15000
MUSIC_START_THRESHOLD = 2
MUSIC_END_THRESHOLD = 2
ON_OFF_THRESHOLD = 35.0

channels = 2
fs = 44100  # Record at 44100 samples per second
sample_rate = 44100
seconds = 0.01

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
    print(values)
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
            + 1.0
        )

    return np.rint(matrix)


startTime = time.time()
endTime = time.time()


def isMusicPlaying(values):
    global startTime, endTime
    avg = np.mean(values)
    now = time.time()
    if avg > ON_OFF_THRESHOLD:
        if startTime + MUSIC_START_THRESHOLD < now:
            endTime = now
            return True
        else:
            return False
    else:
        if endTime + MUSIC_END_THRESHOLD < now:
            startTime = now
            return False
        else:
            return True


BASS_SAMPLES = 100
BASS_OUTPUT_SAMPLES = 4
bassWindow = deque([35.0] * BASS_SAMPLES)
bassAvg = 35.0
smoothingWindow = deque([35.0] * BASS_OUTPUT_SAMPLES)
BASS_TRESHOLD = 4.0
BASS_STD_TRESHOLD = 25.0


def bassline(values):
    global bassAvg, bassWindow
    new = values[0] + values[1]
    bassWindow.append(new)
    out = bassWindow.popleft()
    bassAvg = bassAvg + ((new - out) / BASS_SAMPLES)

    smoothingWindow.append(new - bassAvg)
    smoothingWindow.popleft()

    # print(variance(smoothingWindow), mean(smoothingWindow))
    if variance(smoothingWindow) > BASS_STD_TRESHOLD and mean(smoothingWindow) > 0.0:
        return True

    return False


class SongClassifier:
    SAMPLE_SIZE = 100
    samples = deque()
    songData = None

    def reset(self):
        self.samples.clear()
        self.songData = None

    def sample(self, data):
        self.samples.append(data)
        if len(self.samples) > self.SAMPLE_SIZE:
            self.samples.popleft()
            self.classify()

    def getGenre(self):
        try:
            if self.songData:
                return self.songData["track"]["genres"]["primary"]
            else:
                return ""
        except:
            return ""

    def classify(self):
        print("classifiying song")

        values = bytearray()

        for i in self.samples:
            values.extend(i)

        base64EncodedStr = base64.b64encode(values)
        url = "https://shazam.p.rapidapi.com/songs/detect"
        payload = base64EncodedStr
        headers = {
            "content-type": "text/plain",
            "x-rapidapi-key": "f42136d023msh1c820c2920202f4p1b5b4ajsnc04e9452c380",
            "x-rapidapi-host": "shazam.p.rapidapi.com",
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        self.songData = json.loads(response.text)


TIMING_SAMPLES = 100
timingSmoother = deque([0.01] * TIMING_SAMPLES)
timingAverage = 0.01


def measureTiming(start, end):
    global timingSmoother, timingAverage
    new = end - start
    timingSmoother.append(new)
    old = timingSmoother.popleft()
    timingAverage = timingAverage - (old / TIMING_SAMPLES)
    timingAverage = timingAverage + (new / TIMING_SAMPLES)
    return timingAverage


def exit():
    stream.stop_stream()
    stream.close()
    p.terminate()  # Terminate the PortAudio interface
    print("Finished recording")


atexit.register(exit)

frequency_limits = calculate_channel_frequency()


sc = SongClassifier()
nowPlaying = False
basslineDidHit = True
mode = "rainbow"
idx = 0


while True:
    cycleStart = time.time()

    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
    if sys.byteorder == "big":
        data = audioop.byteswap(data, p.get_sample_size(SAMPLE_FORMAT))

    casted = np.asarray(memoryview(data).cast("B"))
    values = equalizer(casted)

    # os.system("clear")
    nowPlaying = isMusicPlaying(values)
    basslineDidHit = bassline(values)
    currentSongGenre = sc.getGenre()

    # if basslineDidHit:
    #     print("Boom")
    # else:
    #     print("-")

    # if nowPlaying:
    #     print("Now Playing")
    #     # sc.sample(data)

    # display(values)

    # if nowPlaying:
    #     bassLight(basslineDidHit)

    bassLight(basslineDidHit)

    for i in panels:
        i.update()

    strip.show()
    # timer
    cycleEnd = time.time()
    print(measureTiming(cycleStart, cycleEnd))
