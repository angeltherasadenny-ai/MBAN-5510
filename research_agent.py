import requests
from bs4 import BeautifulSoup


def research_michael(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}

    # verify=False fixes SMU SSL issue
    r = requests.get(url, headers=headers, timeout=20, verify=False)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else "Michael Zhang"

    # Return ONLY name (prevents menu garbage)
    return {"name": name}
