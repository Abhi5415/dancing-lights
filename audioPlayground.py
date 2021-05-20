from collections import deque
import matplotlib.pyplot as plt
import pyaudio
import wave
from scipy.io import wavfile # get the api
from scipy.fftpack import fft


chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
seconds = 3
filename = "output.wav"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print('Recording')

def save(window):
  print("saving")
  wf = wave.open(filename, 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(p.get_sample_size(sample_format))
  wf.setframerate(fs)
  wf.writeframes(b''.join(window))
  wf.close()

stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)

window = deque()  # Initialize array to store frames

# Store data in chunks for 3 seconds

for i in range(0, int(fs / chunk * seconds)):
  data = stream.read(chunk)
  window.append(data)

  # if len(window) > int(fs / chunk * seconds):
  #   window.popleft()
save(window)

# Stop and close the stream 
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()

print('Finished recording')

# Save the recorded data as a WAV file
