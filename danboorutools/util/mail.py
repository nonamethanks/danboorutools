import smtplib
from email.message import EmailMessage


def send_email(*,
               send_to: str,
               message: str,
               subject: str | None = None) -> None:
    """Send an email."""

    email = EmailMessage()
    email.set_content(message)
    email["Subject"] = subject
    email["From"] = send_to
    email["To"] = send_to

    server = smtplib.SMTP("mail", 25)
    server.send_message(email)
    server.quit()
