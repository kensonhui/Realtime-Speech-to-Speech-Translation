import numpy as np

def convert_and_normalize(audio_data_int16):
    """
    Converts an int16 numpy array to float32 and normalizes it to the range -1.0 to 1.0.

    Parameters:
    audio_data_int16 (numpy.ndarray): The int16 audio data to convert.

    Returns:
    numpy.ndarray: The converted and normalized float32 audio data.
    """
    # Convert to float32
    audio_data_float32 = audio_data_int16.astype(np.float32)

    # Normalize the data to the range -1.0 to 1.0
    max_int16 = np.iinfo(np.int16).max
    audio_data_float32 /= max_int16

    return audio_data_float32


def get_volume_norm(indata: np.ndarray):
    return np.sqrt(np.mean(np.square(indata))) * 20

def print_sound(input_volume, output_volume, blocks=10):
    """"""
    print("\rInput microphone:" + " " * blocks * 3 + 
          "\rInput microphone:" + "\u2588" * int(input_volume * blocks) + "\n" +
          "\rOutput microphone:" + " " * blocks * 3 +
          "\rOutput microphone:" + "\u2588" * int(output_volume * blocks) + "\033[A", end="", flush=True)