import pyaudio
import socket
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((sys.argv[1], int(sys.argv[2])))
audio = pyaudio.PyAudio()

# Callback function for microphone input
def callback(in_data, frame_count, time_info, status):
    # Fires when there is new data from the microphone
    
    # Sends data through the socket
    s.send(in_data)
    
    return (None, pyaudio.paContinue)

## Open audio as input from microphone
print("recording...")
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)

try:
    while True:
        data = s.recv(CHUNK)
        print(data)
except KeyboardInterrupt:
    pass

print('Shutting down')
s.close()
stream.close()
audio.terminate()