import json
import re

from pydantic import ValidationError

from agents.base import load_prompt
from core.llm import call_llm
from core.schemas import TurnEvaluation
from core.session import SessionState


def _extract_json(text: str) -> dict[str, object]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


class EvaluatorAgent:
    def __init__(self) -> None:
        self.system_prompt = load_prompt("evaluator.md")

    def evaluate(self, state: SessionState, question: str, answer: str) -> TurnEvaluation:
        user_prompt = json.dumps(
            {
                "session": state.summary(),
                "question": question,
                "answer": answer,
                "required_schema": TurnEvaluation.model_json_schema(),
            },
            indent=2,
        )
        raw = call_llm(self.system_prompt, user_prompt, temperature=0.2)
        try:
            return TurnEvaluation.model_validate(_extract_json(raw))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise RuntimeError(f"Evaluator returned invalid JSON: {raw}") from exc
