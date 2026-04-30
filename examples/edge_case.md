# Edge Case Transcript

Target role: Machine Learning Intern
Focus area: model evaluation
Resume snippet: Completed a class project using scikit-learn for classification.
Interview length: Controlled internally by the app, completed in 6 turns.

## Turn 1
Interviewer: How would you evaluate a classification model for an imbalanced dataset?

Candidate: I don't know.

Evaluator: unknown; direct admission with no attempt.

## Turn 2
Interviewer: No problem. At a basic level, what could go wrong if you only use accuracy on imbalanced data?

Candidate: It can be bad because numbers are weird sometimes.

Evaluator: vague; loosely related but lacks concrete explanation.

## Turn 3
Interviewer: Imagine 95% of examples are negative. Why might a model with 95% accuracy still be weak?

Candidate: My favorite programming language is Python, and I like pandas a lot.

Evaluator: off_topic; does not answer the question.

## Turn 4
Interviewer: Let's redirect. If a model predicts every example as negative in that dataset, what does it miss?

Candidate: It misses the positive cases, so recall for the positive class would be poor.

Evaluator: partial; correct recovery but brief.

## Turn 5
Interviewer: Which metrics would you report alongside accuracy?

Candidate: Precision, recall, F1, and maybe a confusion matrix. I would look at the positive class because that is the rare class.

Evaluator: strong; relevant and specific.

## Turn 6
Interviewer: How would you explain the tradeoff between precision and recall to a non-technical stakeholder?

Candidate: Precision is about how many flagged cases are actually right, while recall is about how many real cases we catch. If missing positives is costly, I would favor recall, but if false alarms are costly, I would favor precision.

Evaluator: strong; clear and stakeholder-friendly.
