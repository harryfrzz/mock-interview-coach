# AI Mock Interview Coach

A Python CLI project that runs a realistic internally controlled 5-7 turn mock interview for a candidate preparing for a target role. It uses a multi-agent architecture to generate dynamic questions, evaluate answers, adapt difficulty, and produce structured coaching feedback.

## Features

- Multi-agent interview flow with four agents: Interviewer, Evaluator, Orchestrator, and Coach
- Dynamic question generation with no hardcoded question bank
- Internally controlled 5-7 turn interview sessions, with a default target of 6 turns
- Adaptive difficulty based on answer quality
- Detection of vague, off-topic, partial, strong, and "I don't know" answers
- Multi-dimensional scoring across relevance, depth, clarity, role alignment, and communication
- Structured final feedback in Markdown
- Simple Rich-powered CLI
- OpenAI and Gemini provider support
- Environment-based configuration via `.env`

## Architecture

```text
main.py
  -> OrchestratorAgent decides next action and difficulty
  -> InterviewerAgent generates one dynamic question
  -> Candidate answers in CLI
  -> EvaluatorAgent scores the answer as strict JSON
  -> SessionState updates counters and history
  -> CoachAgent generates final Markdown feedback
```

## Agent Roles

- Interviewer: asks exactly one realistic, adaptive interview question.
- Evaluator: returns strict JSON with answer type, scores, strengths, gaps, and a suggested probe.
- Orchestrator: decides next action, difficulty, focus area, and turn control.
- Coach: creates final structured feedback from the completed session.

## Orchestration

The orchestrator reviews session state before each question. It lowers difficulty or asks recovery follow-ups for weak, vague, unknown, partial, or off-topic answers. It increases difficulty after strong answers and can decide whether the next turn should be a follow-up, new question, simplified question, harder question, or final question. The CLI does not ask the user for the number of turns; `main.py` uses `TARGET_TURNS = 6` and enforces a hard maximum of 7 turns so the interview cannot continue endlessly.

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

- Target role
- Focus area
- Resume snippet, optional

If the resume snippet is empty, the session uses `No background provided.`

## Design Decisions

- Prompts are stored separately in `prompts/` to keep agent behavior easy to inspect and tune.
- Evaluator and orchestrator responses are validated with Pydantic for safer JSON handling.
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
