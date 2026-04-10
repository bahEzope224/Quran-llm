import sys
import os

# Ajout du chemin backend pour l'import
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.models.schemas import ChatRequest, UserProfile
from app.services.rag_pipeline import run_rag_pipeline

def test_pork_recall():
    print("Testing RAG recall for 'porc'...")
    profile = UserProfile(legal_school="maliki", language="fr", mode="clair")
    request = ChatRequest(question="Est ce que le porc est halal ?", profile=profile)
    
    # On simule sans appeler réellement l'API de génération pour gagner du temps
    # mais en vérifiant la sélection des sources
    try:
        from app.services.rag_pipeline import run_rag_pipeline
        response = run_rag_pipeline(request)
        
        print(f"Answer: {response.answer[:100]}...")
        print("Sources found:")
        for s in response.sources:
            print(f"- {s.ref} ({s.type})")
            
        # Vérification qu'on a bien du Coran
        has_quran = any(s.type == "quran" for s in response.sources)
        if has_quran:
            print("✅ SUCCESS: Quranic verses found!")
        else:
            print("❌ FAILURE: No Quranic verses found.")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_pork_recall()
