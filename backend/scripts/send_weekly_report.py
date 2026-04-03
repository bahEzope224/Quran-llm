import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ajout du dossier parent au path pour importer les modules de l'app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.email_service import send_feedback_summary_email

# Configuration
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
ADMIN_EMAIL = "contact@ibrahima-bah.com"

def generate_weekly_report():
    if not FEEDBACK_FILE.exists():
        print("❌ Aucun feedback a traiter.")
        return

    # 1. Calcul de la periode (7 derniers jours)
    now = datetime.utcnow()
    last_week = now - timedelta(days=7)
    
    feedbacks = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            ts = datetime.fromisoformat(record["timestamp"])
            if ts >= last_week:
                feedbacks.append(record)

    if not feedbacks:
        print("📭 Aucun feedback enregistre cette semaine.")
        return

    # 2. Statistiques
    total = len(feedbacks)
    up = sum(1 for f in feedbacks if f["feedback"] == "up")
    down = sum(1 for f in feedbacks if f["feedback"] == "down")
    neg_with_comments = [f for f in feedbacks if f["feedback"] == "down" and f.get("comment")]

    # 3. Generation du HTML
    html = f"""
    <div style="font-family: sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
        <h2 style="color: #2a6746; text-align: center;">📊 Rapport Hebdomadaire ILM AI</h2>
        <p style="text-align: center; color: #666;">Periode : {last_week.strftime('%d/%m/%Y')} au {now.strftime('%d/%m/%Y')}</p>
        
        <div style="display: flex; justify-content: space-around; background: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <div style="text-align: center;">
                <b style="font-size: 20px; color: #101828;">{total}</b><br/>Total
            </div>
            <div style="text-align: center;">
                <b style="font-size: 20px; color: #2a6746;">{up}</b><br/>Utiles 👍
            </div>
            <div style="text-align: center;">
                <b style="font-size: 20px; color: #d92d20;">{down}</b><br/>Imprecis 👎
            </div>
        </div>

        <h3>⚠️ Retours Critiques (Commentaires)</h3>
        { "".join([f'<div style="border-left: 4px solid #d92d20; padding: 10px; margin-bottom: 10px; background: #fffcfc;"><p><b>Question:</b> {f["question"]}</p><p><b>Critique:</b> {f["comment"]}</p></div>' for f in neg_with_comments[:10]]) if neg_with_comments else "<p>Aucun commentaire negatif cette semaine. MashaAllah !</p>" }
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="https://quran-llm.vercel.app/admin" style="background: #2a6746; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">Acceder au Panneau Admin</a>
        </div>
    </div>
    """

    # 4. Envoi de l'email
    success = send_feedback_summary_email(ADMIN_EMAIL, html)
    if success:
        print(f"✅ Rapport hebdomadaire envoye avec succes a {ADMIN_EMAIL}")
    else:
        print("❌ Echec de l'envoi du rapport.")

if __name__ == "__main__":
    generate_weekly_report()
