import json

from agents.base import load_prompt
from core.llm import call_llm
from core.session import SessionState


class CoachAgent:
    def __init__(self) -> None:
        self.system_prompt = load_prompt("coach.md")

    def generate_feedback(self, state: SessionState) -> str:
        user_prompt = json.dumps(
            {
                "session": state.summary(),
                "instruction": "Generate final structured feedback in Markdown.",
            },
            indent=2,
        )
        return call_llm(self.system_prompt, user_prompt, temperature=0.4)
