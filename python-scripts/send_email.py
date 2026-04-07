#!/usr/bin/env python3
"""
发送邮件脚本
使用 Gmail SMTP 服务
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# 邮箱配置
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "jclaw003448@gmail.com"
SENDER_PASSWORD = os.getenv("GMAIL_PASSWORD")

def send_email(to_email, subject, body):
    """
    发送邮件

    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        body: 邮件内容

    Returns:
        bool: 是否发送成功
    """
    if not SENDER_PASSWORD:
        print("❌ 错误: 未设置 GMAIL_PASSWORD 环境变量")
        return False

    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # 连接到 SMTP 服务器
        print(f"正在连接到 {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # 启用 TLS 加密

        # 登录
        print("正在登录...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # 发送邮件
        print(f"正在发送邮件到 {to_email}...")
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)

        # 关闭连接
        server.quit()

        print(f"✅ 邮件发送成功！")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ 认证失败: 请检查 Gmail 密码或应用专用密码")
        return False
    except Exception as e:
        print(f"❌ 发送邮件失败: {e}")
        return False

if __name__ == '__main__':
    # 测试发送邮件
    recipient = "jason0401chong@gmail.com"
    subject = "Hello Test"
    body = "hello test"

    print("=" * 60)
    print("📧 发送邮件测试")
    print("=" * 60)
    print(f"发件人: {SENDER_EMAIL}")
    print(f"收件人: {recipient}")
    print(f"主题: {subject}")
    print(f"内容: {body}")
    print("=" * 60)

    success = send_email(recipient, subject, body)

    if success:
        print("\n✅ 测试完成！")
    else:
        print("\n❌ 测试失败！")
        print("\n提示: 如果遇到认证错误，请：")
        print("1. 确保已设置 GMAIL_PASSWORD 环境变量")
        print("2. 如果使用普通密码，需要在 Gmail 设置中开启'允许不太安全的应用'")
        print("3. 推荐使用应用专用密码: https://myaccount.google.com/apppasswords")