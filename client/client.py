"""Client for live speech to speech translation"""
import logging
import socket
import time
import threading
from datetime import datetime, timezone
import speech_recognition as sr
import numpy as np
import sounddevice as sd
from utils.print_audio import print_sound, get_volume_norm, convert_and_normalize

class AudioSocketClient:
    """ Client for recording audio, streaming it to the server via sockets, receiving
    the data and then piping it to an output audio device """
    CHANNELS = 1
    RATE = 16000
    CHUNK = 4096
    # Used for Speech Recognition library - set this higher for non-English languages
    PHRASE_TIME_LIMIT = 2
    # How long you need to stop speaking to be considered an entire phrase
    PAUSE_THRESHOLD = 0.5
    # Volume for the microphone
    RECORDER_ENERGY_THRESHOLD = 1000
    def __init__(self) -> None:
        # Prompt the user to select their devices
        self.input_device_index, self.output_device_index = sd.default.device
        print(sd.query_devices())
        print(f"Using input index of: {self.input_device_index}\noutput index of: {self.output_device_index}.")
        if input(" Is this correct?\n y/[n]: ") != "y":
            self.input_device_index = int(input("Type the index of the physical microphone: "))
            self.output_device_index = int(input("Type the index of the output microphone: "))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = self.RECORDER_ENERGY_THRESHOLD
        """Definitely do this, dynamic energy compensation lowers the energy threshold dramatically 
            to a point where the SpeechRecognizer never stops recording."""
        self.recorder.dynamic_energy_threshold = False
        self.recorder.pause_threshold = self.PAUSE_THRESHOLD
        self.source = sr.Microphone(device_index=self.input_device_index, sample_rate=self.RATE)
        self.transcription = [""]
        ### Debugging variables
        self.time_last_sent = None
        self.time_first_received = None
        self.time_last_received = None
        self.volume_input = 0
        self.volume_output = 0
        # How much time since the last received packet to refresh the flush
        self.time_flush_received = 2
        threading.Thread(target=self.__debug_worker__, daemon=True).start()
    def __del__(self):
        # Destroy Audio resources
        print('Shutting down')

    def record_callback(self, _, audio: sr.AudioData):
        """ Callback function for microphone input, 
            fires when there is new data from the microphone """
        data = audio.get_raw_data()
        self.time_last_sent = time.time()
        logging.debug("send audio data %f", self.time_last_sent)
        self.socket.send(data)
        # convert to np array for volume
        self.volume_input = get_volume_norm(
            convert_and_normalize(np.frombuffer(data, dtype=np.int16))
        )
    def start(self, ip, port):
        """ Starts the client service """
        # Connect to server
        print(f"Attempting to connect to IP {ip}, port {port}")
        self.socket.connect((ip, port))
        print(f"Successfully connected to IP {ip}, port {port}")
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        # Start microphone
        self.recorder.listen_in_background(self.source,
                                           self.record_callback,
                                           phrase_time_limit=None)
         ## Open audio as input from microphone
        print('''Listening now...\nNote: The input microphone records
              in very large packets, so the volume meter won't move as much.''')
        self.volume_print_worker = threading.Thread(target=self.__volume_print_worker__,
                                                    daemon=True)
        self.volume_print_worker.start()
        with sd.OutputStream(samplerate=self.RATE,
                    channels=1,
                    dtype=np.float32,
                    device=self.output_device_index,
                    ) as audio_output:
            try:
                while True:
                    # This is where we will receive data from the server
                    packet = self.socket.recv(self.CHUNK)
                    if packet:
                        audio_chunk = np.frombuffer(packet, dtype=np.float32)
                        self.time_last_received = time.time()
                        if not self.time_first_received:
                            logging.debug("First audio packet - time: %f",
                                          self.time_last_received - self.time_last_sent)
                            self.time_first_received = self.time_last_received
                        # Speech T5 Output always has a sample rate of 16000
                        audio_output.write(audio_chunk)
                        self.volume_output = get_volume_norm(audio_chunk)
            except ConnectionResetError:
                print("Server connection reset - shutting down client")
            except KeyboardInterrupt:
                print("Received keyboard input - shutting down")
        # Close Socket Connection
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
    def __volume_print_worker__(self):
        """ Event loop for worker to continually update the terminal volume meter"""
        last_volume_input = 0
        last_volume_output = 0
        print_sound(0, 0, blocks=10)
        while True:
            if abs(last_volume_input - self.volume_input) > 0.1 or abs(last_volume_output - self.volume_output) > 0.1:
                print_sound(self.volume_input, self.volume_output, blocks=10)
                last_volume_input = self.volume_input
                last_volume_output = self.volume_output
            if self.time_last_sent and time.time() - self.time_last_sent > self.PHRASE_TIME_LIMIT:
                self.volume_input = 0
            time.sleep(0.1)
    def __debug_worker__(self):
        """Background worker to handle debug statements"""
        print("Started background debug worker")
        while True:
            if not self.time_last_sent:
                # We can let the processor sleep more
                time.sleep(1)
                continue
            if not self.time_last_received:
                # Data has been sent, waiting on receiving
                time.sleep(0.05)
                continue
            if time.time() - self.time_last_received > self.time_flush_received:
                logging.debug("Last audio packet - time: %f",
                              self.time_last_received - self.time_last_sent)
                self.time_last_received = None
                self.time_first_received = None

if __name__ == "__main__":
    date_str = datetime.now(timezone.utc)
    logging.basicConfig(filename=f"logs/{date_str}-output.log",
                        encoding='utf-8',
                        level=logging.DEBUG)
    # Hide cursor in terminal:
    print('\033[?25l', end="")
    # Start server
    client = AudioSocketClient()
    client.start('172.174.109.109', 4444)
    # Show cursor again:
    print('\033[?25h', end="")
