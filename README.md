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

## Example Interview Transcripts

These short examples show the types of sessions the app can handle. Actual questions and feedback may vary because the interviewer, evaluator, orchestrator, and coach are LLM-driven.

## Example Transcript 1: Strong Candidate

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

Your answer: I would first define the target use case, such as answering questions from course notes. Then I would chunk the notes by section, generate embeddings, store them in a vector index, retrieve the top relevant chunks for each query, and pass only those chunks to the LLM. I would also tell the model to say when the answer is not present in the context, and I would evaluate outputs using a small test set for relevance, factual grounding, and completeness.

Quick Evaluation
Type       strong
Relevance  5/5
Depth      5/5

Question 2 of 6
How would you reduce hallucinations in that learning assistant?

Your answer: I would use retrieval-grounded prompts, ask the model to cite the specific context it used, reject answers when retrieval confidence is low, and maintain an evaluation set with unsupported-answer examples. I would also inspect failures by separating retrieval errors from generation errors.

Quick Evaluation
Type       strong
Relevance  5/5
Depth      4/5
```

## Example Transcript 2: Weak Candidate Recovery

```text
$ python main.py

Job description filename (optional, press Enter to skip) (enter filename): sample_jd
Parsing job description...

Target role [AI Engineer Intern]:
Focus area (behavioral / technical / case / mixed) [technical]:
Resume/background filename (optional, press Enter to skip) (enter filename): sample_resume
Start interview? [y/n] (y): y

Question 1 of 6
Can you explain how you would evaluate whether an LLM answer is grounded in the retrieved context?

Your answer: I am not sure.

Quick Evaluation
Type       unknown
Relevance  1/5
Depth      1/5

Question 2 of 6
Let's make that simpler: what is one sign that an LLM answer may not be supported by the provided context?

Your answer: If it gives facts that were not in the course notes, that might be hallucination.

Quick Evaluation
Type       partial
Relevance  4/5
Depth      2/5
```

## Example Transcript 3: Tricky Edge Case

```text
$ python main.py

Job description filename (optional, press Enter to skip) (enter filename): sample_jd
Parsing job description...

Target role [AI Engineer Intern]:
Focus area (behavioral / technical / case / mixed) [technical]:
Resume/background filename (optional, press Enter to skip) (enter filename): sample_resume
Start interview? [y/n] (y): y

Question 1 of 6
How would you decide whether a poor answer from a learning assistant is caused by retrieval quality or prompt design?

Your answer: I would improve the prompt and increase the number of retrieved chunks.

Quick Evaluation
Type       partial
Relevance  3/5
Depth      2/5

Question 2 of 6
That's a useful start. What single test would you run first to determine whether the retrieved context contains the correct answer?

Your answer: I would manually inspect the top retrieved chunks for a few failed questions and check whether the correct answer is present before changing the generation prompt.

Quick Evaluation
Type       strong
Relevance  5/5
Depth      4/5
```

## Notes

- The interview length is controlled internally: minimum 5 turns, target 6 turns, maximum 7 turns.
- The app does not use a fixed question bank.
- The app does not use web search or a vector database.
- Completed sessions are saved as Markdown transcripts in `output/`.
