import os
import smtplib, ssl

smtp_server = "smtp.gmail.com"
port = 465
sender_email = os.getenv('AUTH_USER')
password = os.getenv('AUTH_PASS')

def send_email(recipient, title, content):
    message = f"""Subject: {title}

    {content}
    """

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient, message)
