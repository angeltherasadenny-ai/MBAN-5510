import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://medlineplus.gov/",
}

def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def search_medlineplus(query: str, max_results: int = 5) -> list[dict]:
    """
    Uses the official MedlinePlus Web Service (XML).
    Example: https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term=asthma

    Returns: [{title, url}, ...]
    """
    term = quote_plus(query)
    url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term={term}&retmax={max_results}&rettype=brief"

    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    root = ET.fromstring(r.text)

    results = []
    for doc in root.findall(".//list/document"):
        doc_url = (doc.attrib.get("url") or "").strip()
        title_node = doc.find("./content[@name='title']")
        title = _clean_text("".join(title_node.itertext())) if title_node is not None else "MedlinePlus Topic"

        if not doc_url:
            continue
        if "medlineplus.gov" not in doc_url:
            continue

        results.append({"title": title, "url": doc_url})
        if len(results) >= max_results:
            break

    return results

def fetch_medline_article(url: str, max_chars: int = 12000) -> dict:
    """
    Fetches a MedlinePlus topic page and extracts main text.
    FILTER: cap extracted text to max_chars.
    """
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    # Remove junk
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    main = soup.select_one("main") or soup.select_one("#mplus-content") or soup.body
    text = main.get_text(" ", strip=True) if main else soup.get_text(" ", strip=True)
    text = _clean_text(text)

    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    title = soup.title.get_text(" ", strip=True) if soup.title else "MedlinePlus Page"
    return {"title": title, "url": url, "text": text}
