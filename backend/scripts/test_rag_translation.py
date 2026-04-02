import sys
from pathlib import Path

# Ajouter le backend au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.schemas import ChatRequest
from app.services.rag_pipeline import run_rag_pipeline

def test_translation():
    print("--- TEST DE TRADUCTION DES SOURCES ---")
    request = ChatRequest(
        question="la priere est-il obligatoire",
        profile={"language": "Francais"}
    )
    
    response = run_rag_pipeline(request)
    
    print(f"\nQuestion : {request.question}")
    print(f"Reponse   : {response.answer[:100]}...")
    
    print("\nSources extraites (Verification traduction) :")
    for i, source in enumerate(response.sources):
        if source.type in ["tafsir", "hadith"]:
            print(f"- SOURCE {i} ({source.type} - {source.ref})")
            print(f"  Contenu (FR?) : {source.text[:200]}...")
            
    # Verification simple
    english_keywords = ["mandatory", "must", "the", "and", "is"]
    # On verifie les 3 premiers mots communs (heuristique simple)
    is_french = not any(word in response.sources[0].text.lower() for word in ["perform", "Salah", "Zakah"])
    
    if is_french:
        print("\n✅ SUCCES : Les sources semblent traduites en francais.")
    else:
        print("\n❌ ECHEC : Les sources sont encore en anglais.")

if __name__ == "__main__":
    test_translation()
