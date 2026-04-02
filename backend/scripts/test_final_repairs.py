import sys
import os

# Ajout du chemin pour importer les modules de l'app
sys.path.append(os.getcwd())

from app.services.rag_pipeline import run_rag_pipeline
from app.models.schemas import ChatRequest, UserProfile

def run_test(question: str):
    print("-" * 50)
    print(f"TEST: {question}")
    
    profile = UserProfile(
        legal_school="Maliki",
        language="French",
        mode="Reliable",
        notifications_enabled=True
    )
    request = ChatRequest(question=question, profile=profile)
    response = run_rag_pipeline(request)
    
    print(f"REPONSE: {response.answer}")
    print("\nSOURCES:")
    for i, s in enumerate(response.sources, 1):
        print(f"  {i}. [{s.type}] {s.ref}")
    print("-" * 50)

if __name__ == "__main__":
    # Test 1: Prière (Correction de la mention Coran)
    run_test("Est-ce que la prière est obligatoire ?")
    
    # Test 2: Pharaon (Correction de la coupure biographie)
    run_test("Qui était Pharaon ?")
