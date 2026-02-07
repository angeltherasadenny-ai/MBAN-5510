from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from medline_tools import search_medlineplus, fetch_medline_article
from rag_utils import chunk_text, keyword_rank_chunks, normalize_query, split_conditions

load_dotenv()


def robust_search_hits(question: str, max_results_per_query: int = 6):
    """
    Agentic-friendly:
    - cleaned main query
    - fallback split topics
    """
    clean = normalize_query(question)
    hits = search_medlineplus(clean, max_results=max_results_per_query)

    merged = []
    seen = set()

    def add_hits(hlist):
        nonlocal merged, seen
        for h in hlist:
            url = h.get("url")
            if url and url not in seen:
                seen.add(url)
                merged.append(h)

    add_hits(hits)

    # fallback if weak
    if len(merged) < 2:
        for topic in split_conditions(question):
            add_hits(search_medlineplus(topic, max_results=max_results_per_query))

    return merged


def agentic_rag_answer(question: str) -> dict:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=1200,
    )

    hits = robust_search_hits(question, max_results_per_query=6)

    if not hits:
        return {
            "answer": (
                "I couldn’t find relevant MedlinePlus pages for that query. "
                "Try shorter keywords (e.g., 'bipolar disorder' or 'insomnia'). "
                "This is not medical advice."
            ),
            "sources": [],
            "debug": {"picked_urls": [], "queries_used": [normalize_query(question)]}
        }

    # LLM picks best URLs (up to 3)
    options = "\n".join([f"{i+1}. {h['title']} | {h['url']}" for i, h in enumerate(hits[:12])])

    pick = llm.invoke(
        f"""
Pick up to 3 URLs from the list that best answer the user's question.
Return ONLY the URLs, one per line.

Question: {question}

Options:
{options}
""".strip()
    ).content

    urls = []
    for line in pick.splitlines():
        line = line.strip()
        if line.startswith("http"):
            urls.append(line)
        if len(urls) >= 3:
            break

    if not urls:
        urls = [h["url"] for h in hits[:3]]

    # Fetch pages with larger max chars
    gathered_chunks = []
    for u in urls:
        page = fetch_medline_article(u, max_chars=20000)
        chunks = chunk_text(page.get("text", ""), chunk_size=1000, chunk_overlap=150)[:10]
        for c in chunks:
            gathered_chunks.append({"text": c, "title": page.get("title", ""), "url": page.get("url", u)})

    top_chunks = keyword_rank_chunks(question, gathered_chunks, k=10)
    context = "\n\n".join(
        [f"Source: {c['title']} ({c['url']})\nSnippet:\n{c['text']}" for c in top_chunks]
    )
    sources = list(dict.fromkeys([c["url"] for c in top_chunks if c.get("url")]))

    final = llm.invoke(
        f"""
You are a careful healthcare information assistant.

RULES:
- Use ONLY the CONTEXT. Do not add facts not supported by the context.
- If the context does not contain the needed information, say: "I don't have enough information from the provided sources."
- If the user asks “what should I do”, give general informational next steps (not personalized treatment).
- End with: "This is not medical advice."

FORMAT (use when relevant):
1) Overview
2) Symptoms
3) Causes / Risk factors
4) Diagnosis / Tests
5) Treatment options (general)
6) Self-care / Prevention (general)
7) When to seek urgent medical care

Question: {question}

CONTEXT:
{context}

Return ONLY the answer text.
""".strip()
    ).content.strip()

    return {
        "answer": final,
        "sources": sources,
        "debug": {
            "picked_urls": urls,
            "queries_used": [normalize_query(question)] + split_conditions(question)
        }
    }


if __name__ == "__main__":
    while True:
        q = input("\nAsk (or q to quit): ").strip()
        if q.lower() in {"q", "quit", "exit"}:
            break
        out = agentic_rag_answer(q)
        print("\n=== ANSWER ===\n")
        print(out["answer"])
        print("\n=== SOURCES ===")
        for s in out["sources"]:
            print("-", s)
        print("\n--- DEBUG ---")
        print(out["debug"])

