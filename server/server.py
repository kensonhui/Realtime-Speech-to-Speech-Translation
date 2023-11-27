import pyaudio
import socket
import select
from models.speech_recognition import SpeechRecognitionModel
from queue import Queue
import os
from typing import Dict
import json

class AudioSocketServer:
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    
    PORT = 4444
    # Number of unaccepted connections before server refuses new connections. 
    #   For socket.listen()
    BACKLOG = 5 
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: For multiple concurrent users we will need more queues
        #   for now we only want one user to work first
        self.data_queue = Queue()
        self.transcription = ""
        # Initialize the transcriber model
        self.transcriber = SpeechRecognitionModel(data_queue=self.data_queue, callback=self.handle_transcription)
        self.read_list = []


    def __del__(self):
        self.audio.terminate()
        self.transcriber.stop()
        

    def handle_transcription(self, packet: Dict):
        # Convert to compact JSON format string
        compact_json_encoding = json.dumps(packet, separators=(',', ':'))
        # Then encode to utf-8
        transcription_bytes = compact_json_encoding.encode('utf-8')
        ## TODO: We're going to have to fix this so it is not hard coded to be the first one
        self.read_list[1].sendall(transcription_bytes)


    def start(self):
        self.transcriber.start(16000, 2)
        print(f"Listening on port {self.PORT}")
        self.serversocket.bind(('', self.PORT))
        self.serversocket.listen(self.BACKLOG)
        
        # Contains all of the socket connections, the first is the server socket for listening to
        #   new connections. All other ones are for individual clients sending data.
        self.read_list = [self.serversocket]

        try:
            while True:
                readable, writable, errored = select.select(self.read_list, [], [])
                for s in readable:
                    if s is self.serversocket:
                        (clientsocket, address) = self.serversocket.accept()
                        self.read_list.append(clientsocket)
                        print("Connection from", address)
                    else:
                        data = s.recv(1024)

                        if data:
                            self.data_queue.put(data) 
                        else:
                            self.read_list.remove(s)
                            print("Disconnection from", address)
        except KeyboardInterrupt:
            pass

        self.transcriber.stop()
        self.serversocket.close()

if __name__ == "__main__":
    server = AudioSocketServer()
    server.start()