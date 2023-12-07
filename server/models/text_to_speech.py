import torch
import time
import threading
from datasets import load_dataset
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from queue import Queue

class TextToSpeechModel:
    def __init__(self, callback_function):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Device used for TextToSpeech: {self.device}")
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts",
                                                           normalize=True)

        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        
        self.model.to(self.device)
        self.vocoder.to(self.device)
        
        # List of tuple of (text, callback_function)
        self.task_queue = Queue()
        self.callback_function = callback_function
        
        # Run in daemon so it self exits
        self.__kill_thread = False
        self.thread = threading.Thread(target=self.worker, daemon=True).start()
    
    def __deL__(self):
        self.__kill_thread = True
        self.thread.join()

    def load_speaker_embeddings(self):
        self.speaker_embeddings = torch.load('models/emma_embeddings.pt')
        self.speaker_embeddings = self.speaker_embeddings.squeeze(1)

    
    def synthesise(self, text, client_socket):
        # Call load_speaker_embeddings before generating
        if self.speaker_embeddings is None:
            raise Exception("TextToSpeech: Load speaker embeddings before synthesizing")
        task = (client_socket, text)
        self.task_queue.put(task)
        
    # Don't call this code directly!
    def worker(self):
        # TODO: Processor running in loop, best if we do a timeout
        while not self.__kill_thread:
            if not self.task_queue.empty():
                client, text = self.task_queue.get()
                
                inputs = self.processor(text=text, return_tensors="pt")
                start_time = time.time()
                speech = self.model.generate_speech(
                    inputs["input_ids"].to(self.device), 
                    self.speaker_embeddings.to(self.device), 
                    vocoder=self.vocoder
                )
                end_time = time.time()
                print(f"synthesize : {text}. Time: {end_time - start_time}")
                self.callback_function(speech.cpu(), client)
                self.task_queue.task_done()
            time.sleep(0.05)
        