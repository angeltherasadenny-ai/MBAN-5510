from flask import Flask, request, jsonify, Response
from datetime import datetime

from vanilla_rag import vanilla_rag_answer
from agentic_rag import agentic_rag_answer

app = Flask(__name__)

# ==========================================================
# 1) Your colourful HTML page embedded directly in Python
# ==========================================================
HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Project 2 — MedlinePlus RAG Chat</title>

  <style>
    :root{
      --bg1: #ff3cac;
      --bg2: #784ba0;
      --bg3: #2b86c5;

      --bgA: rgba(255,255,255,.10);
      --bgB: rgba(255,255,255,.14);
      --line: rgba(255,255,255,.18);

      --text: rgba(255,255,255,.95);
      --muted: rgba(255,255,255,.72);

      --vanilla1: #7c5cff;
      --vanilla2: #2b86c5;

      --agent1: #22c55e;
      --agent2: #06b6d4;

      --danger1: #ff4d6d;
      --danger2: #ff9a8b;

      --shadow: 0 18px 40px rgba(0,0,0,.35);
      --radius: 18px;
    }

    /* Light mode */
    [data-theme="light"]{
      --bgA: rgba(17,24,39,.06);
      --bgB: rgba(17,24,39,.10);
      --line: rgba(17,24,39,.12);
      --text: rgba(17,24,39,.92);
      --muted: rgba(17,24,39,.60);
      --shadow: 0 18px 40px rgba(17,24,39,.14);
    }

    *{ box-sizing: border-box; }
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      color: var(--text);
      background:
        radial-gradient(1200px 600px at 10% 10%, rgba(255,255,255,.18), transparent 60%),
        radial-gradient(900px 600px at 90% 20%, rgba(255,255,255,.12), transparent 60%),
        linear-gradient(135deg, var(--bg1), var(--bg2), var(--bg3));
      min-height: 100vh;
      overflow-x: hidden;
    }

    a{ color: #fff; text-decoration: underline; text-decoration-color: rgba(255,255,255,.45); }
    a:hover{ text-decoration-color: rgba(255,255,255,.85); }

    .wrap{
      max-width: 1120px;
      margin: 0 auto;
      padding: 18px;
      display: grid;
      gap: 14px;
      grid-template-columns: 330px 1fr;
      min-height: 100vh;
    }

    .glass{
      background: var(--bgA);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }

    /* Sidebar */
    .sidebar{
      position: sticky;
      top: 18px;
      height: calc(100vh - 36px);
      display:flex;
      flex-direction: column;
      gap: 12px;
    }

    .card{ padding: 14px; }

    .brand{
      display:flex;
      align-items:flex-start;
      justify-content: space-between;
      gap: 10px;
    }

    .logo{
      width: 42px; height: 42px; border-radius: 14px;
      background: linear-gradient(135deg, rgba(255,255,255,.35), rgba(255,255,255,.12));
      border: 1px solid rgba(255,255,255,.22);
      display:flex; align-items:center; justify-content:center;
      box-shadow: 0 10px 22px rgba(0,0,0,.22);
      position: relative;
      overflow: hidden;
    }
    .logo:before{
      content:"";
      position:absolute;
      inset:-40%;
      background: conic-gradient(from 0deg, rgba(124,92,255,.9), rgba(34,197,94,.9), rgba(6,182,212,.9), rgba(255,60,172,.9), rgba(124,92,255,.9));
      animation: spin 6s linear infinite;
      opacity:.65;
    }
    .logo span{
      position: relative;
      font-weight: 900;
      letter-spacing: .5px;
    }
    @keyframes spin{ to{ transform: rotate(360deg);} }

    .title{
      font-weight: 900;
      letter-spacing: .2px;
      font-size: 15px;
      line-height: 1.2;
      text-shadow: 0 10px 20px rgba(0,0,0,.25);
    }
    .subtitle{
      margin-top: 6px;
      font-size: 12px;
      color: var(--muted);
      line-height: 1.35;
    }

    .pill{
      font-size: 11px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.16);
      border: 1px solid rgba(255,255,255,.22);
      color: var(--text);
      white-space: nowrap;
    }

    .chips{
      display:flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }
    .chip{
      font-size: 12px;
      padding: 8px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,.16);
      border: 1px solid rgba(255,255,255,.22);
      color: var(--text);
      cursor:pointer;
      transition: transform .08s ease, background .15s ease;
      user-select:none;
    }
    .chip:hover{
      background: rgba(255,255,255,.22);
      transform: translateY(-1px);
    }

    .controls{ display:grid; gap: 10px; }
    .row{ display:flex; gap: 10px; align-items:center; justify-content: space-between; }

    select, button, input{ font: inherit; }

    select{
      width: 100%;
      background: rgba(255,255,255,.14);
      border: 1px solid rgba(255,255,255,.22);
      border-radius: 14px;
      padding: 10px 12px;
      color: var(--text);
      outline:none;
    }

    .btn{
      background: rgba(255,255,255,.14);
      border: 1px solid rgba(255,255,255,.22);
      color: var(--text);
      padding: 10px 12px;
      border-radius: 14px;
      cursor: pointer;
      transition: transform .06s ease, filter .15s ease, background .15s ease;
      user-select: none;
      flex: 1;
      text-align:center;
    }
    .btn:hover{ background: rgba(255,255,255,.20); filter: brightness(1.05); }
    .btn:active{ transform: translateY(1px); }

    .btn.primary{
      background: linear-gradient(135deg, rgba(124,92,255,.95), rgba(43,134,197,.85));
      border-color: rgba(255,255,255,.25);
    }
    .btn.primary:hover{ filter: brightness(1.10); }

    .btn.danger{
      background: linear-gradient(135deg, rgba(255,77,109,.9), rgba(255,154,139,.85));
      border-color: rgba(255,255,255,.25);
    }

    .history{
      flex: 1;
      overflow:auto;
      padding: 10px 10px;
    }
    .history::-webkit-scrollbar{ width: 10px; }
    .history::-webkit-scrollbar-thumb{ background: rgba(255,255,255,.25); border-radius: 999px; }

    .hist-item{
      padding: 10px 10px;
      border-radius: 16px;
      background: rgba(255,255,255,.10);
      border: 1px solid rgba(255,255,255,.18);
      cursor:pointer;
      margin-top: 10px;
      transition: transform .08s ease, background .15s ease;
    }
    .hist-item:hover{
      background: rgba(255,255,255,.16);
      transform: translateY(-1px);
    }
    .hist-q{ font-size: 12px; line-height: 1.3; max-height: 2.6em; overflow:hidden; }
    .hist-meta{
      margin-top: 6px;
      font-size: 11px;
      color: var(--muted);
      display:flex;
      gap: 8px;
      align-items:center;
    }
    .dot{
      width: 9px; height: 9px; border-radius: 999px;
      background: linear-gradient(135deg, var(--vanilla1), var(--vanilla2));
      box-shadow: 0 0 12px rgba(124,92,255,.55);
    }
    .dot.agent{
      background: linear-gradient(135deg, var(--agent1), var(--agent2));
      box-shadow: 0 0 12px rgba(34,197,94,.55);
    }

    /* Main */
    .main{
      display:flex;
      flex-direction: column;
      gap: 12px;
      min-height: calc(100vh - 36px);
    }

    .chat{
      flex: 1;
      overflow:auto;
      padding: 14px;
    }
    .chat::-webkit-scrollbar{ width: 10px; }
    .chat::-webkit-scrollbar-thumb{ background: rgba(255,255,255,.25); border-radius: 999px; }

    .msg{ display:flex; margin: 12px 0; gap: 10px; align-items:flex-end; }
    .msg.user{ justify-content: flex-end; }

    .avatar{
      width: 36px; height: 36px; border-radius: 14px;
      display:flex; align-items:center; justify-content:center;
      font-weight: 900;
      font-size: 12px;
      border: 1px solid rgba(255,255,255,.22);
      background: rgba(255,255,255,.12);
      box-shadow: 0 12px 20px rgba(0,0,0,.18);
      flex: 0 0 auto;
    }
    .avatar.bot.vanilla{
      background: linear-gradient(135deg, rgba(124,92,255,.45), rgba(43,134,197,.35));
    }
    .avatar.bot.agentic{
      background: linear-gradient(135deg, rgba(34,197,94,.40), rgba(6,182,212,.30));
    }

    .bubble{
      max-width: 76%;
      padding: 12px 14px;
      border-radius: 18px;
      border: 1px solid rgba(255,255,255,.20);
      line-height: 1.45;
      white-space: pre-wrap;
      box-shadow: 0 12px 30px rgba(0,0,0,.20);
    }
    .user .bubble{
      background: linear-gradient(135deg, rgba(255,255,255,.22), rgba(255,255,255,.10));
    }
    .bot .bubble.vanilla{
      background: linear-gradient(135deg, rgba(124,92,255,.22), rgba(43,134,197,.14));
      box-shadow: 0 0 0 1px rgba(124,92,255,.15), 0 18px 36px rgba(0,0,0,.18);
    }
    .bot .bubble.agentic{
      background: linear-gradient(135deg, rgba(34,197,94,.20), rgba(6,182,212,.12));
      box-shadow: 0 0 0 1px rgba(34,197,94,.12), 0 18px 36px rgba(0,0,0,.18);
    }

    .meta{
      margin-top: 8px;
      font-size: 12px;
      color: var(--muted);
      display:flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items:center;
    }

    details{
      width: 100%;
      margin-top: 10px;
      border: 1px solid rgba(255,255,255,.18);
      border-radius: 16px;
      padding: 10px 12px;
      background: rgba(255,255,255,.10);
    }
    details summary{
      cursor:pointer;
      font-size: 12px;
      color: var(--muted);
      user-select:none;
    }
    .sources ul{ margin: 10px 0 0 18px; }
    .sources li{ margin: 6px 0; font-size: 12px; color: var(--text); }

    .composer{
      display:flex;
      gap: 10px;
      padding: 12px;
    }
    .input{
      flex: 1;
      padding: 12px 12px;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,.22);
      background: rgba(255,255,255,.12);
      color: var(--text);
      outline:none;
    }

    .typing{
      display:inline-flex;
      align-items:center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      margin-top: 6px;
    }
    .dots span{
      display:inline-block;
      width: 6px; height: 6px;
      border-radius: 999px;
      background: rgba(255,255,255,.75);
      opacity: .6;
      animation: bounce 1s infinite;
    }
    .dots span:nth-child(2){ animation-delay: .15s; }
    .dots span:nth-child(3){ animation-delay: .3s; }
    @keyframes bounce{
      0%,100%{ transform: translateY(0); opacity: .45; }
      50%{ transform: translateY(-3px); opacity: .95; }
    }

    .toast{
      position: fixed;
      bottom: 18px; left: 50%;
      transform: translateX(-50%);
      background: rgba(255,255,255,.18);
      border: 1px solid rgba(255,255,255,.22);
      box-shadow: var(--shadow);
      padding: 10px 12px;
      border-radius: 16px;
      color: var(--text);
      font-size: 12px;
      opacity: 0;
      pointer-events: none;
      transition: opacity .2s ease, transform .2s ease;
    }
    .toast.show{
      opacity: 1;
      transform: translateX(-50%) translateY(-6px);
    }

    @media (max-width: 980px){
      .wrap{ grid-template-columns: 1fr; }
      .sidebar{ position: relative; height: auto; }
    }
  </style>
</head>

<body data-theme="dark">
  <div class="wrap">

    <div class="sidebar">
      <div class="glass card">
        <div class="brand">
          <div style="display:flex; gap:10px;">
            <div class="logo"><span>R</span></div>
            <div>
              <div class="title">MedlinePlus RAG Chat</div>
              <div class="subtitle"> Vanilla + Agentic • cites sources</div>
            </div>
          </div>
          <div class="pill" id="statusPill">Ready</div>
        </div>

        <div class="chips">
          <div class="chip" data-prompt="ulcerative colitis symptoms">UC symptoms</div>
          <div class="chip" data-prompt="asthma treatment">Asthma treatment</div>
          <div class="chip" data-prompt="high blood pressure symptoms">BP symptoms</div>
          <div class="chip" data-prompt="diabetes complications">Diabetes complications</div>
          <div class="chip" data-prompt="migraine triggers">Migraine triggers</div>
        </div>
      </div>

      <div class="glass card controls">
        <div>
          <div class="subtitle" style="margin:0 0 6px 0;"><b>Mode</b></div>
          <select id="mode">
            <option value="vanilla">Vanilla RAG</option>
            <option value="agentic">Agentic RAG</option>
          </select>
        </div>

        <div class="row">
          <button class="btn" id="themeBtn">Toggle theme</button>
          <button class="btn danger" id="clearBtn">Clear chat</button>
        </div>

        <div class="row">
          <button class="btn" id="exportBtn">Export .txt</button>
          <button class="btn" id="toggleDebugBtn">Debug: ON</button>
        </div>

        <div class="subtitle">
          Press <b>Enter</b> to send • Click chips to autofill.
        </div>
      </div>

      <div class="glass history">
        <div class="subtitle"><b>Recent questions</b></div>
        <div id="historyList"></div>
      </div>
    </div>

    <div class="main">
      <div class="glass chat" id="chat"></div>

      <div class="glass composer">
        <input class="input" id="q" type="text" placeholder="Ask a healthcare question…" />
        <button class="btn primary" id="sendBtn">Send</button>
      </div>

      <div class="typing" id="typing" style="display:none;">
        <span>Thinking</span>
        <span class="dots"><span></span><span></span><span></span></span>
      </div>
    </div>

  </div>

  <div class="toast" id="toast">Copied!</div>

<script>
  const chat = document.getElementById("chat");
  const input = document.getElementById("q");
  const sendBtn = document.getElementById("sendBtn");
  const clearBtn = document.getElementById("clearBtn");
  const exportBtn = document.getElementById("exportBtn");
  const modeSel = document.getElementById("mode");
  const themeBtn = document.getElementById("themeBtn");
  const toast = document.getElementById("toast");
  const typing = document.getElementById("typing");
  const statusPill = document.getElementById("statusPill");
  const historyList = document.getElementById("historyList");
  const toggleDebugBtn = document.getElementById("toggleDebugBtn");

  let showDebug = true;
  const transcript = [];
  const history = [];

  function nowTime(){
    const d = new Date();
    return d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
  }
  function setStatus(t){ statusPill.textContent = t; }
  function showToast(msg){
    toast.textContent = msg;
    toast.classList.add("show");
    setTimeout(()=>toast.classList.remove("show"), 1200);
  }
  function escapeHtml(s){
    return s.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
  }

  function addHistoryItem(q, mode){
    history.unshift({ q, mode, ts: nowTime() });
    history.splice(12);
    renderHistory();
  }

  function renderHistory(){
    historyList.innerHTML = "";
    history.forEach(h=>{
      const div = document.createElement("div");
      div.className = "hist-item";
      div.innerHTML = `
        <div class="hist-q">${escapeHtml(h.q)}</div>
        <div class="hist-meta">
          <span class="dot ${h.mode === "agentic" ? "agent" : ""}"></span>
          <span>${h.mode}</span>
          <span>•</span>
          <span>${h.ts}</span>
        </div>
      `;
      div.onclick = ()=>{ input.value = h.q; input.focus(); };
      historyList.appendChild(div);
    });
  }

  function addMessage({role, text, mode=null, sources=[], debug=null}){
    transcript.push({role, text, mode, sources, debug});

    const wrap = document.createElement("div");
    const msg = document.createElement("div");
    msg.className = "msg " + (role === "user" ? "user" : "bot");

    const avatar = document.createElement("div");
    avatar.className = "avatar " + (role === "user" ? "" : "bot " + (mode || "vanilla"));
    avatar.textContent = role === "user" ? "YOU" : (mode === "agentic" ? "AG" : "AI");

    const bubble = document.createElement("div");
    bubble.className = "bubble " + (role === "user" ? "" : (mode || "vanilla"));
    bubble.textContent = text;

    if (role === "user"){ msg.appendChild(bubble); msg.appendChild(avatar); }
    else { msg.appendChild(avatar); msg.appendChild(bubble); }

    wrap.appendChild(msg);

    if (role !== "user"){
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.innerHTML = `<span><b>${mode === "agentic" ? "Agentic" : "Vanilla"}</b></span><span>•</span><span>${nowTime()}</span>`;
      wrap.appendChild(meta);

      if ((sources || []).length){
        const det = document.createElement("details");
        det.className = "sources";
        const items = sources.map(u => `<li><a href="${u}" target="_blank" rel="noopener">${escapeHtml(u)}</a></li>`).join("");
        det.innerHTML = `<summary>Sources (${sources.length})</summary><ul>${items}</ul>`;
        wrap.appendChild(det);
      }

      if (showDebug && mode === "agentic" && debug){
        const det2 = document.createElement("details");
        det2.innerHTML = `
          <summary>Agent debug</summary>
          <div style="margin-top:10px; font-size:12px; color: var(--muted); line-height:1.4;">
            <div><b>Search queries:</b> ${(debug.queries || []).map(escapeHtml).join(", ") || "(none)"}</div>
            <div style="margin-top:6px;"><b>Fetched URLs:</b> ${(debug.picked_urls || []).map(escapeHtml).join(", ") || "(none)"}</div>
          </div>
        `;
        wrap.appendChild(det2);
      }
    }

    chat.appendChild(wrap);
    chat.scrollTop = chat.scrollHeight;
  }

  async function ask(){
    const question = input.value.trim();
    if (!question) return;

    const mode = modeSel.value;
    addMessage({ role: "user", text: question, mode });
    addHistoryItem(question, mode);

    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    typing.style.display = "inline-flex";
    setStatus("Working…");

    try{
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ question, mode })
      });

      const data = await res.json();
      if (!res.ok){
        addMessage({ role: "bot", text: "Error: " + (data.error || "Unknown error"), mode });
        return;
      }

      addMessage({
        role: "bot",
        text: data.answer || "(no answer returned)",
        mode: data.mode || mode,
        sources: data.sources || [],
        debug: data.debug || null
      });

    } catch(err){
      addMessage({ role: "bot", text: "Network/Server error: " + err.message, mode });
    } finally{
      typing.style.display = "none";
      setStatus("Ready");
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  function clearChat(){
    chat.innerHTML = "";
    transcript.length = 0;
    setStatus("Ready");
    addMessage({
      role: "bot",
      text: "Hi! Choose Vanilla or Agentic mode, then ask a healthcare question.\n\nI will cite MedlinePlus sources.\n\nThis is not medical advice.",
      mode: "vanilla",
      sources: []
    });
  }

  function exportTxt(){
    const lines = [];
    transcript.forEach(m=>{
      const head = m.role === "user" ? `[YOU | ${m.mode || ""}]` : `[BOT | ${m.mode || ""}]`;
      lines.push(head);
      lines.push(m.text);
      if (m.sources && m.sources.length){
        lines.push("Sources:");
        m.sources.forEach(s=>lines.push(" - " + s));
      }
      if (showDebug && m.mode === "agentic" && m.debug){
        lines.push("Agent Debug:");
        lines.push(" queries: " + (m.debug.queries || []).join(", "));
        lines.push(" fetched: " + (m.debug.picked_urls || []).join(", "));
      }
      lines.push("");
    });

    const blob = new Blob([lines.join("\n")], {type:"text/plain;charset=utf-8"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "project2_chat_export.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("Exported ✅");
  }

  sendBtn.addEventListener("click", ask);
  input.addEventListener("keydown", (e)=>{
    if (e.key === "Enter"){
      e.preventDefault();
      ask();
    }
  });

  clearBtn.addEventListener("click", clearChat);
  exportBtn.addEventListener("click", exportTxt);

  document.querySelectorAll(".chip").forEach(ch=>{
    ch.addEventListener("click", ()=>{
      input.value = ch.dataset.prompt || "";
      input.focus();
    });
  });

  themeBtn.addEventListener("click", ()=>{
    const body = document.body;
    body.dataset.theme = body.dataset.theme === "light" ? "dark" : "light";
    showToast("Theme switched");
  });

  toggleDebugBtn.addEventListener("click", ()=>{
    showDebug = !showDebug;
    toggleDebugBtn.textContent = `Debug: ${showDebug ? "ON" : "OFF"}`;
    showToast(`Debug ${showDebug ? "ON" : "OFF"}`);
  });

  clearChat();
  renderHistory();
</script>
</body>
</html>
"""

# ==========================================================
# 2) Routes
# ==========================================================

@app.get("/")
def home():
    return Response(HTML_PAGE, mimetype="text/html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


@app.post("/api/chat")
def api_chat():
    try:
        data = request.get_json(force=True) or {}
        question = (data.get("question") or "").strip()
        mode = (data.get("mode") or "vanilla").strip().lower()

        if not question:
            return jsonify({"error": "Question is required."}), 400
        if mode not in {"vanilla", "agentic"}:
            return jsonify({"error": "Mode must be 'vanilla' or 'agentic'."}), 400

        if mode == "vanilla":
            out = vanilla_rag_answer(question)
            resp = {
                "mode": "vanilla",
                "question": question,
                "answer": out.get("answer", ""),
                "sources": out.get("sources", []),
            }
        else:
            out = agentic_rag_answer(question)
            resp = {
                "mode": "agentic",
                "question": question,
                "answer": out.get("answer", ""),
                "sources": out.get("sources", []),
                "debug": out.get("debug", {}),
            }

        return jsonify(resp)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    print("\n=========================================")
    print(" Colour Web Chat running locally")
    print(" Open: http://127.0.0.1:5000")
    print("=========================================\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
