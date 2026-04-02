import sys
import os

# Ajout du chemin pour importer les modules de l'app
sys.path.append(os.getcwd())

from app.services.rag_pipeline import run_rag_pipeline
from app.models.schemas import ChatRequest, UserProfile

def test_biography():
    print("-" * 50)
    print("TEST: Biographie (Qui etait Pharaon ?)")
    print("-" * 50)
    
    profile = UserProfile(
        legal_school="Maliki",
        language="French",
        mode="Reliable",
        notifications_enabled=True
    )
    request = ChatRequest(question="Qui etait Pharaon ?", profile=profile)
    response = run_rag_pipeline(request)
    
    print(f"QUESTION: {request.question}")
    print(f"REPONSE: {response.answer}")
    print("\nSOURCES:")
    for i, s in enumerate(response.sources, 1):
        print(f"  {i}. [{s.type}] {s.ref}")
    print("-" * 50)

if __name__ == "__main__":
    test_biography()
