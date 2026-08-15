"""
Model Selection Harness
-------------------------
Description explicitly calls for "experimentation and selection of the
best-performing LLMs" against manually-written reports. This script runs
the SAME screenshot+voice input through multiple free Groq models and
scores each generated report against a human-written reference report,
so a real dataset of (screenshot, audio, human_report) triples can be used
to pick the best model.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import call_llm_json, call_llm
from sonography_reporting.transcribe import transcribe_audio
from sonography_reporting.screenshot_reader import read_screenshot
from sonography_reporting.report_generator import REPORT_SYSTEM_PROMPT

# Free, open-weight candidate models available on Groq
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

SCORING_SYSTEM_PROMPT = """You are a medical QA evaluator. Compare an AI-generated sonography
report against a human radiologist's reference report. Score how well the AI report captures the
same findings and impression as the reference, on a 0-10 scale.

Respond ONLY in JSON: {"score": <0-10>, "missed_findings": ["..."], "hallucinated_findings": ["..."]}
"""


def score_against_reference(ai_report: dict, human_reference_text: str) -> dict:
    prompt = f"AI report:\n{ai_report}\n\nHuman reference report:\n{human_reference_text}"
    return call_llm_json(SCORING_SYSTEM_PROMPT, prompt)


def compare_models(screenshot_path: str, audio_path: str, human_reference_text: str) -> list[dict]:
    screen_data = read_screenshot(screenshot_path)
    voice_transcript = transcribe_audio(audio_path)
    user_prompt = f"Machine screenshot data:\n{screen_data}\n\nRadiologist voice annotation:\n{voice_transcript}"

    results = []
    for model in CANDIDATE_MODELS:
        raw = call_llm(REPORT_SYSTEM_PROMPT, user_prompt, model=model, json_mode=True)
        import json
        try:
            ai_report = json.loads(raw)
        except json.JSONDecodeError:
            ai_report = {"error": "malformed_json"}
        score = score_against_reference(ai_report, human_reference_text)
        results.append({"model": model, "report": ai_report, "score": score})

    results.sort(key=lambda r: r["score"].get("score", 0), reverse=True)
    return results
