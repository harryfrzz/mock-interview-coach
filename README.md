# AI Mock Interview Coach

A Python CLI mock interview coach that uses Gemini and a small multi-agent workflow to run a realistic 5-7 turn interview. The standout feature is job-description-aware interviewing: the app reads a Markdown JD file, extracts role requirements, and uses that context to personalize questions and feedback.

## What It Supports

- Optional job description parsing from a local Markdown filename.
- Optional resume/background parsing from a local Markdown filename.
- Dynamic interview questions generated from the JD, resume, target role, focus area, and previous answers.
- Adaptive difficulty.
- Recovery questions for vague, off-topic, partial, or unknown answers.
- Single-part interview questions only, to avoid overloaded multi-part prompts.
- Quick evaluation after each answer with answer type, relevance, and depth.
- Final structured Markdown feedback with strengths, gaps, readiness, and a practice plan.
- Automatic Markdown transcript export to `output/` after each completed interview.
- Rich-powered terminal UI.
- Gemini API integration through environment variables.

## Important JD Input Warning

Do not paste a long job description directly into the terminal prompt. Long pasted text can get cut off because of terminal buffer/input issues, and that can cause parsing errors or broken interview context.

Instead, save the JD in a Markdown file and pass only the filename when the program asks for it.

The JD & Resume Markdown file must be present in the same directory where you run `python main.py`.

Example:

```text
Job description filename (optional, press Enter to skip) (enter filename): sample_jd
```

You can also type:

```text
sample_jd.md
```

The included `sample_jd.md` is based on the original upGrad LinkedIn job post for the AI Engineer Intern role. You can edit `sample_jd.md` to use any other job description.

## Project Files

```text
main.py                  CLI entry point and interview loop
agents/                  Agent implementations
core/                    LLM wrapper, schemas, and session state
core/transcript.py       Markdown transcript exporter
prompts/                 System prompts for each agent
sample_jd.md             Example JD for upGrad AI Engineer Intern
sample_resume.md         Example candidate background
output/                  Generated interview transcripts and assessments
.env.example             Gemini configuration example
requirements.txt         Python dependencies
```

## Prompts Folder

The `prompts/` folder contains the behavior instructions for each agent:

- `prompts/jd_parser.md`: extracts possible roles, focus area, key skills, confidence, and summary from the job description.
- `prompts/interviewer.md`: generates one realistic, single-part interview question at a time.
- `prompts/evaluator.md`: scores the latest answer as strict JSON using relevance, depth, clarity, role alignment, and communication.
- `prompts/orchestrator.md`: decides the next action, difficulty, and interview flow based on session state.
- `prompts/coach.md`: creates final structured Markdown feedback after the interview.

## Architecture

```text
main.py
  -> ask for JD filename
  -> JDParserAgent parses the JD, if provided
  -> ask for role, focus area, and resume filename
  -> OrchestratorAgent decides next action and difficulty
  -> InterviewerAgent asks one question
  -> user answers in the terminal
  -> EvaluatorAgent scores the answer
  -> SessionState stores the turn and counters
  -> repeat for 5-7 turns
  -> CoachAgent generates final feedback
  -> core/transcript.py saves transcript and feedback to output/*.md
```

The app keeps all session state in memory through `core/session.py`. JSON-style outputs from the parser, evaluator, and orchestrator are validated with Pydantic schemas in `core/schemas.py`.

## Model

The app uses Gemini through the `google-generativeai` Python package.

Configuration is read from `.env`:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3-flash-preview
```

If `GEMINI_MODEL` is not set, `core/llm.py` falls back to `gemini-3-flash-preview`.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` and add your Gemini API key.

## How To Run

Start the program:

```bash
python main.py
```

Use the sample JD and resume by typing only the filenames:

```text
Job description filename (optional, press Enter to skip) (enter filename): sample_jd
Parsing job description...

Target role [AI Engineer Intern]:
Focus area (behavioral / technical / case / mixed) [technical]:
Resume/background filename (optional, press Enter to skip) (enter filename): sample_resume
Start interview? [y/n] (y): y
```

You can include `.md`, but it is not required:

```text
sample_jd
sample_jd.md
sample_resume
sample_resume.md
```

To skip the JD or resume, press Enter without typing anything.

## Customizing The JD And Resume

To practice for another role, edit:

- `sample_jd.md` for the job description.
- `sample_resume.md` for the candidate background.

Then run `python main.py` again and pass the same filenames when prompted.

## Output

At the end of each completed interview, the app saves a Markdown file in `output/`.

Example filename:

```text
output/20260430-153000-ai-engineer-intern.md
```

The exported file includes session details, JD summary, JD skills, every question and answer, turn-by-turn evaluation, and final feedback.

## Example Transcript 1: Using JD And Resume

```text
$ python main.py

Step 1: Job Description
Provide a .md JD filename, or press Enter to skip.

Job description filename (optional, press Enter to skip) (enter filename): sample_jd
Parsing job description...

Parsed Job Description
Detected role(s)  AI Engineer Intern
Focus area       technical
Key skills       Python, LLMs, RAG pipelines, AI agents, prompt engineering

Step 2: Interview Setup
Target role [AI Engineer Intern]:
Focus area (behavioral / technical / case / mixed) [technical]:
Resume/background filename (optional, press Enter to skip) (enter filename): sample_resume
Start interview? [y/n] (y): y

Question 1 of 6
Can you walk me through how you would design a small RAG-based learning assistant for course notes?

Your answer: I would chunk the notes, create embeddings, retrieve relevant chunks, and ask the LLM to answer only from that context.

Quick Evaluation
Type       partial
Relevance  4/5
Depth      3/5
```

## Example Transcript 2: Skipping The JD

```text
$ python main.py

Job description filename (optional, press Enter to skip) (enter filename):

Target role: Backend Engineer Intern
Focus area (behavioral / technical / case / mixed): technical
Resume/background filename (optional, press Enter to skip) (enter filename):
Start interview? [y/n] (y): y

Question 1 of 6
Tell me about a backend API you would design for a small product feature and what tradeoff you would consider first?

Your answer: I would start with REST endpoints, validate inputs, add database persistence, and keep the design simple until scale requires more complexity.
```

## Example Transcript 3: Weak Answer Recovery

```text
Question 2 of 6
How would you evaluate whether an LLM answer is grounded in the retrieved context?

Your answer: I am not sure.

Quick Evaluation
Type       unknown
Relevance  1/5
Depth      1/5

Question 3 of 6
Let's make that simpler: what is one sign that an LLM answer may not be supported by the provided context?

Your answer: If it mentions facts that were not present in the retrieved notes, that could be hallucination.
```

## Notes

- The interview length is controlled internally: minimum 5 turns, target 6 turns, maximum 7 turns.
- The app does not use a fixed question bank.
- The app does not use web search or a vector database.
- Completed sessions are saved as Markdown transcripts in `output/`.
