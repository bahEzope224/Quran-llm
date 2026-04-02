import asyncio
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_pipeline import run_rag_pipeline
from app.models.schemas import ChatRequest, UserProfile

async def test_tafsir_coupling():
    print("\n--- TEST: Couplage Verset/Tafsir & Filtrage Hadiths ---")
    
    profile = UserProfile(legal_school="maliki", language="fr", mode="strict")
    payload = ChatRequest(question="Est-ce que la priere est obligatoire ?", profile=profile)
    
    print(f"Question: {payload.question}")
    response = run_rag_pipeline(payload)
    
    print("\nREPONSE:")
    print(response.answer)
    
    print("\nSOURCES RETENUES:")
    for i, source in enumerate(response.sources, 1):
        print(f"  {i}. [{source.type}] {source.source} ({source.ref})")
        # Verifier si on a du bruit
        if "901" in source.ref:
            print("  ⚠️ ERREUR: Le hadith sur la pluie (901) est toujours present !")
            
    # Verification du couplage 2:43 -> Ibn Kathir 2:43
    refs = [s.ref for s in response.sources]
    has_243 = "2:43" in refs
    has_tafsir_243 = any("Ibn Kathir 2:43" in r for r in refs)
    
    if has_243 and has_tafsir_243:
        print("\n✅ SUCCES: Le verset 2:43 est correctement couple a son Tafsir.")
    elif has_243:
        print("\n❌ ECHEC: Le verset 2:43 est present mais PAS son Tafsir.")
    else:
        print("\n❓ NOTE: Le verset 2:43 n'a pas ete retenu par le retriever.")

    # Verifier si 901 est absent
    if not any("901" in r for r in refs):
        print("✅ SUCCES: Le hadith bruite (Bukhari 901) a ete elimine.")

if __name__ == "__main__":
    asyncio.run(test_tafsir_coupling())
