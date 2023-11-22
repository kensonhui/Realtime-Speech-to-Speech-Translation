import pyaudio
import socket
import sys

class AudioSocketClient:
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio = pyaudio.PyAudio()
        
    def __del__(self):
        # Destroy Audio resources
        self.audio.terminate()
        
        print('Shutting down')

    # Callback function for microphone input, fires when there is new data from the microphone
    def send_data_callback(self, in_data, frame_count, time_info, status):
        # Sends data through the socket
        self.socket.send(in_data)
        
        return (None, pyaudio.paContinue)
    
    # Starts the event loop
    def start(self, ip, port):
        # TODO: Seperate this out as thread based process
        
        # Connect to server
        self.socket.connect((ip, port))
        
        # Start microphone
        self.stream = self.audio.open(format=self.FORMAT, 
                                      channels=self.CHANNELS, 
                                      rate=self.RATE, input=True, 
                                      frames_per_buffer=self.CHUNK, 
                                      stream_callback=self.send_data_callback)
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
        # Close Microphone
        self.stream.close()
        
        
client = AudioSocketClient()
client.start('127.0.0.1', 4444)