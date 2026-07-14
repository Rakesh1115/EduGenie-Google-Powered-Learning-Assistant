from fastapi import APIRouter, HTTPException, status

from ..services.gemini_service import GeminiServiceError, get_gemini_service
from ..services import prompt_engineering, formatter
from ..utils.validators import QuizRequest, BaseResponse

router = APIRouter(prefix="/quiz")


@router.post("/", response_model=BaseResponse)
def generate_quiz(payload: QuizRequest):
    try:
        svc = get_gemini_service()
        prompt = prompt_engineering.quiz_prompt(payload.topic, payload.num_questions or 5, payload.difficulty or "medium")
        raw = svc.generate(prompt)
        out = formatter.format_markdown(raw)
        # try to parse quiz items
        meta = formatter.extract_quiz_items(out["markdown"])
        return BaseResponse(success=True, markdown=out["markdown"], text=out["text"], meta=meta)
    except GeminiServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The AI service is unavailable.") from exc
