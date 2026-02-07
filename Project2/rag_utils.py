import re
from typing import List, Dict, Any


STOP_PHRASES = [
    r"what should i do if i have",
    r"what do i do if i have",
    r"what should i do about",
    r"what do i do about",
    r"what should i do if",
    r"what do i do if",
    r"i have",
    r"i think i have",
    r"can you tell me about",
    r"tell me about",
    r"help me with",
]

def normalize_query(q: str) -> str:
    """
    Converts a user question into a MedlinePlus-search-friendly keyword string.
    """
    s = (q or "").strip().lower()
    s = re.sub(r"[^\w\s\-\+]", " ", s)       # remove punctuation
    s = re.sub(r"\s+", " ", s).strip()

    # remove leading chatty phrases
    for p in STOP_PHRASES:
        s = re.sub(rf"^{p}\s+", "", s).strip()

    return s


def split_conditions(q: str) -> List[str]:
    """
    Splits multi-issue queries into topic keywords.
    Example: "bipolar disorder and insomnia" -> ["bipolar disorder", "insomnia"]
    """
    s = normalize_query(q)
    if not s:
        return []

    # common separators
    parts = re.split(r"\b(?:and|with|plus|&)\b|,", s)
    parts = [p.strip() for p in parts if len(p.strip()) >= 3]

    # Keep up to 3 topics to avoid huge fetches
    return parts[:3] if parts else [s]


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> List[str]:
    """
    Simple character-based chunking with overlap.
    """
    if not text:
        return []

    t = text.strip()
    if len(t) <= chunk_size:
        return [t]

    chunks = []
    start = 0
    while start < len(t):
        end = min(start + chunk_size, len(t))
        chunk = t[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == len(t):
            break
        start = max(0, end - chunk_overlap)

    return chunks


def keyword_rank_chunks(question: str, chunks: List[Dict[str, Any]], k: int = 8) -> List[Dict[str, Any]]:
    """
    Very lightweight scoring:
    - count overlapping keywords between question and chunk
    - prefer chunks with more overlap
    """
    q = normalize_query(question)
    q_tokens = set(q.split())

    def score(c: Dict[str, Any]) -> int:
        txt = normalize_query(c.get("text", ""))
        tokens = set(txt.split())
        return len(q_tokens.intersection(tokens))

    ranked = sorted(chunks, key=score, reverse=True)
    return ranked[:k]
