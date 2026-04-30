# Strong Candidate Transcript

Target role: Backend Engineering Intern
Focus area: API design and reliability
Resume snippet: Built a Flask task tracker with PostgreSQL and Redis caching.
Interview length: Controlled internally by the app, completed in 6 turns.

## Turn 1
Interviewer: Tell me about an API you built and how you decided on its endpoints and data model.

Candidate: In my Flask task tracker, I designed endpoints around resources: projects, tasks, and comments. I used `GET /projects/{id}/tasks` for listing tasks and `PATCH /tasks/{id}` for partial updates. I separated task status from priority so filtering stayed simple. I chose PostgreSQL because the data was relational and I needed constraints for ownership.

Evaluator: strong; high relevance, good depth, clear role alignment.

## Turn 2
Interviewer: How would you handle an endpoint that becomes slow under load?

Candidate: I would first measure where time is spent with logs, metrics, and database query analysis. If the bottleneck is repeated reads, I would add Redis caching with a clear invalidation strategy. If it is a query issue, I would review indexes and pagination. I would also set timeouts and return useful errors rather than letting requests hang.

Evaluator: strong; specific and practical.

## Turn 3
Interviewer: Suppose your cache returns stale task data after updates. How would you fix it?

Candidate: I would invalidate or update the relevant cache key in the same code path as the database write. For high-risk cases, I would use a short TTL as a backup. I would also add tests around update flows and metrics for cache hit rate and stale reads.

Evaluator: strong; discusses correctness and observability.

## Turn 4
Interviewer: How do you design API errors for client developers?

Candidate: I use consistent status codes and response bodies with a machine-readable code, human-readable message, and optional field-level details. For example, validation errors should be 400 with field names, while unauthorized requests should be 401. I avoid leaking internals in 500 errors.

Evaluator: strong; concise and structured.

## Turn 5
Interviewer: What tradeoffs would you consider before adding background jobs?

Candidate: Background jobs help move slow work out of request paths, but they add operational complexity. I would use them for email, report generation, or expensive retries. I would consider idempotency, retries, dead-letter handling, and how the user sees job status.

Evaluator: strong; strong tradeoff awareness.

## Turn 6
Interviewer: How would you prove your API is reliable enough for users?

Candidate: I would define SLOs for latency and error rate, add structured logs and metrics, test common failure cases, and monitor database performance. For an intern project, I would start with unit and integration tests plus basic dashboards, then improve based on observed failures.

Evaluator: strong; realistic for internship level.
