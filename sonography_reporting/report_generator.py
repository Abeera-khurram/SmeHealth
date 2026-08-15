"""
Sonography Report Generator
------------------------------
Combines (a) machine screenshot readings and (b) the radiologist's spoken
annotation into one structured report - replacing the manual dictation +
typing workflow the medical assistant currently does by hand.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import call_llm_json
from sonography_reporting.transcribe import transcribe_audio
from sonography_reporting.screenshot_reader import read_screenshot

REPORT_SYSTEM_PROMPT = """You are a medical scribe assistant generating a structured sonography
report. You are given (1) machine-extracted measurements/labels from the screen and (2) the
radiologist's spoken annotation, transcribed to text. Merge these into a clean, structured report.
Do NOT invent findings not present in either source.

Respond ONLY in JSON:
{
  "exam_type": "<type of scan, inferred from inputs>",
  "measurements": ["measurement 1", "measurement 2"],
  "radiologist_findings": "<radiologist's narrative findings, cleaned up from transcript>",
  "impression": "<summary impression, derived only from what radiologist stated>",
  "flag_for_review": true/false,
  "flag_reason": "<reason if flagged, else empty string>"
}
"""


def generate_report(screenshot_path: str, audio_path: str) -> dict:
    screen_data = read_screenshot(screenshot_path)
    voice_transcript = transcribe_audio(audio_path)

    user_prompt = (
        f"Machine screenshot data:\n{screen_data}\n\n"
        f"Radiologist voice annotation (transcribed):\n{voice_transcript}"
    )
    report = call_llm_json(REPORT_SYSTEM_PROMPT, user_prompt)
    report["_screen_data_raw"] = screen_data
    report["_voice_transcript_raw"] = voice_transcript
    return report
