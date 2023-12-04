from models.text_to_speech import TextToSpeechModel
import threading

text_to_speech_tests = [
    "Hello there",
    "What's the deal with airplane food?",
    "I love cheese"
]

def handle_speech(audio):
    print("Received audio")

tts_model = TextToSpeechModel(callback_function=handle_speech)
tts_model.load_speaker_embeddings()

print("Beginning tests")
for text in text_to_speech_tests:
    tts_model.synthesise(text)

event = threading.Event().wait()