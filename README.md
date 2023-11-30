# Speech To Text To Speech Translation

### Server Installation Instructions:

Make sure your XCode CLI tools are fully updated!
https://developer.apple.com/forums/thread/677124

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

Install Jupyter and Pylance extensions on VSCode.

Enjoy 😎😎😎😎😎😎😎

### Client Installation

Install Jack either via tar or brew
https://jackaudio.org/downloads/
or
```brew install jack``` 

Install requirements.txt in the clients folder
```pip install -r requirements.txt```


## speech.ipynb

Audiofile -> Translates to english text with whisper -> Create a synthesized voice with MS T5 TTS

## transcribe.ipynb

Microphone -> Transcribe to english text

## speech-to-transcribe

Microphone -> Translate and transcribe to english text