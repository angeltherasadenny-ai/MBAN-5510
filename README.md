# 🌸 Research Email Assistant

A Human-in-the-Loop (HITL) research email drafting system that: -
Researches a professor profile\
- Generates a structured email draft\
- Allows human approval/editing\
- Sends the email to a test receiver

Built using Flask (backend) and HTML/CSS/JS (frontend).

------------------------------------------------------------------------

## 📌 Project Overview

This system automates the workflow of contacting a professor for
research opportunities while keeping the human fully in control before
sending.

### Workflow

1.  🔎 Research professor profile\
2.  ✨ Generate email draft\
3.  ✏️ Human reviews/edits (approval step)\
4.  📨 Send to test receiver

------------------------------------------------------------------------

## 🗂 Project Structure

    ├── server.py               # Flask API server
    ├── main.py                 # CLI version (terminal-based)
    ├── research_agent.py       # Scrapes professor name
    ├── email_writer_agent.py   # Generates structured email draft
    ├── approval_agent.py       # Human approval loop (CLI)
    ├── email_sender.py         # Sends email using Gmail SMTP
    ├── index.html              # Professional UI
    ├── requirements.txt        # Dependencies
    ├── .env                    # Environment variables (not committed)

------------------------------------------------------------------------

## ⚙️ Backend (Flask API)

Run the backend server:

    python server.py

Server runs on:

    http://127.0.0.1:5000

Available endpoints: - `/api/research` - `/api/draft` - `/api/send`

------------------------------------------------------------------------

## 🎨 Frontend (HTML UI)

Open `index.html` in your browser after starting the backend.

Features: - Modern professional UI - Draft regeneration - Editable
subject/body (HITL) - API status messages - Clear Draft → Edit → Send
workflow

------------------------------------------------------------------------

## 📧 Email Sending

Uses Gmail SMTP with SSL and App Password authentication.

Make sure to configure your `.env` file properly.

------------------------------------------------------------------------

## 🔐 Environment Variables (.env)

Create a `.env` file in the root folder:

    GMAIL_ADDRESS=your_email@gmail.com
    GMAIL_APP_PASSWORD=your_app_password
    TEST_RECEIVER=Michael.Zhang@smu.ca

    MICHAEL_PROFILE_URL=https://www.smu.ca/researchers/sobey/profiles/michael-zhang.html

    STUDENT_NAME=Angel Denny
    STUDENT_PROGRAM=MBAN
    STUDENT_UNIVERSITY=Saint Mary's University

⚠️ Do NOT commit `.env` to GitHub.

------------------------------------------------------------------------

## 🧰 Installation

Install dependencies:

    pip install -r requirements.txt

------------------------------------------------------------------------

## 🏗 Technologies Used

-   Python
-   Flask
-   Flask-CORS
-   BeautifulSoup
-   Requests
-   SMTP (Gmail)
-   HTML5
-   CSS
-   JavaScript

------------------------------------------------------------------------

## 🚀 Future Improvements

-   Support multiple professors
-   Tone customization
-   Email logging system
-   Deployment to cloud hosting
