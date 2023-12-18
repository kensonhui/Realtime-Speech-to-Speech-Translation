# Speech To Text To Speech Translation

### Demo
[![Video Demonstration of Live Speech to Speech Translation](https://img.youtube.com/vi/yvikqjM8TeA/0.jpg)]([https://www.youtube.com/watch?v=yvikqjM8TeA](https://www.youtube.com/watch?v=yvikqjM8TeA))

This project handles local real-time audio to audio translation over sockets with OpenAI's Whisper and Microsoft SpeechT5 TTS. The project includes a client and server Python program, meaning that users can choose host the service on a high-performance GPU, then be able to use it on any consumer-level device.
![Screenshot 2023-12-13 at 10 05 56 AM](https://github.com/kensonhui/live-speech-to-text-to-speech/assets/60726802/02fc9af7-b0a8-4350-b763-af92431d5171)

Within the client, the user can pipe in the audio output to any virtual microphone or audio device they would like. One application is for video calls, the user can pipe the output to a virtual microphone, then use that audio device in a meeting so that everything they say is translated.

### Server Installation Instructions:
#### These are all important steps!

Ensure your ports specified in server.py is open! The default port we chose was 4444.

Make sure your XCode CLI or C++ compiler tools are fully updated!
https://developer.apple.com/forums/thread/677124

Install FFmpeg:
```sudo apt install ffmpeg```

Install Anaconda for your device:
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
```cd server```
```pip install -r requirements.txt```

Finally run the server:
```python server.py```

Enjoy 😎😎😎😎😎😎😎

### Client Installation
If you'd like to use the translation in a video call or such, you can install software to create a virtual microphone. On Mac you can use Blackhole.

Install FFmpeg - you can do so with brew, or here: https://ffmpeg.org/download.html.
```brew install ffmpeg``` 

Install requirements.txt in the clients folder
```pip install -r requirements.txt```

Finally run the client:
```python client.py```

### Notebooks for Testing

## speech.ipynb

Audiofile -> Translates to english text with whisper -> Create a synthesized voice with MS T5 TTS

## transcribe.ipynb

Microphone -> Transcribe to english text

## speech-to-transcribe

Microphone -> Translate and transcribe to english text
