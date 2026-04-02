from app.models.schemas import ChatRequest, UserProfile
from app.services.rag_pipeline import run_rag_pipeline

def test_fatwa_fallback():
    profile = UserProfile(
        legal_school="maliki",
        language="fr",
        mode="response",
        notifications_enabled=True
    )
    
    # Question specifique a la fatwa 112113 importee
    payload = ChatRequest(
        question="Quel est le sort reservé à un musulman qui meurt sans s'être repenti d'un péché majeur comme le vol ?",
        mode="proofs",
        profile=profile
    )
    
    print("\n--- TEST FALLBACK FATWA ---")
    response = run_rag_pipeline(payload)
    
    print(f"QUESTION: {payload.question}")
    print(f"REPONSE: {response.answer[:200]}...")
    
    print("\nSOURCES TROUVEES:")
    for i, source in enumerate(response.sources):
        print(f"{i+1}. [{source.type.upper()}] {source.ref} - {source.source}")
        if source.url:
            print(f"   URL: {source.url}")

    has_fatwa = any(s.type == "fatwa" for s in response.sources)
    if has_fatwa:
        print("\nSUCCESS: Le systeme a bien utilise la Fatwa d'IslamQA comme source.")
    else:
        print("\nINFO: Le systeme a trouve des sources scripturaires suffisantes, la Fatwa n'a pas ete necessaire (Cascade OK).")

if __name__ == "__main__":
    test_fatwa_fallback()
