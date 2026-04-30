from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["easy", "medium", "hard"]
AnswerType = Literal["strong", "partial", "vague", "off_topic", "unknown"]
NextAction = Literal["ask_follow_up", "ask_new_question", "increase_difficulty", "decrease_difficulty", "finish"]


class TurnEvaluation(BaseModel):
    answer_type: AnswerType
    relevance: int = Field(ge=1, le=5)
    depth: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    role_alignment: int = Field(ge=1, le=5)
    communication: int = Field(ge=1, le=5)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    suggested_probe: str = ""
    rationale: str


class OrchestrationDecision(BaseModel):
    next_action: NextAction
    difficulty: Difficulty
    focus_for_next_question: str
    reason: str
    should_finish: bool = False


class InterviewTurn(BaseModel):
    number: int
    question: str
    answer: str
    difficulty: Difficulty
    evaluation: TurnEvaluation
