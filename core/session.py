from dataclasses import dataclass, field

from core.schemas import Difficulty, InterviewTurn, TurnEvaluation


@dataclass
class SessionState:
    role: str
    focus_area: str
    resume: str
    total_turns: int = 6
    difficulty: Difficulty = "medium"
    turns: list[InterviewTurn] = field(default_factory=list)
    weak_count: int = 0
    vague_count: int = 0
    unknown_count: int = 0
    strong_count: int = 0

    def add_turn(self, question: str, answer: str, evaluation: TurnEvaluation) -> None:
        self.turns.append(
            InterviewTurn(
                number=len(self.turns) + 1,
                question=question,
                answer=answer,
                difficulty=self.difficulty,
                evaluation=evaluation,
            )
        )
        if evaluation.answer_type == "strong":
            self.strong_count += 1
        elif evaluation.answer_type == "vague":
            self.vague_count += 1
            self.weak_count += 1
        elif evaluation.answer_type == "unknown":
            self.unknown_count += 1
            self.weak_count += 1
        elif evaluation.answer_type in {"partial", "off_topic"}:
            self.weak_count += 1

    def summary(self) -> dict[str, object]:
        return {
            "role": self.role,
            "focus_area": self.focus_area,
            "resume": self.resume,
            "total_turns": self.total_turns,
            "current_turn": len(self.turns),
            "difficulty": self.difficulty,
            "counters": {
                "weak": self.weak_count,
                "vague": self.vague_count,
                "unknown": self.unknown_count,
                "strong": self.strong_count,
            },
            "turns": [turn.model_dump() for turn in self.turns],
        }
