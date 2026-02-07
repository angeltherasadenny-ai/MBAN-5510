from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from medline_tools import search_medlineplus, fetch_medline_article
from rag_utils import chunk_text, keyword_rank_chunks, normalize_query, split_conditions

load_dotenv()


def robust_search(question: str, max_results_per_query: int = 6):
    """
    1) Try a cleaned keyword query
    2) If weak/empty, split into topics and merge results
    """
    clean = normalize_query(question)
    hits = search_medlineplus(clean, max_results=max_results_per_query)

    if hits:
        return hits

    merged = []
    seen = set()
    topics = split_conditions(question)
    for topic in topics:
        for h in search_medlineplus(topic, max_results=max_results_per_query):
            url = h.get("url")
            if url and url not in seen:
                seen.add(url)
                merged.append(h)

    return merged


def vanilla_rag_answer(question: str) -> dict:
    """
    search -> fetch -> chunk -> rank -> answer
    Returns { "answer": str, "sources": [urls] }
    """

    hits = robust_search(question, max_results_per_query=6)

    if not hits:
        return {
            "answer": (
                "I couldn’t find relevant MedlinePlus pages for that query. "
                "Try shorter keywords (e.g., 'bipolar disorder' or 'insomnia'). "
                "This is not medical advice."
            ),
            "sources": []
        }

    # Fetch more text
    pages = [fetch_medline_article(h["url"], max_chars=20000) for h in hits[:5]]

    # Chunk pages
    all_chunks = []
    per_page_chunk_cap = 12
    total_chunks_cap = 50

    for p in pages:
        chunks = chunk_text(p.get("text", ""), chunk_size=1000, chunk_overlap=150)
        for c in chunks[:per_page_chunk_cap]:
            all_chunks.append({"text": c, "title": p.get("title", ""), "url": p.get("url", "")})
        if len(all_chunks) >= total_chunks_cap:
            all_chunks = all_chunks[:total_chunks_cap]
            break

    top_chunks = keyword_rank_chunks(question, all_chunks, k=10)

    context = "\n\n".join(
        [f"Source: {c['title']} ({c['url']})\nSnippet:\n{c['text']}" for c in top_chunks]
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=1100,
    )

    prompt = f"""
You are a careful healthcare information assistant.

RULES:

You are a helpful assistant.

Answer the user’s question using only the information in the provided context. Do not add outside facts or assumptions. If the context does not contain enough information to answer, say: "I don't have enough information from the provided sources."

Keep your response short and easy to understand in 1–2 brief paragraphs. If the user asks what to do, provide only general informational guidance (not personal medical advice). End with: "This is not medical advice."

QUESTION:
{question}

CONTEXT:
{context}

Return ONLY the answer text.
""".strip()

    resp = llm.invoke(prompt).content.strip()
    sources = list(dict.fromkeys([c["url"] for c in top_chunks if c.get("url")]))

    return {"answer": resp, "sources": sources}


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else input("Ask: ").strip()
    out = vanilla_rag_answer(q)

    print("\n=== ANSWER ===\n")
    print(out["answer"])
    print("\n=== SOURCES ===")
    for s in out["sources"]:
        print("-", s)
