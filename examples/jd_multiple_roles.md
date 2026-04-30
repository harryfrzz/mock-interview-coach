# JD Parsing With Multiple Roles Example

Note: This is an illustrative sample transcript. Because questions are generated dynamically by the LLM, exact question wording may differ between runs.

## Startup

Paste job description (optional, press Enter to skip):

```text
We are hiring interns for our analytics team. Candidates may support Product Analyst or Data Analyst projects. Responsibilities include writing SQL queries, building dashboards, analyzing product funnels, communicating findings to stakeholders, and helping define business metrics. Python experience is a plus.
```

## Parsed Job Description

Detected role(s): Product Analyst Intern, Data Analyst Intern

Detected focus area: technical

Detected key skills: SQL, dashboards, product funnels, business metrics, stakeholder communication, Python

Confidence: high

JD summary: Internship role focused on analytics, SQL, dashboards, product funnel analysis, and business metric reporting.

## Role Selection

Detected Role Options:

| # | Role |
|---|---|
| 1 | Product Analyst Intern |
| 2 | Data Analyst Intern |

Select a role number [1]: 2

Target role [Data Analyst Intern]:

Focus area [technical]:

Optional resume/background snippet (2-3 lines, press Enter to skip): Built a small SQL dashboard for a class project.

## Interview Behavior

Question 1 | medium:

How would you use SQL to investigate a drop in a product funnel metric, and what checks would you run before sharing the result with stakeholders?

Candidate answer: I would compare conversion rates between steps, segment by date and user type, check for missing data, and validate the query counts against raw event totals.

Evaluation: strong; relevant to the selected Data Analyst Intern role and grounded in JD skills.

Question 2 | hard:

Suppose your dashboard shows a sudden improvement in conversion rate after a product release. How would you determine whether the improvement is real or caused by tracking changes?

Candidate answer: I would check event definitions, compare pre/post instrumentation, look for missing events, and validate against another source if available.

Evaluation: strong; role-specific follow-up based on dashboarding and product metrics.
