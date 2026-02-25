# middleware.py
# All middleware components used in the LangGraph workflow.
#
# Middleware documented:
#   PIIMiddleware              — masks patient identifiers before logging
#   OpenAIModerationMiddleware — flags harmful content via OpenAI API
#   ToolCallLimitMiddleware    — caps LLM calls per node (fresh instance each time)
#   ModelRetryMiddleware       — retries failed LLM calls with backoff

import re
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── 1. PIIMiddleware ──────────────────────────────────────────────
# Scans the patient message and masks personal info so it never
# appears in logs or gets passed to external systems.
class PIIMiddleware:
    PII_PATTERNS = {
        "phone":       r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "email":       r'[\w.-]+@[\w.-]+\.\w+',
        "dob":         r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        "health_card": r'\b[A-Z]{4}\d{8,12}\b',
    }

    def run(self, text: str) -> str:
        for label, pattern in self.PII_PATTERNS.items():
            text = re.sub(pattern, f"[REDACTED-{label.upper()}]", text, flags=re.IGNORECASE)
        return text


# ── 2. OpenAIModerationMiddleware ─────────────────────────────────
# Calls OpenAI's moderation endpoint. If flagged → route to ESCALATE.
class OpenAIModerationMiddleware:
    def run(self, text: str) -> dict:
        try:
            response = client.moderations.create(input=text)
            result = response.results[0]
            flagged_cats = [cat for cat, val in result.categories.__dict__.items() if val]
            return {"flagged": result.flagged, "categories": flagged_cats}
        except Exception as e:
            print(f"[ModerationMiddleware] Warning: {e}")
            return {"flagged": False, "categories": []}


# ── 3. ToolCallLimitMiddleware ────────────────────────────────────
# Created fresh per node call so the count never carries over
# between Streamlit reruns. Raises if limit exceeded.
class ToolCallLimitMiddleware:
    def __init__(self, max_calls: int = 5):
        self.max_calls = max_calls
        self.call_count = 0

    def check(self):
        self.call_count += 1
        if self.call_count > self.max_calls:
            raise RuntimeError(
                f"[ToolCallLimitMiddleware] Exceeded max calls ({self.max_calls})."
            )


def get_fresh_limiter() -> ToolCallLimitMiddleware:
    """Always return a brand-new limiter — no state carries over between runs."""
    return ToolCallLimitMiddleware(max_calls=5)


# ── 4. ModelRetryMiddleware ───────────────────────────────────────
# Wraps any LLM call with automatic retry + backoff.
class ModelRetryMiddleware:
    def __init__(self, max_retries: int = 2, wait_seconds: int = 1):
        self.max_retries = max_retries
        self.wait_seconds = wait_seconds

    def run(self, func, *args, **kwargs):
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                wait = self.wait_seconds * attempt
                print(f"[ModelRetryMiddleware] Attempt {attempt} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
        raise RuntimeError(f"[ModelRetryMiddleware] All retries failed. Last error: {last_error}")
