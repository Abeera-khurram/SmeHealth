"""
Screenshot Reader - reads sonography machine screenshots (measurements,
labels, on-screen annotations) using a free vision-capable LLM.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import call_vision

SCREENSHOT_SYSTEM_PROMPT = """You are a medical imaging assistant reading a screenshot from an
ultrasound/sonography machine. Extract every visible on-screen measurement, label, organ view,
and numeric value exactly as shown. Do not interpret or diagnose - only transcribe what is
visually present on screen."""


def read_screenshot(image_path: str) -> str:
    return call_vision(
        system_prompt=SCREENSHOT_SYSTEM_PROMPT,
        image_path=image_path,
        question="List every measurement, label, and value visible in this sonography machine screenshot.",
    )
