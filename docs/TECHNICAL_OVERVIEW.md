# DevFlow: Technical overview

## The challenge

A code-generating assistant is not automatically a reliable engineering assistant. To diagnose an unfamiliar repository, it must inspect the codebase, form and test a hypothesis, make a bounded change, and explain the evidence for its conclusion. DevFlow explores how to make that sequence explicit and reusable.

## What the prototype implements

- A Python agent runtime with a Gemini model backend and an iterative tool-call/observation loop.
- Workspace-scoped tools for file listing, reading, searching and editing, plus restricted command execution.
- A skill catalog that discovers `SKILL.md` metadata before a full skill is loaded.
- Two reusable engineering workflows: `repo-understanding` and `debug-and-fix`.
- A diagnostic example containing an intentionally failing test and a percentage/decimal conversion bug.

## Architecture and design choices

```text
User task -> Gemini agent loop -> tool registry -> scoped workspace
                        |
                        +-> skill metadata -> load_skill -> task workflow
                        |
                        +-> tool result / error -> next reasoning step
```

The skill catalog avoids injecting every procedure into every conversation. An explicit workspace path constrains normal file operations, while separate skill-library paths allow reuse between repositories. Tool responses and exit codes are fed back to the agent rather than presented as a guarantee of success.

**Key trade-off:** allowlisted executables, timeouts and `shell=False` reduce avoidable risk but do **not** sandbox subprocesses. A process can still act with the user's OS permissions. This is an important boundary in the design.

## Walk-through: a concrete debugging flow

The included `examples/buggy-demo/` simulates an order calculation defect. A failing unit test supplies the observation; the agent inspects a few relevant modules, traces the percent-vs-fraction mismatch, modifies the relevant calculation and reruns the tests. The original project README provides the invocation and expected before/after output. See the example source and reset script if you want to reproduce it.

## Evidence and verification

- The automated test workflow has passed **21 unit tests** on GitHub (scope: tools, workspace boundaries, skills, runtime handling and related behavior).
- `evals/phase4-evaluation.md` describes a **small six-scenario, developer-run evaluation**, including five expected skill routings and one deliberately ambiguous case. These observations are not a statistical benchmark, and the live model run was not reproduced during this documentation pass.
- The deterministic demo documents the failing test and the subsequently passing tests; actual Gemini behavior may differ by model version and environment.

## Supported behaviors

Agent-loop design, development-tool interfaces, context/skill management, error handling, safety trade-offs, test-oriented workflow design and communicating uncertainty.

## Limits and further work

The runtime currently targets a single Gemini backend. Large-repository, multi-agent, adversarial, resource-budget and live-provider reliability studies have not been established. A full process/container sandbox, tighter write authorization and more systematic evaluation would be separate engineering work.

## Sources and maintenance

The implementation, tests and evaluation records are the sources for these design notes. Individual contributions should be confirmed through project records, not inferred from filenames.

**Primary sources:** [main README](../readme.md) · [agent runtime](../devflow/agent/runtime.py) · [tool execution](../devflow/tools/execution.py) · [evaluation](../evals/phase4-evaluation.md).


## Repository map

| Path | Purpose |
| --- | --- |
| `main.py`, `devflow/cli.py` | CLI entry points |
| `devflow/agent/runtime.py` | Iterative agent runtime and tool observations |
| `devflow/gemini.py` | Gemini model integration |
| `devflow/skills/` | Skill discovery and loading |
| `devflow/tools/` | Workspace file and process tools |
| `.github/skills/` | Reusable procedures |
| `examples/buggy-demo/` | Reproducible debugging example |
| `tests/` and `evals/` | Regression tests and evaluation records |

## Operation and maintenance

Install with `pip install -e .` in a compatible Python 3.14+ environment, then run `python -m unittest discover -s tests -v`. A live agent run also requires a configured Gemini API key. The [main README](../readme.md) has the CLI and configuration details.

The command allowlist and workspace checks do not sandbox an operating-system process. When updating the tool registry or skill loader, maintain the established failure-propagation and scope tests; a green unit test suite does not demonstrate safe arbitrary-code execution.
