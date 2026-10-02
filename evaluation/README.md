# REF reflection pilot

The current Streamlit chat uses `rve.reflection.generate_response`. Review mode
makes a draft, requests a structured critique, and revises only when the critique
identifies a concrete problem. It uses the same model for all phases and stops
at three calls. Baseline mode uses the same drafting call alone. This is bounded
self-review, not an independent fact checker. No external retrieval or persistent
cross-session memory is introduced by this change.

The UI defaults to review mode. Disable **Review before answering** for ordinary
chat. Review notes, attempted calls, elapsed time, and reported token usage are
available under response details. Review failures retain the original draft and
are visibly flagged. Initial generation failures do not commit a conversation turn.

## Run the pilot

Install the repository dependencies and configure `OPENAI_API_KEY` in the local
environment. The hosted app can instead use Streamlit Secrets. The evaluation
CLI uses an environment variable and runs outside Streamlit.

```bash
python -m evaluation.ref_pilot --check
python -m evaluation.ref_pilot --model gpt-4o-mini --output ref-pilot-results.json
```

The live run contains 20 task pairs. Each arm uses a separate fresh conversation,
the same model, temperature 0, and the same token limit. Order alternates across
tasks. Answer keys are used only by the local scorer, never sent to the model.
Results are checkpointed after each pair. The JSON contains both drafts, final
answers, review issues, status, usage, paired wins and regressions.

These tasks are a small, fixed synthetic diagnostic set, not a held-out benchmark
or proof of general improvement. Exact-answer scoring also tests output-format
compliance. Missing-information cases measure unsupported assertions narrowly;
other claims and real conversational helpfulness require human review. Token
counts are provider-reported; dollar prices are deliberately not assumed. A
failed call can make usage incomplete. Reflection failures are retained in the
comparison as degraded results; initial-generation failures have no correctness
score and are excluded from paired summaries.

## What has been validated

Offline tests cover call bounds, model-setting consistency, structured critique
validation, clean-review retention, revision failure, provider failure, incomplete
usage, and the 20 scoring contracts. Live model quality and cost need an API run.

Older `test_tools.py`, `recursor.py`, and glyph detectors are retained as legacy
experiments; they do not supply the new response review. Symbolic annotations in
the chat are explicitly labelled as keyword annotations, not truth scores.
