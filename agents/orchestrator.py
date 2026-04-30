import json
import re

from pydantic import ValidationError

from agents.base import load_prompt
from core.llm import call_llm
from core.schemas import OrchestrationDecision
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


class OrchestratorAgent:
    def __init__(self) -> None:
        self.system_prompt = load_prompt("orchestrator.md")

    def decide(self, state: SessionState) -> OrchestrationDecision:
        if len(state.turns) >= state.total_turns:
            return OrchestrationDecision(
                next_action="finish",
                difficulty=state.difficulty,
                focus_for_next_question="",
                reason="Configured turn limit reached.",
                should_finish=True,
            )

        user_prompt = json.dumps(
            {
                "session": state.summary(),
                "remaining_turns": state.total_turns - len(state.turns),
                "required_schema": OrchestrationDecision.model_json_schema(),
            },
            indent=2,
        )
        raw = call_llm(self.system_prompt, user_prompt, temperature=0.2)
        try:
            decision = OrchestrationDecision.model_validate(_extract_json(raw))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise RuntimeError(f"Orchestrator returned invalid JSON: {raw}") from exc

        if len(state.turns) + 1 >= state.total_turns:
            decision.should_finish = False
        return decision
