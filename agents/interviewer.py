import json

from agents.base import load_prompt
from core.llm import call_llm
from core.session import SessionState


class InterviewerAgent:
    def __init__(self) -> None:
        self.system_prompt = load_prompt("interviewer.md")

    def ask_question(self, state: SessionState, focus_for_next_question: str) -> str:
        question_style = "advanced" if state.difficulty == "hard" else "standard"
        last_turn = state.turns[-1] if state.turns else None
        last_answer = last_turn.answer if last_turn else ""
        evaluation_summary = ""
        if last_turn:
            evaluation = last_turn.evaluation
            evaluation_summary = (
                f"answer_type={evaluation.answer_type}; "
                f"relevance={evaluation.relevance}/5; depth={evaluation.depth}/5; "
                f"rationale={evaluation.rationale}"
            )
        user_prompt = json.dumps(
            {
                "session": state.summary(),
                "question_style": question_style,
                "last_answer": last_answer,
                "evaluation_summary": evaluation_summary,
                "focus_for_next_question": focus_for_next_question,
                "instruction": "Ask exactly one single-part interview question. Return only the question text.",
            },
            indent=2,
        )
        return self._single_question(call_llm(self.system_prompt, user_prompt, temperature=0.7))

    def _single_question(self, question: str) -> str:
        clean_question = " ".join(question.strip().strip('"').split())
        first_question_mark = clean_question.find("?")
        if first_question_mark == -1:
            return clean_question
        return clean_question[: first_question_mark + 1]
