from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_pipeline import run_rag_pipeline


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    return run_rag_pipeline(payload)
