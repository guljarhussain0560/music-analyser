from fastapi import APIRouter

from app.dto.schemas import ChatRequest, ChatResponse
from app.utils.chatbot import get_ai_answer

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("/ask", response_model=ChatResponse)
async def ask_maestro(request: ChatRequest) -> ChatResponse:
    """Submits a question to Maestro AI music analysis assistant."""
    answer = await get_ai_answer(request.question)
    return ChatResponse(answer=answer)
