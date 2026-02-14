"""
Custom email backend using Resend Python SDK.
Bypasses SMTP entirely — works on Railway where SMTP ports are blocked.
"""

import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    """
    Send emails via Resend SDK (https://resend.com).
    
    Required settings:
        RESEND_API_KEY = 'your-api-key'
        DEFAULT_FROM_EMAIL = 'Your App <onboarding@resend.dev>'  (or verified domain)
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        api_key = getattr(settings, 'RESEND_API_KEY', None)
        if api_key:
            resend.api_key = api_key

    def send_messages(self, email_messages):
        if not resend.api_key:
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY is not set in Django settings.")
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                self._send(message)
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
        return sent_count

    def _send(self, message):
        params: resend.Emails.SendParams = {
            "from": message.from_email,
            "to": list(message.to),
            "subject": message.subject,
        }

        # Use HTML or plain text
        if hasattr(message, 'content_subtype') and message.content_subtype == 'html':
            params["html"] = message.body
        else:
            params["html"] = f"<p>{message.body}</p>"

        # Add CC and BCC if present
        if message.cc:
            params["cc"] = list(message.cc)
        if message.bcc:
            params["bcc"] = list(message.bcc)

        email = resend.Emails.send(params)
        return email
