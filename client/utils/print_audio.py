import numpy as np

def get_volume_norm(indata):
    return np.linalg.norm(indata)

def print_sound(volume_norm, blocks=10):
    """"""
    print("\rOutput microphone:" + " " * 50, end="", flush=True)  # Clears the line
    print("\rOutput microphone:" + "\u2588" * int(volume_norm * blocks), end="", flush=True)