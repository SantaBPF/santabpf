import os
import smtplib
import ssl

smtp_server = "smtp.gmail.com"
port = 465
sender_email = os.getenv('AUTH_USER')
password = os.getenv('AUTH_PASS')


def send_email(recipient, title, content):
    message = f"""Subject: {title}
MIME-Version: 1.0
Content-type: text/html; charset=utf-8

<pre style="font: monospace">
{content}
</pre>
    """.encode('utf8')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient, message)


if __name__ == '__main__':
    send_email('dongho971220@gmail.com', 'test', '테스트 메시지 test message')
