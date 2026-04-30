from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from agents.coach import CoachAgent
from agents.evaluator import EvaluatorAgent
from agents.interviewer import InterviewerAgent
from agents.jd_parser import JDParserAgent
from agents.orchestrator import OrchestratorAgent
from core.schemas import FocusArea, JDParseResult
from core.session import SessionState
from core.transcript import export_transcript


console = Console()

MIN_TURNS = 5
TARGET_TURNS = 6
MAX_TURNS = 7
FOCUS_AREAS = {"behavioral", "technical", "case", "mixed"}
FOCUS_AREA_PROMPT = "Focus area (behavioral / technical / case / mixed)"


def _safe_target_turns() -> int:
    return min(max(TARGET_TURNS, MIN_TURNS), MAX_TURNS)


def show_welcome() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]AI Mock Interview Coach[/bold cyan]\n"
            "Adaptive 5-7 turn practice interview\n"
            "Optional JD parsing, role confirmation, and structured feedback",
            border_style="cyan",
        )
    )


def show_step(title: str, description: str = "") -> None:
    text = f"[bold]{title}[/bold]"
    if description:
        text += f"\n[dim]{description}[/dim]"
    console.print(Panel(text, border_style="blue"))


def ask_required_text(label: str, default: str = "") -> str:
    while True:
        raw_value = Prompt.ask(label, default=default) if default else Prompt.ask(label)
        value = raw_value.strip()
        if value:
            return value
        console.print(f"[yellow]{label} cannot be empty. Please type a response.[/yellow]")


def ask_markdown_file(label: str, placeholder: str = "enter filename") -> str:
    prompt_label = f"{label} [dim]({placeholder})[/dim]"
    while True:
        filename = Prompt.ask(prompt_label).strip()
        if not filename:
            return ""
        path = Path(filename)
        if path.name != filename:
            console.print("[yellow]Enter only a filename in this directory, not a full path.[/yellow]")
            continue
        if path.suffix and path.suffix.lower() != ".md":
            console.print("[yellow]Only Markdown files are supported. Enter a filename like sample_jd or sample_jd.md.[/yellow]")
            continue
        if not path.suffix:
            path = path.with_suffix(".md")
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            console.print(f"[yellow]Could not read Markdown file: {exc}[/yellow]")
            console.print("[yellow]Enter a valid filename like sample_jd or press Enter to skip.[/yellow]")


def ask_focus_area(default: str = "") -> FocusArea:
    fallback = default if default in FOCUS_AREAS else ""
    table = Table(title="Focus Area Options", show_header=True)
    table.add_column("Option", style="cyan")
    table.add_column("Use for")
    table.add_row("behavioral", "Past experience, teamwork, communication")
    table.add_row("technical", "Tools, coding, systems, SQL, APIs, ML")
    table.add_row("case", "Business or product problem-solving")
    table.add_row("mixed", "A combination of the above")
    console.print(table)
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

    table = Table(title="Detected Role Options", show_header=True)
    table.add_column("#", justify="right")
    table.add_column("Role")
    for index, role in enumerate(possible_roles, start=1):
        table.add_row(str(index), role)
    console.print(table)

    while True:
        selection = Prompt.ask("Select target role by number", default="1").strip()
        if selection.isdigit() and 1 <= int(selection) <= len(possible_roles):
            return possible_roles[int(selection) - 1]
        console.print("[yellow]Enter a valid role number from the list.[/yellow]")


def show_jd_parse_result(result: JDParseResult) -> None:
    roles = ", ".join(result.possible_roles) or "No confident role detected"
    skills = ", ".join(result.key_skills) or "No key skills detected"
    table = Table(title="Parsed Job Description", show_header=False)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value")
    table.add_row("Detected role(s)", roles)
    table.add_row("Focus area", result.inferred_focus_area)
    table.add_row("Key skills", skills)
    table.add_row("Confidence", result.confidence)
    table.add_row("Summary", result.summary)
    console.print(table)


def show_setup_summary(state: SessionState) -> bool:
    skills = ", ".join(state.jd_skills) if state.jd_skills else "None provided"
    resume_status = "Provided" if state.resume_snippet != "No background provided." else "Not provided"
    table = Table(title="Interview Setup Summary", show_header=False)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value")
    table.add_row("Target role", state.target_role)
    table.add_row("Focus area", state.focus_area)
    table.add_row("JD skills", skills)
    table.add_row("Resume/background", resume_status)
    table.add_row("Target turns", str(state.total_turns))
    console.print(table)
    return Confirm.ask("Start interview?", default=True)


def show_quick_evaluation(answer_type: str, relevance: int, depth: int) -> None:
    table = Table(title="Quick Evaluation", show_header=False)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Result")
    table.add_row("Type", answer_type)
    table.add_row("Relevance", f"{relevance}/5")
    table.add_row("Depth", f"{depth}/5")
    console.print(table)


def collect_session_state() -> SessionState:
    show_step("Step 1: Job Description", "Provide a .md JD filename, or press Enter to skip.")
    jd_text = ask_markdown_file("Job description filename (optional, press Enter to skip)")
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

    show_step("Step 2: Interview Setup", "Confirm the role, choose focus area, and add an optional resume .md file.")
    target_role = ask_required_text("Target role", default=default_role)
    focus_area = ask_focus_area(default_focus)
    resume_snippet = ask_markdown_file("Resume/background filename (optional, press Enter to skip)") or "No background provided."
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
    show_welcome()
    state = collect_session_state()
    if not show_setup_summary(state):
        console.print("[yellow]Interview setup cancelled.[/yellow]")
        return

    interviewer = InterviewerAgent()
    evaluator = EvaluatorAgent()
    orchestrator = OrchestratorAgent()
    coach = CoachAgent()

    show_step("Step 3: Mock Interview", "Tip: answer with context, action, result, and tradeoffs when possible.")

    while len(state.turns) < MAX_TURNS:
        decision = orchestrator.decide(state)
        if decision.should_finish and len(state.turns) >= MIN_TURNS:
            break

        state.difficulty = decision.difficulty
        question = interviewer.ask_question(state, decision.focus_for_next_question)
        console.print(
            Panel(
                question,
                title=f"Question {len(state.turns) + 1} of {state.total_turns}",
                border_style="magenta",
            )
        )
        answer = ask_required_text("Your answer")

        evaluation = evaluator.evaluate(state, question, answer)
        state.add_turn(question, answer, evaluation)
        show_quick_evaluation(evaluation.answer_type, evaluation.relevance, evaluation.depth)

    show_step("Step 4: Final Feedback")
    final_feedback = coach.generate_feedback(state)
    console.print(Markdown(final_feedback))
    transcript_path = export_transcript(state, final_feedback)
    console.print(f"\n[green]Transcript saved to:[/green] {transcript_path}")
    console.print(
        Panel.fit(
            "[bold green]Interview complete[/bold green]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    try:
        run_interview()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interview stopped by user.[/yellow]")
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {exc}")
