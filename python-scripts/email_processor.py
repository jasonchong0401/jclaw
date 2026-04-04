import imaplib
from email.parser import BytesParser
from email.policy import default
import os

# 邮箱配置
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "jclaw003448@gmail.com"
PASSWORD = os.getenv("GMAIL_PASSWORD")

def fetch_emails():
    # 连接到IMAP服务器
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    print("Connecting to Gmail...")
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    print("Successfully logged in to Gmail.")
    mail.select("inbox")
    print("Selected inbox.")

    # 搜索未读邮件
    status, messages = mail.search(None, "(UNSEEN)")
    print(f"Search status: {status}, Number of unread emails: {len(messages[0].split()) if messages else 0}")
    
    email_ids = messages[0].split()
    emails = []
    for e_id in email_ids:
        # 获取邮件内容
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                email_content = BytesParser(policy=default).parsebytes(response_part[1])
                emails.append(email_content)
    mail.logout()
    print("Logged out from Gmail.")
    return emails

# 示例：获取未读邮件
emails = fetch_emails()
if not emails:
    print("No unread emails found.")
else:
    print(f"Found {len(emails)} unread email(s):")
    for i, email in enumerate(emails, 1):
        email_from = email.get("from", "Unknown Sender")
        email_subject = email.get("subject", "No Subject")
        email_body = email.get_body(preferencelist=("plain",))
        email_body_content = email_body.get_content() if email_body else "No plain text body"

        print(f"\nEmail {i}:")
        print(f"From: {email_from}")
        print(f"Subject: {email_subject}")
        print(f"Body: {email_body_content}")
