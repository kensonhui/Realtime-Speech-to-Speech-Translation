import torch
import whisper
from queue import Queue
import speech_recognition as sr
import io
import time
import soundfile as sf
from datetime import datetime, timedelta
import threading

class SpeechRecognitionModel:    
    def __init__(self, data_queue, generation_callback=lambda *args: None, final_callback=lambda *args: None, model_name="base"):
        # The last time a recording was retrieved from the queue.
        self.phrase_time = None
        # Current raw audio bytes.
        self.last_sample = bytes()
        # Thread safe Queue for passing data from the threaded recording callback.
        self.data_queue : Queue = data_queue
        # Callback to get real-time transcription results
        self.generation_callback = generation_callback
        # Callback for final transcription results
        self.final_callback = final_callback
        # How much empty space between recordings before new lines in transcriptions
        self.phrase_timeout = 0.5

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Loading model whisper-{model_name} on {self.device}")
        self.audio_model = whisper.load_model(model_name, device=self.device)
        self.thread = None
        self._kill_thread = False

        self.recent_transcription = ""

    def start(self, sample_rate, sample_width):
        self.thread = threading.Thread(target=self.__worker__, args=(sample_rate, sample_width))
        self._kill_thread = False
        self.thread.start()

    def stop(self):
        self._kill_thread = True
        if self.thread:
            self.thread.join()
            self.thread = None

    def __worker__(self, sample_rate, sample_width):
        while not self._kill_thread:
            now = datetime.utcnow()
            phrase_complete = self.__update_phrase_time__(now)
            if not self.data_queue.empty():
                self.__concatenate_new_audio__()
                self.__transcribe_audio__(sample_rate, sample_width, phrase_complete)
            time.sleep(0.05)

    def __update_phrase_time__(self, current_time):
        phrase_complete = False
        # If enough time has passed between recordings, consider the phrase complete.
        #   Clear the current working audio buffer to start over with the new data.
        if self.phrase_time and current_time - self.phrase_time > timedelta(seconds=self.phrase_timeout):
            if self.recent_transcription:
                self.final_callback(self.recent_transcription)
                self.recent_transcription = ""
            self.last_sample = bytes()
            phrase_complete = True
        self.phrase_time = current_time
        return phrase_complete

    def __concatenate_new_audio__(self):
        while not self.data_queue.empty():
            data = self.data_queue.get()
            self.last_sample += data

    def __transcribe_audio__(self, sample_rate, sample_width, phrase_complete):
        try:
            audio_data = sr.AudioData(self.last_sample, sample_rate, sample_width)
            wav_data = io.BytesIO(audio_data.get_wav_data())
            with sf.SoundFile(wav_data, mode='r') as sound_file:
                audio = sound_file.read(dtype='float32')
                start_time = time.time()
                result = self.audio_model.transcribe(audio, fp16=torch.cuda.is_available())
                end_time = time.time()

            text = result['text'].strip()
            if text:
                self.generation_callback({"add": phrase_complete, "text": text, "transcribe_time": end_time - start_time})
                if phrase_complete:
                    self.final_callback(self.recent_transcription)
                self.recent_transcription = text
        except Exception as e:
            print(f"Error during transcription: {e}")

    def __del__(self):
        self.stop()
