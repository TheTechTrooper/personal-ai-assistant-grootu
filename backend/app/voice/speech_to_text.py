import os
import queue
import time
from typing import Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_DURATION_SECONDS = 0.1
BLOCKSIZE = int(SAMPLE_RATE * BLOCK_DURATION_SECONDS)

STT_MODEL_SIZE = os.getenv("STT_MODEL_SIZE", "small.en")
STT_DEVICE = os.getenv("STT_DEVICE", "cpu")
STT_COMPUTE_TYPE = os.getenv("STT_COMPUTE_TYPE", "int8")
STT_ENERGY_THRESHOLD = float(os.getenv("STT_ENERGY_THRESHOLD", "0.012"))

_audio_queue: "queue.Queue[np.ndarray]" = queue.Queue()
_model = WhisperModel(
    STT_MODEL_SIZE,
    device=STT_DEVICE,
    compute_type=STT_COMPUTE_TYPE,
)


def _audio_callback(indata, frames, callback_time, status):
    if status:
        print(status)
    # indata shape: (frames, channels)
    mono = indata[:, 0].copy()
    _audio_queue.put(mono)


def _rms(chunk: np.ndarray) -> float:
    if chunk.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(chunk), dtype=np.float64)))


def _capture_until_silence(
    max_seconds: float,
    min_seconds: float,
    silence_seconds: float,
) -> Optional[np.ndarray]:
    if max_seconds <= 0:
        return None

    chunks: list[np.ndarray] = []
    started_speaking = False
    silence_run = 0.0
    start_time = time.time()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCKSIZE,
        callback=_audio_callback,
    ):
        while True:
            elapsed = time.time() - start_time
            if elapsed >= max_seconds:
                break

            try:
                chunk = _audio_queue.get(timeout=0.3)
            except queue.Empty:
                continue

            chunks.append(chunk)
            energy = _rms(chunk)

            if energy >= STT_ENERGY_THRESHOLD:
                started_speaking = True
                silence_run = 0.0
            elif started_speaking:
                silence_run += BLOCK_DURATION_SECONDS

            if started_speaking and elapsed >= min_seconds and silence_run >= silence_seconds:
                break

    if not started_speaking or not chunks:
        return None

    audio = np.concatenate(chunks, axis=0).astype(np.float32, copy=False)
    return audio


def _transcribe(audio: np.ndarray) -> Optional[str]:
    segments, _ = _model.transcribe(
        audio,
        language="en",
        beam_size=2,
        vad_filter=True,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return text or None


def listen() -> Optional[str]:
    print("Listening (faster-whisper)...")
    audio = _capture_until_silence(
        max_seconds=8.0,
        min_seconds=0.7,
        silence_seconds=0.9,
    )
    if audio is None:
        return None

    text = _transcribe(audio)
    if text:
        print(f"You said: {text}")
    return text


def listen_for_seconds(timeout_seconds: float = 1.2) -> Optional[str]:
    audio = _capture_until_silence(
        max_seconds=timeout_seconds,
        min_seconds=0.2,
        silence_seconds=0.35,
    )
    if audio is None:
        return None
    return _transcribe(audio)
