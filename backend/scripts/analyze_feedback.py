import json
import pandas as pd
from pathlib import Path
from collections import Counter

# Configuration
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
REPORT_FILE = DATA_DIR / "feedback_report.csv"

def analyze():
    if not FEEDBACK_FILE.exists():
        print(f"❌ Aucun fichier de feedback trouve a {FEEDBACK_FILE}")
        return

    records = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    if not records:
        print("📭 Le fichier de feedback est vide.")
        return

    df = pd.DataFrame(records)
    
    # Statistiques globales
    total = len(df)
    stats = df['feedback'].value_counts()
    pos = stats.get('up', 0)
    neg = stats.get('down', 0)

    print("\n--- 📊 RAPPORT DE PERFORMANCE ILM AI ---")
    print(f"Total des feedbacks : {total}")
    print(f"👍 Utiles (Up)      : {pos} ({pos/total:.1%})")
    print(f"👎 Imprecis (Down)  : {neg} ({neg/total:.1%})")
    
    # Analyse des commentaires pour les "Down"
    print("\n--- 💬 RETOURS UTILISATEURS (CRITIQUES) ---")
    neg_with_comments = df[(df['feedback'] == 'down') & (df['comment'].str.len() > 0)]
    
    if not neg_with_comments.empty:
        for _, row in neg_with_comments.iterrows():
            print(f"- Question : {row['question'][:60]}...")
            print(f"  Commentaire : {row['comment']}")
            print(f"  Sources citees : {[s['ref'] for s in row['sources']]}")
            print("-" * 30)
    else:
        print("Aucun commentaire detaille pour le moment.")

    # Exportation pour analyse approfondie (Excel/CSV)
    df.to_csv(REPORT_FILE, index=False)
    print(f"\n✅ Rapport detaille exporte dans : {REPORT_FILE}")

    # Guide d'amelioration RAG
    print("\n--- 🚀 COMMENT AMELIORER LE RAG ? ---")
    print("1. SI LA SOURCE MANQUE : Ajoutez les documents manquants dans 'data/' et relancez l'ingestion.")
    print("2. SI LE LLM HALLUCINE : Ajustez le System Prompt dans 'rag_pipeline.py' pour etre plus strict.")
    print("3. SI LA SOURCE EST MAUVAISE : Verifiez le 'chunking' (decoupage) des textes originaux.")

if __name__ == "__main__":
    analyze()
