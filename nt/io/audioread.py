"""
This module deals with all sorts of audio input and output.
"""
import inspect
import os
import tempfile
import wave
from io import BytesIO
from pathlib import Path

import numpy as np
import wavefile

import nt.utils.process_caller as pc

UTILS_DIR = os.path.join(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))), 'utils'
)


def audioread(path, offset=0.0, duration=None):
def audioread(path, offset=0.0, duration=None, sample_rate=None):
    """
    Reads a wav file, converts it to 32 bit float values and reshapes according
    to the number of channels.

    This function uses the `wavefile` module which in turn uses `libsndfile` to
    read an audio file. This is much faster than the previous version based on
    `librosa`, especially if one reads a short segment of a long audio file.

    .. note:: Contrary to the previous version, this one does not implicitly
        resample the audio if the `sample_rate` parameter differs from the
        actual sampling rate of the file. Instead, it raises an error.


    :param path: Absolute or relative file path to audio file.
    :type: String.
    :param offset: Begin of loaded audio.
    :type: Scalar in seconds.
    :param duration: Duration of loaded audio.
    :type: Scalar in seconds.
    :param sample_rate: (deprecated) Former audioread did implicit resampling
        when a different sample rate was given. This raises an error if the
        `sample_rate` does not match the files sampling rate. `None` accepts
        any rate.
    :type: scalar in number of samples per second
    :return:

    .. admonition:: Example:
        Only path provided:

        >>> path = '/net/speechdb/timit/pcm/train/dr1/fcjf0/sa1.wav'
        >>> signal = audioread(path)

        Say you load audio examples from a very long audio, you can provide a
        start position and a duration in seconds.

        >>> path = '/net/speechdb/timit/pcm/train/dr1/fcjf0/sa1.wav'
        >>> signal = audioread(path, offset=0, duration=1)
    """
    if isinstance(path, Path):
        path = str(path)
    path = os.path.expanduser(path)

    with wavefile.WaveReader(path) as wav_reader:
        channels = wav_reader.channels
        if sample_rate is None:
            sample_rate = wav_reader.samplerate
        if wav_reader.samplerate != sample_rate:
            raise ValueError(
                'Requested sampling rate is {} but the audiofile has {}'.format(
                    sample_rate, wav_reader.samplerate
                )
            )

        if duration is None:
            samples = wav_reader.frames - int(np.round(offset * sample_rate))
            frames_before = int(np.round(offset * sample_rate))
        else:
            samples = int(np.round(duration * sample_rate))
            frames_before = int(np.round(offset * sample_rate))

        data = np.empty((channels, samples), dtype=np.float32, order='F')
        wav_reader.seek(frames_before)
        wav_reader.read(data)
        return np.squeeze(data)


def read_nist_wsj(path, sample_rate=16000, audioread_function=audioread):
    """
    Converts a nist/sphere file of wsj and reads it with audioread.

    :param path: file path to audio file.
    :param sample_rate: Resamples utterances to given value. None = native
        sample rate.
    :param audioread_function: Function to use to read the resulting audio file
    :return:
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    cmd = "{}/sph2pipe -f wav {path} {dest_file}".format(
        UTILS_DIR, path=path, dest_file=tmp_file.name
    )
    pc.run_processes(cmd, ignore_return_code=False)
    signal = audioread_function(tmp_file.name, sample_rate=sample_rate)
    os.remove(tmp_file.name)
    return signal


def read_raw(path, dtype=np.dtype('<i2')):
    """
    Reads raw data (tidigits data)

    :param path: file path to audio file
    :param dtype: datatype, default: int16, little-endian
    :return: numpy array with audio samples
    """

    if isinstance(path, Path):
        path = str(path)

    with open(path, 'rb') as f:
        return np.fromfile(f, dtype=dtype)


def getparams(path):
    """
    Returns parameters of wav file.

    :param path: Absolute or relative file path to audio file.
    :type: String.
    :return: Named tuple with attributes (nchannels, sampwidth, framerate,
    nframes, comptype, compname)
    """
    with wave.open(str(path), 'r') as wave_file:
        return wave_file.getparams()


def read_from_byte_string(byte_string, dtype=np.dtype('<i2')):
    """ Parses a bytes string, i.e. a raw read of a wav file

    :param byte_string: input bytes string
    :param dtype: dtype used to decode the audio data
    :return: np.ndarray with audio data with channels x samples
    """
    wav_file = wave.openfp(BytesIO(byte_string))
    channels = wav_file.getnchannels()
    interleaved_audio_data = np.frombuffer(
        wav_file.readframes(wav_file.getnframes()), dtype=dtype)
    audio_data = np.array(
        [interleaved_audio_data[ch::channels] for ch in range(channels)])
    audio_data = audio_data.astype(np.float32) / np.max(audio_data)
    return audio_data
