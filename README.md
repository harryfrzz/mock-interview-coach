# AI Mock Interview Coach

A Python CLI project that runs a realistic internally controlled 5-7 turn mock interview for a candidate preparing for a target role. It uses a multi-agent architecture to generate dynamic questions, evaluate answers, adapt difficulty, and produce structured coaching feedback.

## Features

- Multi-agent interview flow with five agents: JD Parser, Interviewer, Evaluator, Orchestrator, and Coach
- Dynamic question generation with no hardcoded question bank
- Internally controlled 5-7 turn interview sessions, with a default target of 6 turns
- Adaptive difficulty based on answer quality
- Optional job description parsing with user confirmation and override
- Detection of vague, off-topic, partial, strong, and "I don't know" answers
- Multi-dimensional scoring across relevance, depth, clarity, role alignment, and communication
- Structured final feedback in Markdown
- Simple Rich-powered CLI
- OpenAI and Gemini provider support
- Environment-based configuration via `.env`

## Architecture

```text
main.py
  -> JDParserAgent optionally parses pasted job descriptions
  -> OrchestratorAgent decides next action and difficulty
  -> InterviewerAgent generates one dynamic question
  -> Candidate answers in CLI
  -> EvaluatorAgent scores the answer as strict JSON
  -> SessionState updates counters and history
  -> CoachAgent generates final Markdown feedback
```

## Agent Roles

- JD Parser: extracts likely roles, focus area, key skills, confidence, and summary from an optional job description.
- Interviewer: asks exactly one realistic, adaptive interview question.
- Evaluator: returns strict JSON with answer type, scores, strengths, gaps, and a suggested probe.
- Orchestrator: decides next action, difficulty, focus area, and turn control.
- Coach: creates final structured feedback from the completed session.

## Orchestration

The orchestrator reviews session state before each question. It lowers difficulty or asks recovery follow-ups for weak, vague, unknown, partial, or off-topic answers. It increases difficulty after strong answers and can decide whether the next turn should be a follow-up, new question, simplified question, harder question, or final question. The CLI does not ask the user for the number of turns; `main.py` uses `TARGET_TURNS = 6` and enforces a hard maximum of 7 turns so the interview cannot continue endlessly.

## Optional JD Parsing

The CLI starts by asking whether the user wants to paste a job description. If a JD is provided, the `JDParserAgent` extracts likely role titles, an inferred focus area, key skills, confidence, and a short summary.

The user stays in control:

- If one role is detected, it is shown as the default target role.
- If multiple roles are detected, the CLI shows numbered options and asks the user to select one.
- If no confident role is detected, the CLI asks for the target role manually.
- The user can accept inferred values by pressing Enter or type an override.
- Focus area is validated as one of `behavioral`, `technical`, `case`, or `mixed`.

JD context and candidate background are kept separate. The JD represents role and company requirements. The resume/background snippet represents the candidate. Extracted JD skills are internal context passed to the agents so questions and final coaching can be more relevant to the role.

This feature does not use web search, RAG, vector databases, or question banks. Those remain future scope.

## Setup

Create and activate a virtual environment if one does not exist:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

## Environment Variables

```text
OPENAI_API_KEY=
GEMINI_API_KEY=
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-1.5-flash
```

`LLM_PROVIDER` can be `openai` or `gemini`. OpenAI is the default.

## Run

```bash
python main.py
```

The CLI asks for:

- Job description, optional
- Target role
- Focus area
- Resume/background snippet, optional

If the resume snippet is empty, the session uses `No background provided.`

## Design Decisions

- Prompts are stored separately in `prompts/` to keep agent behavior easy to inspect and tune.
- Evaluator and orchestrator responses are validated with Pydantic for safer JSON handling.
- JD parsing uses strict JSON validation with a safe low-confidence fallback if parsing fails.
- Session state is centralized in `core/session.py` to make orchestration explicit.
- The implementation avoids question banks so questions are generated dynamically by the interviewer agent.
- The interview length is controlled internally. `TARGET_TURNS = 6` is the default, `MIN_TURNS = 5` allows early finish only after enough signal, and `MAX_TURNS = 7` prevents runaway loops.

## Tradeoffs

- The project depends on live LLM API calls, so tests and runs require valid credentials.
- Strict JSON parsing is robust to Markdown fences, but malformed model output can still fail fast.
- No persistence layer is included; sessions are in memory for simplicity.

## Limitations

- No automated transcript export yet.
- No local/offline model provider.
- No rubric customization from config files.
- No question bank, retrieval, or external knowledge lookup.

## Future Scope

- Add a curated question bank by role and difficulty.
- Add RAG over resume, job descriptions, and company-specific interview material.
- Add web search for current company and role context.
- Add transcript export to Markdown or JSON.
- Add automated tests with mocked LLM responses.

## Example Transcripts

See `examples/`:

- `strong_candidate.md`
- `weak_candidate.md`
- `edge_case.md`
- `jd_multiple_roles.md`
