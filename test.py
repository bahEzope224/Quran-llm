# test.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger le .env
load_dotenv()

# Initialiser le client
client = OpenAI()   # Il lit automatiquement OPENAI_API_KEY depuis l'environnement

def test_openai():
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant de test. Réponds toujours de façon très courte et directe."},
                {"role": "user",   "content": "Dis seulement : API OK"}
            ],
            max_tokens=20,
            temperature=0.0   # On force une réponse déterministe
        )

        message = response.choices[0].message.content.strip()

        print("\n" + "="*60)
        if "API OK" in message:
            print("✅ TEST RÉUSSI - L'API OpenAI fonctionne parfaitement !")
        else:
            print("⚠️  L'API répond, mais pas exactement comme attendu.")

        print(f"Réponse reçue : {message}")
        print(f"Modèle utilisé : {response.model}")
        print(f"Tokens utilisés : {response.usage.total_tokens}")
        print("="*60)

    except Exception as e:
        print("\n❌ ERREUR lors de l'appel à l'API :")
        print(e)

if __name__ == "__main__":
    test_openai()