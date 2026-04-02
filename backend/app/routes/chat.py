from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.services.feedback import save_feedback
from app.services.rag_pipeline import run_rag_pipeline

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    return run_rag_pipeline(payload)


@router.post("/feedback")
async def post_feedback(payload: FeedbackRequest) -> dict[str, str]:
    success = save_feedback(payload)
    return {"status": "success" if success else "error"}
