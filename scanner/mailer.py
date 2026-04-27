import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_email_with_attachment(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Path,
) -> None:
    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with open(attachment_path, "rb") as file_obj:
        data = file_obj.read()

    msg.add_attachment(
        data,
        maintype="application",
        subtype="zip",
        filename=attachment_path.name,
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)