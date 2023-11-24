import pyaudio
import socket
import sys
import speech_recognition as sr
import os
import json

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
        
        self.transcription = [""]
        
    def __del__(self):
        # Destroy Audio resources
        
        print('Shutting down')

    # Callback function for microphone input, fires when there is new data from the microphone
    def record_callback(self, _, audio: sr.AudioData):
        data = audio.get_raw_data()
        # print(data)
        # Sends data through the socket
        self.socket.send(data)
        
    
    # Starts the event loop
    def start(self, ip, port):
        # TODO: Seperate this out as thread based process
        
        # Connect to server
        print(f"Attempting to connect to IP {ip}, port {port}")
        self.socket.connect((ip, port))
        print(f"Successfully connected to IP {ip}, port {port}")
        
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
                transcription_bytes = self.socket.recv(self.CHUNK).decode('utf-8')
                packet = json.loads(transcription_bytes)
                if packet["add"]:
                    self.transcription.append(packet["text"])
                else:
                    self.transcription[-1] = packet["text"]
                    
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"Transcribed from IP {ip}, port {port}")
                print(f"Sample rate {self.source.SAMPLE_RATE}, Sample Width {self.source.SAMPLE_WIDTH}")
                for line in self.transcription:
                    print(line)
                # Flush stdout.
                print('', end='', flush=True)
        except KeyboardInterrupt:
            pass
        
        print("Finished recording")
        print("\n\nTranscription:")
        for line in self.transcription:
            print(line)
        
        # Close Socket Connection
        self.socket.close()
        
        
client = AudioSocketClient()
client.start('127.0.0.1', 4444)