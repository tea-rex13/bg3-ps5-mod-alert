import os, smtplib, ssl
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level above /src)
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)  # <- explicitly load the root .env

def send_email(subject, body):
    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_USER")
    pwd  = os.getenv("SMTP_PASS")
    to   = os.getenv("ALERT_TO")

    missing = [k for k, v in {
        "SMTP_HOST": host, "SMTP_PORT": port, "SMTP_USER": user,
        "SMTP_PASS": pwd,  "ALERT_TO": to
    }.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)} (loaded from {ENV_PATH})")

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, int(port)) as s:
        s.starttls(context=ssl.create_default_context())
        s.login(user, pwd)
        s.send_message(msg)
