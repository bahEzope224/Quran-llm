import sys
import os
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_path))

try:
    from app.services.rag_pipeline import run_rag_pipeline
    from app.models.schemas import ChatRequest, UserProfile
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_seerah_marriage_age():
    print("Testing question: À quel âge le prophète Mohamed a marié Khadija")
    profile = UserProfile(
        legal_school="Maliki",
        language="Francais",
        mode="Clair",
        notifications_enabled=True
    )
    request = ChatRequest(
        question="À quel âge le prophète Mohamed a marié Khadija",
        profile=profile
    )
    response = run_rag_pipeline(request)
    
    print("\nANSWER:")
    print(response.answer)
    print("\nSOURCES:")
    for source in response.sources:
        print(f"- [{source.type}] {source.ref}: {source.text[:100]}...")

    if "25" in response.answer:
        print("\nSUCCESS: The answer correctly mentions 25 years old.")
    else:
        print("\nFAILURE: The answer does not mention 25 years old.")

if __name__ == "__main__":
    test_seerah_marriage_age()
