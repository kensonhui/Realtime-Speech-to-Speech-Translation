import json
import pickle
import pyaudio
import os
import socket
import select
import sys
import torch
import threading
from models.speech_recognition import SpeechRecognitionModel
from models.text_to_speech import TextToSpeechModel
from queue import Queue
from typing import Dict
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
        
        # String that holds the last completed phrase, we feed this into texttospeech
        self.last_phrase = ""
        # Initialize the transcriber model
        self.transcriber = SpeechRecognitionModel(data_queue=self.data_queue, 
                                                  callback=self.handle_transcription)
        self.text_to_speech = TextToSpeechModel(callback_function=self.handle_synthesize)
        self.text_to_speech.load_speaker_embeddings()
        self.read_list = []


    def __del__(self):
        self.audio.terminate()
        self.transcriber.stop()
        self.serversocket.close()
        

    def handle_transcription(self, packet: Dict):
        if packet["add"]:
            self.text_to_speech.synthesise(self.last_phrase)
            print(f"put {self.last_phrase} into queue")
        self.last_phrase = packet["text"]
    
    def handle_synthesize(self, audio: torch.Tensor):
        print("got audio")
        self.stream_numpy_array_audio(audio)

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
        
    def stream_numpy_array_audio(self, audio):
        # TODO: Make this asyncronhous
        for i in range(0, len(audio), self.CHUNK):
            chunk = audio[i:i + self.CHUNK]
            self.read_list[1].send(chunk.tobytes())

if __name__ == "__main__":
    server = AudioSocketServer()
    server.start()