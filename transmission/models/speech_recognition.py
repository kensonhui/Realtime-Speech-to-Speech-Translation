# Adapted from whisper_real_time https://github.com/davabase/whisper_real_time
import torch
from transformers import pipeline
from pyaudio import PyAudio
import torch
import whisper
from queue import Queue
from tempfile import NamedTemporaryFile
import speech_recognition as sr
import io
import os
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
import time
from sys import platform
import threading

class SpeechRecognitionModel:    
    def __init__(self, data_queue, callback=None, model_name = "base"):
        # The last time a recording was retrieved from the queue.
        self.phrase_time = None
        # Current raw audio bytes.
        self.last_sample = bytes()
        # Thread safe Queue for passing data from the threaded recording callback.
        self.data_queue = data_queue

        self.callback = callback
       
        # How real the recording is in seconds.
        self.record_timeout = 2
        # How much empty space between recordings before new lines in transcriptions
        self.phrase_timeout = 3
        
        self.temp_file = NamedTemporaryFile().name
        self.transcription = ['']
        
        print(f"Loading model whisper-{model_name}")
        self.audio_model = whisper.load_model(model_name)
        print("Finished loading model")
        self.thread = None
        self._kill_thread = False
    
    def __del__(self):
        self.__kill_worker__()
    
    def stop(self):
        self.__kill_worker__()

    def start(self, SAMPLE_RATE, SAMPLE_WIDTH):
        self.thread = threading.Thread(
            target=self.__worker__,
            args=(SAMPLE_RATE, SAMPLE_WIDTH)
            )
        self._kill_thread = False
        self.thread.start()
        print("Finished starting thread")
        
    def __kill_worker__(self):
        self._kill_thread = True
        self.thread.join()
        self.thread = None
        
    def __worker__(self, SAMPLE_RATE, SAMPLE_WIDTH):
        # Do not call this method directly!!! You will block the main thread
        while True:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not self.data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                    self.last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                self.phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not self.data_queue.empty():
                    data = self.data_queue.get()
                    self.last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(self.last_sample, SAMPLE_RATE, SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                with open(self.temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                # Read the transcription.
                result = self.audio_model.transcribe(self.temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                if phrase_complete:
                    self.transcription.append(text)
                else:
                    self.transcription[-1] = text

                # TODO: make the callback take in the most recent line and not the entire transcription
                self.callback({ "add": phrase_complete, "text": text})

                # Infinite loops are bad for processors, must sleep.
            time.sleep(0.25)
            if self._kill_thread:
                break

        print("\n\nTranscription:")
        for line in self.transcription:
            print(line)