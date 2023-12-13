""" Server for real-time translation and voice synthesization """
from typing import Dict
from queue import Queue
import select
import socket
import pyaudio
import torch
from models.speech_recognition import SpeechRecognitionModel
from models.text_to_speech import TextToSpeechModel
class AudioSocketServer:
    """ Class that handles real-time translation and voice synthesization
        Socket input -> SpeechRecognition -> text -> TextToSpeech -> Socket output
    """
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    PORT = 4444
    # Number of unaccepted connections before server refuses new connections.
    #   For socket.listen()
    BACKLOG = 5
    def __init__(self, whisper_model):
        self.audio = pyaudio.PyAudio()
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Let kernel know we want to reuse the same port for restarting the server
        #   in quick succession
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        # TODO: For multiple concurrent users we will need more queues
        #   for now we only want one user to work first
        self.data_queue : Queue = Queue()

        # Initialize the transcriber model
        self.transcriber = SpeechRecognitionModel(model_name=whisper_model,
                                                  data_queue=self.data_queue,
                                                  generation_callback=self.handle_generation,
                                                  final_callback=self.handle_transcription)
        self.text_to_speech = TextToSpeechModel(callback_function=self.handle_synthesize)
        self.text_to_speech.load_speaker_embeddings()
        self.read_list = []

    def __del__(self):
        self.audio.terminate()
        self.transcriber.stop()
        self.serversocket.shutdown()
        self.serversocket.close()
    def handle_generation(self, packet: Dict):
        """ Placeholder function for transcription"""
    def handle_transcription(self, packet: str, client_socket):
        """ Callback function to put finalized transcriptions into TTS"""
        print(f"Added {packet} to synthesize task queue")
        self.text_to_speech.synthesise(packet, client_socket)
    def handle_synthesize(self, audio: torch.Tensor, client_socket):
        """ Callback function to stream audio back to the client"""
        self.stream_numpy_array_audio(audio, client_socket)

    def start(self):
        """ Starts the server"""
        self.transcriber.start(16000, 2)
        print(f"Listening on port {self.PORT}")
        self.serversocket.bind(('', self.PORT))
        self.serversocket.listen(self.BACKLOG)
        # Contains all of the socket connections, the first is the server socket for listening to
        #   new connections. All other ones are for individual clients sending data.
        self.read_list = [self.serversocket]

        try:
            while True:
                readable, _, _ = select.select(self.read_list, [], [])
                for s in readable:
                    if s is self.serversocket:
                        (clientsocket, address) = self.serversocket.accept()
                        self.read_list.append(clientsocket)
                        print("Connection from", address)
                    else:
                        try:
                            data = s.recv(4096)

                            if data:
                                self.data_queue.put((s, data))
                            else:
                                self.read_list.remove(s)
                                print("Disconnection from", address)
                        except ConnectionResetError:
                            self.read_list.remove(s)
                            print("Client crashed from", address)
        except KeyboardInterrupt:
            pass
        print("Performing server cleanup")
        self.audio.terminate()
        self.transcriber.stop()
        self.serversocket.shutdown(socket.SHUT_RDWR)
        self.serversocket.close()
        print("Sockets cleaned up")
    def stream_numpy_array_audio(self, audio, client_socket):
        """ Streams audio back to the client"""
        try:
            client_socket.sendall(audio.numpy().tobytes())
        except ConnectionResetError as e:
            print(f"Error sending audio to client: {e}")
            if client_socket in self.read_list:
                self.read_list.remove(client_socket)

if __name__ == "__main__":
    server = AudioSocketServer(whisper_model="base")
    server.start()
    