import json

from agents.base import load_prompt
from core.llm import call_llm
from core.session import SessionState


class InterviewerAgent:
    def __init__(self) -> None:
        self.system_prompt = load_prompt("interviewer.md")

    def ask_question(self, state: SessionState, focus_for_next_question: str) -> str:
        user_prompt = json.dumps(
            {
                "session": state.summary(),
                "focus_for_next_question": focus_for_next_question,
                "instruction": "Ask exactly one interview question. Return only the question text.",
            },
            indent=2,
        )
        return call_llm(self.system_prompt, user_prompt, temperature=0.7).strip().strip('"')
