import pyaudio
import socket
import select
from models.speech_recognition import SpeechRecognitionModel
from queue import Queue

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
        # Initialize the transcriber model
        self.transcriber = SpeechRecognitionModel(data_queue=self.data_queue)
        
    def __del__(self):
        self.audio.terminate()
        self.transcriber.stop()
        
    def start(self):
        print("Start transcriber")
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
                        self.data_queue.put(data) 
                        # stream.write(data)
                        if not data:
                            self.read_list.remove(s)
                            print("Disconnection from", address)
        except KeyboardInterrupt:
            pass

        self.serversocket.close()

server = AudioSocketServer()
server.start()