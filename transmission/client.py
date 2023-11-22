import pyaudio
import socket
import sys
import speech_recognition as sr

class AudioSocketClient:
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = 1000
        # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
        self.recorder.dynamic_energy_threshold = False
        
        # If you're on Linux you'll need to actually list the microphone devices
        #   here I'm being lazy
        self.source = sr.Microphone(sample_rate=16000)
        
        print(f"Sample rate {self.source.SAMPLE_RATE}, Sample Width {self.source.SAMPLE_WIDTH}")
        
    def __del__(self):
        # Destroy Audio resources
        
        print('Shutting down')

    # Callback function for microphone input, fires when there is new data from the microphone
    def record_callback(self, _, audio: sr.AudioData):
        data = audio.get_raw_data()
        print(data)
        # Sends data through the socket
        self.socket.send(data)
        
    
    # Starts the event loop
    def start(self, ip, port):
        # TODO: Seperate this out as thread based process
        
        # Connect to server
        self.socket.connect((ip, port))
        
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        
        # Start microphone
        self.recorder.listen_in_background(self.source, 
                                           self.record_callback,
                                           phrase_time_limit=2)
         ## Open audio as input from microphone
        print("Started recording...")
        
        try:
            while True:
                # This is where we will receive data from the server
                data = self.socket.recv(self.CHUNK)
                print(data)
        except KeyboardInterrupt:
            pass
        
        print("Finished recording")
        
        # Close Socket Connection
        self.socket.close()
        
        
client = AudioSocketClient()
client.start('127.0.0.1', 4444)