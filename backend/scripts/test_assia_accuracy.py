from app.models.schemas import ChatRequest, UserProfile
from app.services.rag_pipeline import run_rag_pipeline

def test_assia_accuracy():
    profile = UserProfile(
        legal_school="maliki",
        language="fr",
        mode="response",
        notifications_enabled=True
    )
    
    # Question sur Assia qui avait cause l'hallucination precedemment
    payload = ChatRequest(
        question="qui etait assia ?",
        mode="proofs",
        profile=profile
    )
    
    print("\n--- TEST RIGUEUR HISTORIQUE : ASSIA ---")
    response = run_rag_pipeline(payload)
    
    print(f"QUESTION: {payload.question}")
    print(f"REPONSE: {response.answer}")
    
    print("\nSOURCES TROUVEES:")
    for i, source in enumerate(response.sources):
        print(f"{i+1}. [{source.type.upper()}] {source.ref} - {source.source}")
        # On verifie si "Aisha" ou "Aicha" est dans les sources par erreur
        if "aisha" in source.text.lower() or "aicha" in source.text.lower():
            print("   WARNING: Confusion avec Aisha detectee dans cette source !")
        else:
            print("   INFO: Source pertinente (non-Aicha).")

    # On verifie si le verset 66:11 (Assia) est remonte
    has_assia_verse = any("66:11" in s.ref for s in response.sources)
    if has_assia_verse:
        print("\nSUCCESS: Le verset 66:11 (Assia) a bien ete identifie par le retriever.")
    else:
        print("\nINFO: Le verset 66:11 n'est pas remonte, mais verifions si Aisha a ete evitee.")

if __name__ == "__main__":
    test_assia_accuracy()
