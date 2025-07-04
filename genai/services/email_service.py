import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

GMAIL_USER = os.environ.get("GMAIL_USER", "testasnode@gmail.com")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "ncbbgnwyljozujpj")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

async def send_verification_link(email: str, link: str):
    subject = "Hospital Claim Verification Required"
    body = f"Please verify the claim by uploading the required medical documents and bill using the following link: {link}"

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        raise 