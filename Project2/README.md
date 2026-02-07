# MedlinePlus RAG Chat (Project 2)

A Retrieval-Augmented Generation (RAG) chatbot that answers medical questions using **ONLY trusted MedlinePlus content**.

This project is designed to reduce hallucinations by enforcing strict rules:
- The assistant must use ONLY the retrieved context
- If the context does not contain the answer, it must say so clearly
- It gives general informational next steps (not personalized treatment plans)
- It ends with: **"This is not medical advice."**

---

## Features
- MedlinePlus-based retrieval (RAG)
- Strict “context-only” answering rules
- Web UI chat interface
- Summarized answers in paragraph form
- Prevents unsupported claims by refusing when sources don’t contain the answer

---

## Tech Stack
- Python
- OpenAI API (chat + embeddings)
- Vector retrieval (depending on implementation)
- Flask (or similar backend)
- HTML/CSS/JavaScript frontend

---

## Example Project Structure
.
├── app.py
├── main.py
├── medline_tools.py
├── vanilla_rag.py
├── agentic_rag.py
├── color_web_app.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env # NOT uploaded to GitHub
├── .env.example # safe template
└── README.md


> Your file names may vary. Update this section to match your repo if needed.

---

## Setup Instructions

### 1) Clone the repo
```bash
git clone <YOUR_GITHUB_REPO_LINK>
cd <YOUR_REPO_FOLDER>
2) Create and activate a virtual environment
Option A (Recommended): using uv
Install uv:

pip install uv
Create environment:

uv venv
Activate it:

Windows PowerShell

.venv\Scripts\Activate.ps1
Mac/Linux

source .venv/bin/activate
Install dependencies:

uv pip install -r requirements.txt
Option B: using regular Python venv
Create environment:

python -m venv .venv
Activate it:

Windows PowerShell

.venv\Scripts\Activate.ps1
Mac/Linux

source .venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Environment Variables (.env)
1) Create a .env file
Inside your project folder (root), create:

.env
2) Add your OpenAI API key
Inside .env, add:

OPENAI_API_KEY=your_api_key_here
IMPORTANT: Do NOT Upload Your API Key
To make your repo safe, this project uses .env.example.

Create .env.example
Create a file named:

.env.example
And add:

OPENAI_API_KEY=xxxxxxx
Add .env to .gitignore
Make sure your .gitignore contains:

.env
.venv/
__pycache__/
*.pyc
Running the Project
Depending on your setup, one of these will work:

python app.py
or

python main.py
or

python color_web_app.py
Open the Web App
Once the server is running, open your browser:

http://127.0.0.1:5000
(Or whatever port your terminal shows.)

Example Questions You Can Ask
"What is bipolar disorder?"

"What are symptoms of insomnia?"

"How is depression diagnosed?"

"What are treatment options for anxiety?"

"What should I do if I have bipolar disorder and insomnia?"

Safety Rules Used in This Project
The assistant follows these rules:

Use ONLY the retrieved CONTEXT

Do not add facts not supported by the context

If the context does not contain the needed information, respond with:
"I don't have enough information from the provided sources."

If the user asks “what should I do”, provide general informational next steps only

Crisis guidance must be general (seek urgent care / emergency services if severe)

Always end with:
"This is not medical advice."

Notes
This project is for educational purposes only and is not a substitute for professional medical advice.

License
This project is open for educational use.
(You can add an MIT License if you want.)


---