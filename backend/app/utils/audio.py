from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

DEFAULT_SAMPLE_RATE = 16000
DEFAULT_DURATION_SEC = 5
N_MELS = 64


def load_waveform(path: Path, sample_rate: int = DEFAULT_SAMPLE_RATE) -> np.ndarray:
    """Load waveform from file and ensure consistent sample rate."""
    waveform, _ = librosa.load(path, sr=sample_rate, mono=True)
    target_length = sample_rate * DEFAULT_DURATION_SEC
    if waveform.shape[0] < target_length:
        pad_width = target_length - waveform.shape[0]
        waveform = np.pad(waveform, (0, pad_width))
    else:
        waveform = waveform[:target_length]
    return waveform


def extract_mel_spectrogram(
    waveform: np.ndarray,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    n_mels: int = N_MELS,
) -> np.ndarray:
    """Return log-mel spectrogram features for inference."""
    spectrogram = librosa.feature.melspectrogram(
        y=waveform,
        sr=sample_rate,
        n_fft=1024,
        hop_length=256,
        n_mels=n_mels,
    )
    log_mel = librosa.power_to_db(spectrogram)
    # Normalize
    mean = np.mean(log_mel)
    std = np.std(log_mel)
    normalized = (log_mel - mean) / (std + 1e-6)
    return normalized

