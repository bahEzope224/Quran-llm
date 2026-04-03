import os
import resend
from app.config import settings

# Configuration Resend
resend.api_key = os.getenv("RESEND_API_KEY", "")

def send_feedback_summary_email(recipient: str, summary_html: str):
    """Envoie le resume hebdomadaire des feedbacks."""
    if not resend.api_key:
        print("⚠️ RESEND_API_KEY manquante. Email non envoye.")
        return False
        
    try:
        r = resend.Emails.send({
            "from": "ILM AI Admin <admin@resend.dev>", # Changez par votre domaine verifie sur Resend
            "to": recipient,
            "subject": "📊 Resume Hebdomadaire ILM AI - feedbacks & Stats",
            "html": summary_html
        })
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        return False
