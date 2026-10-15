# DevFlow

> **At a glance:** A Python/Gemini engineering-agent prototype that inspects repositories, uses structured development tools, loads task-specific skills, and verifies focused changes. **Evidence:** a repeatable failing-test demo, 21 passing offline unit tests, and an existing small exploratory evaluation. **Scope:** engineering prototype; command restrictions are not an OS sandbox.

**Explore:** [Architecture](#architecture) · [Debugging demo](#end-to-end-debugging-demo) · [Evaluation](#evaluation) · [Detailed case study](docs/CASE_STUDY.md)


**A standalone agentic AI engineering assistant with portable Agent Skills for repository understanding and verified debugging.**

DevFlow uses an iterative LLM tool-calling loop to inspect software repositories, search and read code, execute development commands, make focused changes, and verify its work inside an explicitly scoped workspace.

Instead of placing every workflow into one large system prompt, DevFlow supports reusable `SKILL.md` capabilities that are discovered by metadata and loaded only when relevant.

---

## Why DevFlow?

Developers repeatedly spend time on tasks such as:

- returning to an unfamiliar or forgotten repository
- locating important entry points and execution flow
- diagnosing failing tests and runtime errors
- changing only the code responsible for a defect
- verifying that a proposed fix actually works

DevFlow explores how an engineering agent can handle these workflows through a combination of:

- an iterative agent loop
- structured developer tools
- workspace-scoped execution
- reusable Agent Skills
- progressive context loading
- verification-oriented behavior

The goal is not just to generate code, but to **inspect, act, observe, and verify**.

---

## Key Features

- **Standalone agent runtime** using Gemini as the current model backend
- **Iterative tool calling** with observations returned to the model after each action
- **Workspace isolation** for file and command operations
- **Portable Agent Skills** stored as `.github/skills/<skill-name>/SKILL.md`
- **Progressive skill loading** so only skill metadata is present initially
- **Repository understanding workflow** for unfamiliar codebases
- **Debug-and-fix workflow** that emphasizes reproduction, evidence, minimal repair, and verification
- **Developer tools** for listing, reading, searching, writing, and executing within a workspace
- **Normalized tool results** for successes, failures, output, and exit codes
- **Bounded command execution** with timeouts, `shell=False`, restricted executables, and read-only Git operations
- **Automated tests and end-to-end evaluation**

---

## Architecture

```text
                           User
                            |
                            v
                     DevFlow Agent
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          Gemini Session          Skill Catalog
                 |                 metadata only
                 |                     |
                 |              load_skill(name)
                 |                     |
                 +----------+----------+
                            |
                            v
                      Agent Runtime
                            |
                            v
                      Tool Registry
                            |
        +-------------------+-------------------+
        |          |          |         |       |
        v          v          v         v       v
   list_files  read_file  search_files  write  run_command
        |          |          |         |       |
        +-------------------+-------------------+
                            |
                            v
                    Scoped Workspace
```

The model decides the next action, DevFlow executes the requested tool, returns the observation, and continues until the task is complete or the iteration limit is reached.

---

## Agent Skills

DevFlow currently includes two production skills.

### `repo-understanding`

Used when a developer needs a grounded mental model of a repository.

The workflow guides the agent to:

1. inspect the top-level structure
2. identify manifests, configuration, languages, and frameworks
3. locate likely entry points
4. inspect only relevant modules
5. trace imports, references, and execution or data flow
6. distinguish repository evidence from inference
7. summarize architecture and useful continuation points

This skill remains read-only unless modification is explicitly requested.

### `debug-and-fix`

Used for crashes, runtime exceptions, failing tests, regressions, and incorrect behavior.

The workflow guides the agent to:

1. understand expected and observed behavior
2. reproduce the failure when possible
3. collect stack traces, test failures, logs, and source evidence
4. identify the root cause instead of patching symptoms
5. make the smallest reasonable repair
6. rerun appropriate verification
7. continue investigating if verification fails
8. report success only after successful verification

---

## Progressive Skill Loading

DevFlow does not inject every skill body into every request.

```text
.github/skills/*/SKILL.md
          |
          v
   discover metadata
   name + description
          |
          v
    agent context
          |
          v
 model selects skill
          |
          v
  load_skill(name)
          |
          v
 full SKILL.md loaded
          |
          v
 agent follows workflow
```

The skill library is separate from the target workspace:

- `--workspace` selects the repository DevFlow may inspect, modify, and execute in
- `--skills-dir` selects the read-only Agent Skills library

This allows the same DevFlow skill library to be used while working on different repositories.

---

## Developer Tools

| Tool | Purpose |
|---|---|
| `list_files` | Inspect workspace structure |
| `read_file` | Read UTF-8 source and configuration files |
| `search_files` | Search repository content |
| `write_file` | Make focused file modifications |
| `run_command` | Execute allowlisted development commands |
| `load_skill` | Progressively load a selected Agent Skill |

Tool handlers return normalized results containing success state, output, error details, and exit codes where applicable.

---

## End-to-End Debugging Demo

The repository includes a reproducible multi-file Python demo with an intentional failing test.

Example:

```powershell
python .\main.py --workspace .\examples\buggy-demo --skills-dir .\.github\skills --verbose "The tests in this project are failing. Diagnose the root cause from evidence, make the smallest reasonable repair, and verify the fix."
```

Observed agent flow:

```text
load_skill("debug-and-fix")
        |
        v
run failing tests
        |
        v
observe AssertionError
        |
        v
inspect config.py
inspect pricing.py
inspect order_service.py
        |
        v
identify percentage / decimal unit mismatch
        |
        v
modify order_service.py only
        |
        v
rerun tests
        |
        v
2 tests passed
```

The defect was a unit mismatch:

```python
# Before
return apply_tax(subtotal, DEFAULT_TAX_PERCENT)

# Verified repair
return apply_tax(subtotal, DEFAULT_TAX_PERCENT / 100)
```

Before the repair:

```text
Ran 2 tests
FAILED (failures=1)
AssertionError: 525.0 != 30.0
```

After the repair:

```text
Ran 2 tests
OK
```

The demo can be restored to its intentionally failing baseline with:

```powershell
python .\examples\reset_buggy_demo.py
```

---

## Evaluation

DevFlow was evaluated using live Gemini runs together with the production skills and workspace tools.

| Scenario | Expected skill | Actual skill | Result |
|---|---|---|---|
| Repository overview | `repo-understanding` | `repo-understanding` | Complete |
| Execution and data-flow tracing | `repo-understanding` | `repo-understanding` | Complete |
| Runtime debugging | `debug-and-fix` | `debug-and-fix` | Complete |
| Failing-test debugging | `debug-and-fix` | `debug-and-fix` | Complete and verified |
| Simple file listing | None | None | Complete |
| Production-only issue without logs or fixtures | `debug-and-fix` | None | Safe partial result |

**5 of 6 scenarios matched the expected skill-routing behavior.**

In the remaining ambiguous production-only scenario, the agent still behaved safely: it gathered available evidence, made no unsupported changes, and clearly stated that the reported issue could not be reproduced or fully verified.

The complete evaluation record is available in [`evals/phase4-evaluation.md`](evals/phase4-evaluation.md).

---

## Automated Validation

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

Current result:

```text
Ran 21 tests
OK
```

Tests cover areas including:

- workspace containment
- filesystem tools
- normalized tool failures
- command restrictions and timeouts
- tool-registry dispatch
- agent-loop failure handling
- Agent Skill discovery and validation
- metadata-only startup context
- progressive skill loading
- independent workspace and skill-library paths
- production-skill discovery and loading
- Windows UTF-8 console handling

---

## Installation

### Requirements

- Python 3.14+
- Gemini API key

Clone the repository and create a virtual environment:

```powershell
git clone <your-repository-url>
cd DevFlow

python -m venv env
.\env\Scripts\Activate.ps1
```

Install DevFlow:

```powershell
pip install -e .
```

Create a `.env` file based on `.env.example`:

```text
GEMINI_API_KEY=your_api_key_here
```

The current default model is:

```text
gemini-3.5-flash-lite
```

A different Gemini model can be selected with the `GEMINI_MODEL` environment variable.

---

## Usage

### Understand a repository

```powershell
python .\main.py --workspace . --verbose "Explain what this repository does, its architecture, main entry points, and execution flow."
```

### Debug another project

```powershell
python .\main.py --workspace "D:\Projects\ExampleApp" --verbose "Run this application, diagnose the failure, make the smallest reasonable fix, and verify it."
```

### Use an explicit skill library

```powershell
python .\main.py --workspace "D:\Projects\ExampleApp" --skills-dir .\.github\skills --verbose "Explain this repository."
```

After installation, the package also exposes the `devflow` CLI entry point.

---

## Project Structure

```text
DevFlow/
├── .github/
│   └── skills/
│       ├── debug-and-fix/
│       │   └── SKILL.md
│       └── repo-understanding/
│           └── SKILL.md
├── devflow/
│   ├── agent/
│   │   ├── prompts.py
│   │   └── runtime.py
│   ├── skills/
│   │   ├── manager.py
│   │   └── parser.py
│   ├── tools/
│   │   ├── execution.py
│   │   ├── filesystem.py
│   │   ├── registry.py
│   │   └── workspace.py
│   ├── cli.py
│   └── gemini.py
├── evals/
│   └── phase4-evaluation.md
├── examples/
│   ├── buggy-demo/
│   └── reset_buggy_demo.py
├── tests/
├── main.py
├── pyproject.toml
└── .env.example
```

---

## Safety and Limitations

DevFlow applies several safeguards:

- file operations are restricted to the selected workspace
- workspace-escape attempts are rejected
- `.env` secrets are excluded from routine file access
- subprocesses do not inherit DevFlow's Gemini credentials
- commands run with `shell=False`
- command execution has bounded timeouts
- only an allowlisted set of development executables can be invoked
- Git access is limited to selected read-only subcommands
- agent execution has a maximum iteration count

`run_command` is **not an operating-system sandbox**. Allowed executables still run with the permissions of the DevFlow process.

The current evaluation is intentionally small and should be treated as an engineering validation exercise rather than a statistical benchmark.

---

## Future Work

Potential next steps include:

- **Open-source and local model support** through providers such as Ollama or vLLM
- **Model-provider abstraction** to reduce dependency on a single LLM backend
- **MCP integrations** for external engineering systems such as GitHub, project-management tools, documentation platforms, and internal APIs
- **Retrieval-augmented context** when workflows require knowledge outside the active repository
- **Expanded skill-routing evaluation** across larger and more ambiguous task sets
- **VS Code / GitHub Copilot portability validation** using the same `SKILL.md` capabilities
- **Additional engineering skills** only where a repeated workflow justifies them

---

## Design Principles

1. Inspect before editing.
2. Prefer evidence over assumptions.
3. Make focused changes.
4. Treat tool failures as observations.
5. Verify before reporting success.
6. Keep execution finite.
7. Separate reusable procedural knowledge from the core agent runtime.
8. Avoid adding architecture without a demonstrated need.
