---
name: debug-and-fix
description: Systematically diagnose, repair, and verify software defects using reproducible failures, stack traces, tests, logs, and focused source inspection. Use when an application, command, test, build, or runtime behavior is failing or incorrect and the user wants the root cause identified, fixed, and verified.
---

# Debug and Fix

Diagnose from evidence, make the smallest justified repair, and verify the outcome.

## Establish the failure contract

- Determine the expected behavior, observed behavior, triggering inputs, and relevant environment from the request and repository.
- Inspect the documented run or test commands before guessing how to execute the project.
- Identify what would constitute a successful fix before editing.

## Reproduce and collect evidence

1. Reproduce the failure when execution is reasonably possible and safe.
2. Record the exact command, inputs, exit status, stdout, stderr, failing tests, stack trace, or logs.
3. If reproduction is blocked, explain why and continue only with evidence available from the repository and user.
4. Inspect the failing path and the smallest surrounding context needed to understand it.

## Diagnose the root cause

- Follow the stack trace or failing assertion to relevant code, then search callers, definitions, configuration, and related tests.
- Separate the visible symptom from the earliest incorrect assumption, state transition, input handling, or dependency behavior that causes it.
- Form a concrete hypothesis and test it against the collected evidence.
- Consider multiple hypotheses only when the evidence does not distinguish them; investigate the cheapest discriminating check first.
- Do not edit code merely because it appears suspicious.

## Apply a focused repair

- Change only what is necessary to address the supported root cause.
- Preserve public behavior and unrelated code paths unless the requested correction requires otherwise.
- Avoid cleanup, dependency changes, formatting churn, and unrelated refactoring.
- Update or add a focused test when it is the practical way to capture the defect and prevent regression.

## Verify and iterate

1. Rerun the original reproduction command or failing test after the change.
2. Run the narrowest relevant regression checks, then broader tests when risk and available time justify them.
3. Evaluate exit status and output; do not treat command execution alone as success.
4. If verification fails, use the new evidence to continue investigating. Do not stack speculative fixes.
5. If full verification is unavailable, state exactly what was and was not verified.

Never report success solely because code was changed or because the proposed fix looks correct.

## Report the outcome

Clearly state:

- the root cause and supporting evidence
- the focused changes made
- the verification commands or checks performed and their actual results
- any remaining failures, limitations, or uncertainty
