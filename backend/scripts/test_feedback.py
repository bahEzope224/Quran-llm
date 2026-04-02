import requests
import json
import os
from pathlib import Path

def test_feedback_submission():
    url = "http://127.0.0.1:8000/chat/feedback"
    payload = {
        "question": "Comment faire la priere ?",
        "answer": "La priere (Salat) se fait en plusieurs etapes...",
        "feedback": "up",
        "profile": {
            "legal_school": "Maliki",
            "language": "Francais",
            "mode": "Clair"
        }
    }
    
    print(f"Envoi du feedback a {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("SUCCES: L'endpoint a repondu positivement.")
            
            # Verifier le fichier local
            feedback_file = Path("data/feedback.jsonl")
            if feedback_file.exists():
                with open(feedback_file, "r", encoding="utf-8") as f:
                    last_line = f.readlines()[-1]
                    record = json.loads(last_line)
                    if record["question"] == payload["question"]:
                        print("SUCCES: Le feedback a ete correctement enregistre dans data/feedback.jsonl.")
                    else:
                        print("ERREUR: Le contenu du fichier ne correspond pas.")
            else:
                print("ERREUR: Le fichier data/feedback.jsonl n'existe pas.")
        else:
            print("ERREUR: Le serveur a renvoye une erreur.")
            
    except Exception as e:
        print(f"ERREUR: Connexion echouee : {e}")

if __name__ == "__main__":
    test_feedback_submission()
