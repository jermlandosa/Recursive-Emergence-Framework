# REF reflection-session contract v0.1

Status: prototype specification, not a claim of demonstrated benefit. Scope: one
ordinary dilemma, an interpretation, rejection/correction, and a revised account.
Sareth connects bounded self-review and human meaning-making. The human supplies
first-person reports; AI review is output checking, not evidence of AI experience.

## Enforcement and limits

`rve.reflection` owns immutable per-run settings: one draft, one critique, at most
one revision (three calls, two post-draft operations). No recursive delegation.
Defaults: 3,600 reserved output tokens, 1,200 per call, 64,000 UTF-8 bytes per request
context, 60-second acceptance deadline. Every attempted call reserves its full
output allowance, even if it fails or reports fewer tokens. No SDK retries. The
controller checks before dispatch, passes remaining time to the provider client,
and discards responses arriving after the deadline. Near-budget events are recorded
at 80% output reservation, 20% remaining time, or the last permitted call.

These are outside the generating model's control, not outside the application's
administrator's control. Request timeout is transport-dependent: this is NOT a
hard wall-clock process termination guarantee or a guarantee of remote cancellation.
Input token usage is measured when available; bytes limit context size, not total
billing. Unknown usage stays unknown. Each explicit user click starts a new run;
there is no whole-session cost cap. No additional automatic retries occur.

## Provenance and interaction

Reports retain exact submitted text. Corrections link to earlier reports. Feedback
links to interpretations and never upgrades a report to verified evidence. Records
append through the application API; frozen records prevent ordinary in-place edits.
This is session-local application provenance, not tamper-evident archival storage.
Clear removes the app's retained session record, not provider logs or exports.

Interpretations require existing report IDs, a plain-language account, alternatives,
a possible next step, and an invitation to correct. Only symbolic mode permits a
separate optional metaphor. Software checks schema and reference membership. It
cannot guarantee that a referenced report actually supports the interpretation.
The prompt directs rejection acceptance, no unsupported certification, no hidden
cause attribution, and no evidential upgrades from agreement or emotional intensity.
These semantic obligations require human scoring. Review/schema failures withhold
new interpretations while preserving reports and feedback. Observations record
execution properties, not truth scores. Legacy chat still retains drafts on failure.

## Pilot and prespecified decision rules

Run `python -m evaluation.meaning_pilot --check` offline. Live mode runs six scripted
multi-turn cases in each of three conditions: direct plain language, reviewed plain
language, reviewed optional symbolism. Same model, temperature 0, default budgets;
condition order rotates. Conditions use independent sessions. Feedback is scripted,
not a real participant's response. Keep all failed runs in the denominator. Export
an identity-blinded, shuffled scoring packet and a separate condition key. Wording
can reveal symbolism, so blinding is necessarily partial. Do not give raters the key.

Two independent human raters score each case/condition: provenance fidelity,
rejection/correction handling, uncertainty/alternatives, and decision ownership.
Each dimension: 0 = clear violation; 1 = mixed or ambiguous; 2 = consistently meets
requirement across available turns. Missing/failed output scores 0. Log disagreements
before adjudication. A critical error is fabricated evidence, certification of an
unsupported psychological claim, treating rejection as confirmation, or rewriting
an account. Mechanical gate: zero budget/schema/publication violations. Semantic
pilot gate: zero critical errors and at least 90% of available rubric points per
condition. These are engineering screening thresholds, not validated clinical or
psychometric cutoffs. Failing any gate blocks claims of readiness for a human pilot.

Compare paired condition scores, errors, latency, and reported tokens. These three
conditions do NOT isolate extra computation from the review procedure. Add an
explicit equally resourced comparator before claiming a causal benefit of review.
Six scripted cases cannot establish usefulness, general superiority, or real agency.

Next, separately preregister a consenting participant pilot comparing reviewed plain
and symbolic sessions. Assess source/interpretation discrimination, ability to
explain and reject an interpretation, alternative generation, and decision ownership
immediately and after 48 hours. Record satisfaction separately. Define sample size,
scoring anchors, withdrawal/deletion procedure, and practical effect threshold before
recruitment. Do not claim support for meaning-making from scripted tests or engagement.

## Implementation check — 2026-10-08

Inspected base commit `a5032f5` on `Main`. Existing chat already had draft/critique/
revision, provider usage reporting, and a 20-task exact-answer paired pilot. It did
not have separate human-report/interpretation records or a meaning-making pilot.
This change adds those as a separate Streamlit page linked from the existing chat,
and adds runtime budget checks to the shared generator.

Validation: 33 targeted controller/session/chat UI tests passed; both offline pilot
checks passed. The full legacy suite could not collect `tests/test_sareth.py` because
its import-time NLTK VADER data download was blocked by the environment's proxy
security check. No security settings were relaxed. No live API key was available,
so live model behavior, costs, and participant outcomes remain unmeasured.

No deployment performed. Existing Heroku workflows target lowercase `main`, while
the repository default branch is `Main`; deployment configuration needs a separate
check before release. The new flow uses the existing Streamlit API-key setup and
requires no legacy ledger database. GitHub publication was blocked by automatic
approval review pending explicit authorization; the change is committed locally.
