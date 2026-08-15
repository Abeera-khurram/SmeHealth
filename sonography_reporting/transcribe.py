"""
Voice Transcription - fully local, free (no API cost).
Uses faster-whisper (open-weight Whisper model, runs on CPU) to transcribe
radiologist voice annotations recorded during a sonography scan.
"""
from faster_whisper import WhisperModel

# "base" model: good accuracy/speed tradeoff for CPU, ~150MB, free download
_model = WhisperModel("base", device="cpu", compute_type="int8")


def transcribe_audio(audio_path: str) -> str:
    segments, _info = _model.transcribe(audio_path, language="en")
    return " ".join(seg.text.strip() for seg in segments)
