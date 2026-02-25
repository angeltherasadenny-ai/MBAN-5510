import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

from research_agent import research_michael
from email_writer_agent import write_email
from email_sender import send_email

# Load .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # allows your HTML page to call the API


@app.get("/")
def home():
    return "Server running. Use /api/research, /api/draft, /api/send"


@app.post("/api/research")
def api_research():
    profile_url = os.getenv("MICHAEL_PROFILE_URL", "").strip()
    if not profile_url:
        return jsonify({"error": "MICHAEL_PROFILE_URL missing in .env"}), 400

    try:
        research = research_michael(profile_url)
        professor_name = research.get("name", "Michael Zhang")
        return jsonify({"ok": True, "professor_name": professor_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/draft")
def api_draft():
    profile_url = os.getenv("MICHAEL_PROFILE_URL", "").strip()
    if not profile_url:
        return jsonify({"error": "MICHAEL_PROFILE_URL missing in .env"}), 400

    data = request.get_json(silent=True) or {}
    student = data.get("student", {})

    # Basic validation
    if not student.get("name") or not student.get("program") or not student.get("university"):
        return jsonify({"error": "Student name/program/university required"}), 400

    try:
        research = research_michael(profile_url)
        draft = write_email(student, research)

        return jsonify({
            "ok": True,
            "subject": draft["subject"],
            "body": draft["body"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/api/send")
def api_send():
    data = request.get_json(silent=True) or {}
    subject = (data.get("subject") or "").strip()
    body = (data.get("body") or "").strip()

    if not subject or not body:
        return jsonify({"error": "Subject and body cannot be empty"}), 400

    test_receiver = os.getenv("TEST_RECEIVER", "Michael.Zhang@smu.ca").strip()

    try:
        send_email(subject, body, test_receiver)
        return jsonify({"ok": True, "to": test_receiver})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
