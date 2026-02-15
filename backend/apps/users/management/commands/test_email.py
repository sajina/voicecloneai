
import socket
import smtplib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail

class Command(BaseCommand):
    help = "Test email connectivity directly"

    def handle(self, *args, **options):
        print("\n--- EMAIL DIAGNOSTICS ---")
        
        # 1. Check settings
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        
        host = settings.EMAIL_HOST
        port = int(settings.EMAIL_PORT)
        
        # 2. DNS Resolution
        print(f"\n[1/3] Resolving {host}...")
        try:
            # This uses getaddrinfo which might be patched by our settings.py
            addr_info = socket.getaddrinfo(host, port)
            ip = addr_info[0][4][0]
            print(f"Success! Resolved to: {ip} (Family: {addr_info[0][0]})")
        except Exception as e:
            print(f"FAILED DNS Resolution: {e}")
            # Try unpatched resolution just to see
            try:
                print("Trying raw socket.gethostbyname...")
                raw_ip = socket.gethostbyname(host)
                print(f"Raw resolution: {raw_ip}")
            except:
                pass
            return

        # 3. Connectivity Test
        print(f"\n[2/3] Connecting to {host}:{port}...")
        try:
            sock = socket.create_connection((host, port), timeout=10)
            print("Success! socket.create_connection worked.")
            sock.close()
        except Exception as e:
            print(f"FAILED Connection: {e}")
            # Try alternate port
            alt_port = 465 if port == 587 else 587
            print(f"Trying alternate port {alt_port} just in case...")
            try:
                sock = socket.create_connection((host, alt_port), timeout=5)
                print(f"Success on alternate port {alt_port}!")
                sock.close()
            except:
                print(f"Failed on {alt_port} too.")
            return

        # 4. SMTP Login Test
        print(f"\n[3/3] Testing SMTP Login...")
        try:
            if getattr(settings, 'EMAIL_USE_SSL', False):
                print("Using SMTP_SSL...")
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else:
                print("Using SMTP...")
                server = smtplib.SMTP(host, port, timeout=10)
                if settings.EMAIL_USE_TLS:
                    print("Starting TLS...")
                    server.starttls()
            
            print(f"Logging in as {settings.EMAIL_HOST_USER}...")
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print("Success! Logged in to SMTP server.")
            server.quit()
        except Exception as e:
            print(f"FAILED SMTP Login: {e}")
            return

        print("\nDIAGNOSTICS COMPLETE: All systems appear functional.")
