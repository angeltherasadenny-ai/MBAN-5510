import os
import ssl
import smtplib
from email.message import EmailMessage


def send_email(subject: str, body: str, to_email: str) -> None:
    sender = os.getenv("GMAIL_ADDRESS", "").strip()
    password = os.getenv("GMAIL_APP_PASSWORD", "").strip()

    if not sender or not password:
        print("ERROR: Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("Email sent successfully.")
