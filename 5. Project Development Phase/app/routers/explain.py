from fastapi import APIRouter, HTTPException, status

from ..services.gemini_service import GeminiServiceError, get_gemini_service
from ..services import prompt_engineering, formatter
from ..utils.validators import ExplainRequest, BaseResponse

router = APIRouter(prefix="/explain")


@router.post("/", response_model=BaseResponse)
def explain_concept(payload: ExplainRequest):
    try:
        svc = get_gemini_service()
        prompt = prompt_engineering.explain_prompt(payload.topic, payload.level)
        raw = svc.generate(prompt)
        out = formatter.format_markdown(raw)
        return BaseResponse(success=True, markdown=out["markdown"], text=out["text"])
    except GeminiServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The AI service is unavailable.") from exc
