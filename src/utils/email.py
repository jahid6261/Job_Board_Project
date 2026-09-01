import smtplib
from email.mime.text import MIMEText
from src.utils.settings import settings

EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT
EMAIL_USER = settings.EMAIL_USER
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_FROM = settings.EMAIL_FROM


def email_utility(email_to: str, email_subject: str, email_body: str):
    msg = MIMEText(email_body)
    msg["Subject"] = email_subject
    msg["From"] = EMAIL_FROM
    msg["To"] = email_to

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        return {"success": True, "message": f"Email sent to {email_to}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def send_activation_email(to_email: str, first_name: str, activation_token: str):
    activation_url = f"{settings.FRONTEND_URL}/activate?token={activation_token}"

    email_body = f"""
Hello {first_name},

Welcome to Job Board!

Your account has been created successfully.

Please click the link below to activate your account:

{activation_url}

After activating your account, you will be able to login.

If you did not create this account, please ignore this email.

Best regards,
Job Board Team
"""

    return email_utility(
        email_to=to_email,
        email_subject="Activate Your Job Board Account",
        email_body=email_body,
    )





def send_password_reset_otp_email(to_email: str, first_name: str, otp: str):
    email_body = f"""
Hello {first_name},

We received a request to reset your Job Board account password.

Your password reset OTP is:

{otp}

This OTP will expire in 5 minutes.

If you did not request a password reset, you can safely ignore this email.

Best regards,
Job Board Team
"""

    return email_utility(
        email_to=to_email,
        email_subject="Your Job Board Password Reset OTP",
        email_body=email_body,
    )