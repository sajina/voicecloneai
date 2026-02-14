"""
Custom email backend using Resend HTTP API.
Bypasses SMTP entirely — works on Railway where SMTP ports are blocked.
"""

import json
import urllib.request
import urllib.error
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    """
    Send emails via Resend's HTTP API (https://resend.com).
    
    Required setting:
        RESEND_API_KEY = 'your-api-key'
    """

    api_url = 'https://api.resend.com/emails'

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)

    def send_messages(self, email_messages):
        if not self.api_key:
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
        payload = {
            'from': message.from_email,
            'to': list(message.to),
            'subject': message.subject,
            'text': message.body,
        }

        # Support HTML content
        if message.content_subtype == 'html':
            payload['html'] = message.body

        # Add CC and BCC if present
        if message.cc:
            payload['cc'] = list(message.cc)
        if message.bcc:
            payload['bcc'] = list(message.bcc)

        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            self.api_url,
            data=data,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )

        try:
            response = urllib.request.urlopen(req, timeout=30)
            return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"Resend API error ({e.code}): {error_body}")
