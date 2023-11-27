import torch
from datasets import load_dataset
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

class TextToSpeechModel:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")

        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        self.model.to(self.device)
        self.vocoder.to(self.device)
    
    def load_speaker_embeddings(self):
        # TODO: Load custom speaker embedding
        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
    
    def synthesise(self, text):
        # Call load_speaker_embeddings before generating
        if (self.speaker_embeddings is None):
            raise Exception("TextToSpeech: Load speaker embeddings before synthesizing")
        inputs = self.processor(text=text, return_tensors="pt")
        speech = self.model.generate_speech(
            inputs["input_ids"].to(self.device), 
            self.speaker_embeddings.to(self.device), 
            vocoder=self.vocoder
        )
        return speech.cpu()