"""
services/email_service.py
Envoi d'emails via SMTP (configurable dans .env).
Compatible avec tout provider SMTP : Gmail, Brevo, Resend, Mailgun, etc.
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ── Configuration depuis .env ─────────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM     = os.getenv("SMTP_FROM", SMTP_USER)   # ex: "Festival Horizons <noreply@festival.fr>"
SMTP_USE_TLS  = os.getenv("SMTP_USE_TLS", "true").lower() == "true"


class EmailError(Exception):
    """Levée quand l'envoi échoue pour un destinataire."""
    pass


def send_html_email(
    to_email: str,
    subject: str,
    html_body: str,
    attachment_bytes: Optional[bytes] = None,
    attachment_filename: str | None = "planning.pdf",
) -> None:
    """
    Envoie un email HTML avec, optionnellement, une pièce jointe HTML.

    Args:
        to_email:            Adresse du destinataire.
        subject:             Objet du mail.
        html_body:           Corps HTML du mail.
        attachment_html:     Contenu HTML de la pièce jointe (planning perso).
        attachment_filename: Nom du fichier joint.

    Raises:
        EmailError: si l'envoi échoue.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        raise EmailError(
            "SMTP_USER et SMTP_PASSWORD ne sont pas configurés dans le fichier .env"
        )

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = SMTP_FROM
    msg["To"]      = to_email

    # Corps du mail (texte alternatif + HTML)
    body_part = MIMEMultipart("alternative")
    body_part.attach(MIMEText(_html_to_plain(html_body), "plain", "utf-8"))
    body_part.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(body_part)

    if attachment_bytes:
        attachment = MIMEBase("application", "pdf")
        attachment.set_payload(attachment_bytes)
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=attachment_filename,
        )
        msg.attach(attachment)

    try:
        if SMTP_USE_TLS:
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, to_email, msg.as_bytes())
        else:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, to_email, msg.as_bytes())

    except smtplib.SMTPAuthenticationError as e:
        raise EmailError(f"Authentification SMTP échouée : {e}") from e
    except smtplib.SMTPRecipientsRefused as e:
        raise EmailError(f"Adresse refusée par le serveur : {to_email}") from e
    except smtplib.SMTPException as e:
        raise EmailError(f"Erreur SMTP : {e}") from e
    except Exception as e:
        raise EmailError(f"Erreur inattendue : {e}") from e


def _html_to_plain(html: str) -> str:
    """Conversion basique HTML → texte brut pour le fallback plain-text."""
    import re
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()