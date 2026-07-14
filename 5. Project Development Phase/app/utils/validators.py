from pydantic import BaseModel, Field
from typing import Optional


class QARequest(BaseModel):
	question: str = Field(min_length=1)
	context: Optional[str] = None


class ExplainRequest(BaseModel):
	topic: str = Field(min_length=1)
	level: Optional[str] = Field(default="beginner", description="beginner|intermediate|advanced")


class QuizRequest(BaseModel):
	topic: str = Field(min_length=1)
	num_questions: Optional[int] = Field(default=5, ge=1, le=50)
	difficulty: Optional[str] = Field(default="medium")


class SummarizeRequest(BaseModel):
	text: str = Field(min_length=1)
	max_length: Optional[int] = Field(default=200, ge=50)


class RoadmapRequest(BaseModel):
	subject: str = Field(min_length=1)
	goals: Optional[str] = None
	duration_weeks: Optional[int] = Field(default=8, ge=1, le=52)


class BaseResponse(BaseModel):
	success: bool = True
	markdown: Optional[str] = None
	text: Optional[str] = None
	meta: Optional[dict] = None
