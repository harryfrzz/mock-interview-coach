from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from agents.coach import CoachAgent
from agents.evaluator import EvaluatorAgent
from agents.interviewer import InterviewerAgent
from agents.jd_parser import JDParserAgent
from agents.orchestrator import OrchestratorAgent
from core.schemas import FocusArea, JDParseResult
from core.session import SessionState


console = Console()

MIN_TURNS = 5
TARGET_TURNS = 6
MAX_TURNS = 7
FOCUS_AREAS = {"behavioral", "technical", "case", "mixed"}
FOCUS_AREA_PROMPT = "Focus area (behavioral / technical / case / mixed)"


def _safe_target_turns() -> int:
    return min(max(TARGET_TURNS, MIN_TURNS), MAX_TURNS)


def ask_required_text(label: str, default: str = "") -> str:
    while True:
        raw_value = Prompt.ask(label, default=default) if default else Prompt.ask(label)
        value = raw_value.strip()
        if value:
            return value
        console.print(f"[yellow]{label} cannot be empty. Please type a response.[/yellow]")


def ask_focus_area(default: str = "") -> FocusArea:
    fallback = default if default in FOCUS_AREAS else ""
    console.print(
        "[dim]Focus areas: behavioral = past experience/teamwork, "
        "technical = tools/coding/systems, case = business or product problem-solving, "
        "mixed = combination.[/dim]"
    )
    while True:
        raw_value = Prompt.ask(FOCUS_AREA_PROMPT, default=fallback) if fallback else Prompt.ask(FOCUS_AREA_PROMPT)
        value = raw_value.strip().lower()
        if value in FOCUS_AREAS:
            return value  # type: ignore[return-value]
        console.print("[yellow]Invalid focus area. Choose one of: behavioral, technical, case, mixed.[/yellow]")


def select_role(possible_roles: list[str]) -> str:
    if not possible_roles:
        return ""
    if len(possible_roles) == 1:
        return possible_roles[0]

    table = Table(title="Detected Role Options")
    table.add_column("#", justify="right")
    table.add_column("Role")
    for index, role in enumerate(possible_roles, start=1):
        table.add_row(str(index), role)
    console.print(table)

    while True:
        selection = Prompt.ask("Select a role number", default="1").strip()
        if selection.isdigit() and 1 <= int(selection) <= len(possible_roles):
            return possible_roles[int(selection) - 1]
        console.print("[yellow]Enter a valid role number from the list.[/yellow]")


def show_jd_parse_result(result: JDParseResult) -> None:
    roles = ", ".join(result.possible_roles) or "No confident role detected"
    skills = ", ".join(result.key_skills) or "No key skills detected"
    console.print(
        Panel(
            f"[bold]Detected role(s):[/bold] {roles}\n"
            f"[bold]Detected focus area:[/bold] {result.inferred_focus_area}\n"
            f"[bold]Detected key skills:[/bold] {skills}\n"
            f"[bold]Confidence:[/bold] {result.confidence}\n"
            f"[bold]JD summary:[/bold] {result.summary}",
            title="Parsed Job Description",
        )
    )


def collect_session_state() -> SessionState:
    jd_text = Prompt.ask("Paste job description (optional, press Enter to skip)").strip()
    jd_summary = ""
    jd_skills: list[str] = []
    default_role = ""
    default_focus = ""

    if jd_text:
        console.print("[dim]Parsing job description...[/dim]")
        jd_result = JDParserAgent().parse(jd_text)
        show_jd_parse_result(jd_result)
        default_role = select_role(jd_result.possible_roles)
        default_focus = jd_result.inferred_focus_area
        jd_summary = jd_result.summary
        jd_skills = jd_result.key_skills
    else:
        jd_text = "No job description provided."

    target_role = ask_required_text("Target role", default=default_role)
    focus_area = ask_focus_area(default_focus)
    resume_snippet = (
        Prompt.ask("Optional resume/background snippet (2-3 lines, press Enter to skip)").strip()
        or "No background provided."
    )
    return SessionState(
        target_role=target_role,
        focus_area=focus_area,
        resume_snippet=resume_snippet,
        jd_text=jd_text,
        jd_summary=jd_summary,
        jd_skills=jd_skills,
        total_turns=_safe_target_turns(),
    )


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

    console.print("\n[bold cyan]Final Feedback[/bold cyan]")
    console.print(Markdown(coach.generate_feedback(state)))


if __name__ == "__main__":
    try:
        run_interview()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interview stopped by user.[/yellow]")
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {exc}")
