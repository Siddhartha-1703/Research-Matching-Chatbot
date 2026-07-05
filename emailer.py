import os
import smtplib
from email.message import EmailMessage


def send_summary_email(to_emails, subject, body):
    """Send a plain-text summary email via SMTP. Reads credentials from env vars.

    Required env vars:
    - EMAIL_USER: sender email (e.g., your Gmail address)
    - EMAIL_PASS: app password or SMTP password
    - SMTP_SERVER (optional, default: smtp.gmail.com)
    - SMTP_PORT (optional, default: 587)
    """
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    user = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')

    if not user or not password:
        return {'ok': False, 'error': 'Missing EMAIL_USER or EMAIL_PASS environment variables.'}

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = ', '.join(to_emails) if isinstance(to_emails, (list,tuple)) else to_emails
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
