from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from agents.coach import CoachAgent
from agents.evaluator import EvaluatorAgent
from agents.interviewer import InterviewerAgent
from agents.orchestrator import OrchestratorAgent
from core.session import SessionState
from core.transcript import export_transcript


console = Console()

MIN_TURNS = 5
TARGET_TURNS = 6
MAX_TURNS = 7


def _safe_target_turns() -> int:
    return min(max(TARGET_TURNS, MIN_TURNS), MAX_TURNS)


def ask_required_text(label: str) -> str:
    while True:
        value = Prompt.ask(label).strip()
        if value:
            return value
        console.print("[yellow]Please enter a response before continuing.[/yellow]")


def collect_session_state() -> SessionState:
    role = ask_required_text("Target role")
    focus_area = ask_required_text("Focus area")
    resume = Prompt.ask("Resume snippet (optional)").strip() or "No background provided."
    return SessionState(role=role, focus_area=focus_area, resume=resume, total_turns=_safe_target_turns())


def run_interview() -> None:
    console.print(Panel.fit("AI Mock Interview Coach", style="bold cyan"))
    state = collect_session_state()

    interviewer = InterviewerAgent()
    evaluator = EvaluatorAgent()
    orchestrator = OrchestratorAgent()
    coach = CoachAgent()

    while len(state.turns) < MAX_TURNS:
        decision = orchestrator.decide(state)
        if decision.should_finish and len(state.turns) >= MIN_TURNS:
            break

        state.difficulty = decision.difficulty
        question = interviewer.ask_question(state, decision.focus_for_next_question)
        console.print(Panel(question, title=f"Question {len(state.turns) + 1} | {state.difficulty}"))
        answer = ask_required_text("Your answer")

        evaluation = evaluator.evaluate(state, question, answer)
        state.add_turn(question, answer, evaluation)
        console.print(
            f"[dim]Evaluation: {evaluation.answer_type}, "
            f"relevance {evaluation.relevance}/5, depth {evaluation.depth}/5[/dim]"
        )

    final_feedback = coach.generate_feedback(state)
    console.print("\n[bold cyan]Final Feedback[/bold cyan]")
    console.print(Markdown(final_feedback))
    transcript_path = export_transcript(state, final_feedback)
    console.print(f"\n[green]Transcript saved to:[/green] {transcript_path}")


if __name__ == "__main__":
    try:
        run_interview()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interview stopped by user.[/yellow]")
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {exc}")
