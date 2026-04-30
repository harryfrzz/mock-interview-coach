from datetime import datetime
from pathlib import Path
import re

from core.session import SessionState


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "interview"


def export_transcript(state: SessionState, final_feedback: str) -> Path:
    """Write the completed interview transcript and feedback to output/*.md."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = OUTPUT_DIR / f"{timestamp}-{_slugify(state.role)}.md"

    lines = [
        "# AI Mock Interview Coach Transcript",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Session Details",
        "",
        f"- Target role: {state.role}",
        f"- Focus area: {state.focus_area}",
        f"- Resume snippet: {state.resume}",
        f"- Completed turns: {len(state.turns)}",
        f"- Final difficulty: {state.difficulty}",
        "",
        "## Counters",
        "",
        f"- Strong answers: {state.strong_count}",
        f"- Weak answers: {state.weak_count}",
        f"- Vague answers: {state.vague_count}",
        f"- Unknown answers: {state.unknown_count}",
        "",
        "## Interview Transcript",
        "",
    ]

    for turn in state.turns:
        evaluation = turn.evaluation
        lines.extend(
            [
                f"### Turn {turn.number} | {turn.difficulty}",
                "",
                f"**Question:** {turn.question}",
                "",
                f"**Answer:** {turn.answer}",
                "",
                "**Evaluation:**",
                "",
                f"- Answer type: {evaluation.answer_type}",
                f"- Relevance: {evaluation.relevance}/5",
                f"- Depth: {evaluation.depth}/5",
                f"- Clarity: {evaluation.clarity}/5",
                f"- Role alignment: {evaluation.role_alignment}/5",
                f"- Communication: {evaluation.communication}/5",
                f"- Strengths: {', '.join(evaluation.strengths) or 'None'}",
                f"- Gaps: {', '.join(evaluation.gaps) or 'None'}",
                f"- Suggested probe: {evaluation.suggested_probe or 'None'}",
                f"- Rationale: {evaluation.rationale}",
                "",
            ]
        )

    lines.extend(["## Final Feedback", "", final_feedback.strip(), ""])
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path
