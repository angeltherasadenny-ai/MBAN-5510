from vanilla_rag import vanilla_rag_answer
from agentic_rag import agentic_rag_answer

def run_vanilla():
    while True:
        q = input("\n[Vanilla] Ask a question (or type 'back'): ").strip()
        if q.lower() in {"back", "b"}:
            return
        if q.lower() in {"q", "quit", "exit"}:
            raise SystemExit
        if not q:
            continue

        out = vanilla_rag_answer(q)
        print("\n=== VANILLA RAG ANSWER ===\n")
        print(out["answer"])
        print("\n=== SOURCES USED ===")
        for s in out["sources"]:
            print("-", s)

def run_agentic():
    while True:
        q = input("\n[Agentic] Ask a question (or type 'back'): ").strip()
        if q.lower() in {"back", "b"}:
            return
        if q.lower() in {"q", "quit", "exit"}:
            raise SystemExit
        if not q:
            continue

        out = agentic_rag_answer(q)
        print("\n=== AGENTIC RAG ANSWER ===\n")
        print(out["answer"])
        print("\n=== SOURCES USED ===")
        for s in out["sources"]:
            print("-", s)

        # Optional debug (shows what the agent did)
        print("\n--- Agent Debug ---")
        print("Search queries:", out["debug"]["queries"])
        print("Fetched URLs:", out["debug"]["picked_urls"])

def main():
    print("===================================")
    print(" Project 2: MedlinePlus RAG System ")
    print("===================================")

    while True:
        print("\nChoose mode:")
        print("1) Vanilla RAG (fixed pipeline)")
        print("2) Agentic RAG (agent chooses steps)")
        print("3) Quit")

        choice = input("Enter 1/2/3: ").strip()

        try:
            if choice == "1":
                run_vanilla()
            elif choice == "2":
                run_agentic()
            elif choice == "3":
                print("Bye!")
                break
            else:
                print("Invalid choice. Enter 1, 2, or 3.")
        except SystemExit:
            print("Bye!")
            break

if __name__ == "__main__":
    main()
