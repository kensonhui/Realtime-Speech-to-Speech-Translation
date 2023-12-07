# Speech To Text To Speech Translation

This project handles local real-time audio to audio translation over sockets with OpenAI's Whisper and Microsoft SpeechT5 TTS. The project includes a client and server Python program.

Within the client, the user can pipe in the audio output to any virtual microphone or audio device they would like. 

### Server Installation Instructions:
#### These are all important steps!

Ensure your ports specified in server.py is open! Otherwise your socket connection will fail.

Make sure your XCode CLI or C++ compiler tools are fully updated!
https://developer.apple.com/forums/thread/677124

Install FFmpeg:
```sudo apt install ffmpeg```

Install Anaconda:
https://www.anaconda.com/download

Run the initialization command:
```conda init```

Make sure Conda is updated to the latest version:
```conda upgrade conda```

Create a virtual environment
```conda create -n "speech-to-speech" python==3.11```

```conda activate speech-to-speech```

Install Pytorch here:
https://pytorch.org/get-started/locally/

Install Librosa
```conda install -c conda-forge librosa```

Install Transformers:
```conda install -c huggingface transformers```

Install pyaudio:
```pip install pyaudio```

Install Project Packages:
```pip install -r requirements.txt```

Finally run the server:
```python server.py```

Enjoy 😎😎😎😎😎😎😎

### Client Installation

Install FFmpeg - you can do so with brew, or here: https://ffmpeg.org/download.html.
```brew install ffmpeg``` 

Install requirements.txt in the clients folder
```pip install -r requirements.txt```


## speech.ipynb

Audiofile -> Translates to english text with whisper -> Create a synthesized voice with MS T5 TTS

## transcribe.ipynb

Microphone -> Transcribe to english text

## speech-to-transcribe

Microphone -> Translate and transcribe to english text
