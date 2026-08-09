# DevFlow AI

> A standalone AI engineering agent that understands repositories, uses developer tools, fixes code, verifies its work, and supports portable Agent Skills.

> [!IMPORTANT]
> **Current phase: Phase 2.1 skill-library portability complete — awaiting review before Phase 3.**
>
> Phase 1A transformed the tutorial implementation into DevFlow Core. Phase 2 added progressive `SKILL.md` loading, and Phase 2.1 separated the read-only skill library from the writable target workspace. Production skills have not been written yet.

---

## 1. Product Definition

DevFlow is a **standalone tool-using engineering agent**, not a chatbot and not a collection of Markdown prompts.

It should operate on a user-selected software repository and be able to:

- inspect and understand a codebase
- locate relevant files/code
- trace execution flow
- run programs/tests
- observe errors and command output
- make focused code changes
- rerun verification
- iterate when a fix fails
- later load reusable `SKILL.md` procedures

Core behavior:

```text
User request
    ↓
DevFlow Agent
    ↓
LLM decides next action
    ↓
Tool call
    ↓
Execute inside workspace
    ↓
Return observation
    ↓
LLM decides again
    ↓
... repeat until complete
```

DevFlow should never claim that a fix works without attempting verification when execution is available.

---

## 2. Where the Existing Tutorial Code Fits

The initial coding agent was built while following the freeCodeCamp Agentic AI tutorial. It already provides the foundation:

- Gemini API interaction
- system prompt
- conversation state
- function declarations
- tool calling
- tool dispatch
- file read/write
- Python execution
- iterative agent loop

That stage is complete.

From now on:

```text
Tutorial-derived working agent
            ↓ refactor
      DevFlow Agent Core
            ↓
      Developer Tool Layer
            ↓
       Portable Skills
            ↓
     Evaluation + Demo
```

Do **not** create a second agent beside the tutorial agent. Transform the existing implementation.

---

## 3. Target Architecture

```text
                         DevFlow
                            │
                    ┌───────▼────────┐
                    │  Agent Runtime │
                    │                │
                    │ agent loop     │
                    │ context        │
                    │ system rules   │
                    └───┬────────┬───┘
                        │        │
                 skills │        │ tools
                        │        │
              ┌─────────▼──┐  ┌──▼───────────┐
              │Skill Manager│  │Tool Registry │
              └─────┬──────┘  └──────┬───────┘
                    │                │
           ┌────────┴───────┐        ├─ list/search
           │                │        ├─ read
           ▼                ▼        ├─ write
 repo-understanding   debug-and-fix  ├─ run command
      SKILL.md            SKILL.md    └─ verify
```

For V1, Gemini is the model backend. DevFlow itself must not be designed as a Gemini-only product.

---

## 4. Design Rules

1. **Inspect before editing.** Gather relevant context first.
2. **Evidence over guessing.** Use files, stack traces, logs, tests, and command output.
3. **Minimal changes.** Avoid unrelated refactoring.
4. **Verify before success.** Run an appropriate command/test after changes when possible.
5. **Workspace isolation.** Tools may not access paths outside the selected repository.
6. **Errors become observations.** Tool failures should return to the agent instead of crashing the runtime.
7. **Finite execution.** Use a maximum agent-loop iteration count.
8. **Provider independence.** Keep Gemini-specific code separated enough to support another model later.
9. **Do not over-engineer.** Add abstractions only when they solve a current design problem.

---

## 5. Current V1 Tools

Refactor the tutorial tools into a clean DevFlow tool layer.

Required V1 capabilities:

```text
list_files
read_file
search_files
write_file
run_command
```

`run_tests` may be added later if useful, but `run_command` should already support verification workflows.

### Tool registry

Do not continue growing an `if/elif` dispatcher. Use an explicit registry or equivalent maintainable design.

Concept:

```python
TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "search_files": search_files,
    "write_file": write_file,
    "run_command": run_command,
}
```

### Tool results

Tools should return a predictable result structure, for example:

```python
@dataclass
class ToolResult:
    success: bool
    output: str = ""
    error: str | None = None
```

Use a simpler equivalent if appropriate.

---

## 6. Workspace and Execution Safety

DevFlow must receive an explicit workspace.

Desired interface concept:

```bash
python main.py --workspace ./project --skills-dir ./.github/skills "Explain this repository"
```

All tool paths must resolve inside that workspace.

`--workspace` selects the repository that file and command tools may inspect, modify, and execute in. The optional `--skills-dir` selects one separate read-only Agent Skills library; when omitted, it defaults to DevFlow's own `.github/skills/` directory.

Required safeguards:

- prevent `../` or equivalent workspace escape
- do not expose `.env` secrets unnecessarily
- use command timeouts
- validate tool arguments
- return stdout/stderr and exit status as observations
- do not automatically run destructive operations such as recursive deletion or `git reset --hard`

### `run_command` boundary

`run_command` uses the selected workspace as the subprocess current directory, passes arguments with `shell=False`, applies a bounded timeout, removes DevFlow's Gemini credentials from the child environment, and restricts Git to a small read-only subcommand set.

This is a workspace-CWD safety boundary, not an OS-level sandbox. An allowed development executable still runs with the operating-system permissions of the DevFlow process.

---

## 7. Model Provider Boundary

Gemini is the current backend only.

Keep model-specific behavior behind a small boundary so a future provider can be added without rewriting DevFlow's tools/skills.

Concept only:

```python
class ModelProvider:
    def generate(self, messages, tools):
        ...

class GeminiProvider(ModelProvider):
    ...
```

Do **not** implement other providers now.

Future possibilities may include Ollama, vLLM, Qwen/Llama, or another OpenAI-compatible endpoint.

---

## 8. Agent Skills: Phase After Core Agent

A skill is reusable procedural knowledge, not an executable tool.

```text
Tool  = what the agent can do
Skill = how the agent should handle a class of tasks
Agent = model + context + skills + tools + loop
```

Use portable project skills:

```text
.github/
└── skills/
    ├── repo-understanding/
    │   └── SKILL.md
    └── debug-and-fix/
        ├── SKILL.md
        └── references/
            └── debugging-checklist.md
```

The same skill files should remain usable by skills-compatible hosts such as GitHub Copilot where practical.

### Progressive loading

Do not inject all skill contents into every request.

```text
discover skills
    ↓
load name + description
    ↓
identify relevant skill
    ↓
load that SKILL.md
    ↓
load supporting files only if needed
```

V1 needs only two skills:

1. `repo-understanding`
2. `debug-and-fix`

Do not build ML Experiment skill yet.

---

## 9. Initial Skill Behaviors

### Repository Understanding

Typical requests:

```text
What is in this repository and how does it work?
```

```text
I have not touched this project recently. Give me enough context to continue development.
```

Expected workflow:

1. inspect repository structure
2. identify language/framework/dependency files
3. identify likely entry points
4. inspect relevant modules only
5. trace important relationships/execution paths
6. distinguish observed facts from assumptions
7. summarize architecture and continuation points

### Debug and Fix

Typical request:

```text
Run this project, find why it fails, fix it, and verify the fix.
```

Expected workflow:

```text
reproduce
   ↓
observe evidence
   ↓
inspect relevant code
   ↓
form hypothesis
   ↓
minimal fix
   ↓
verify
  ↙   ↘
fail  pass
 ↓      ↓
iterate report
```

Never report success if verification still fails.

---

## 10. Target Repository Direction

Do not create every file immediately. Refactor toward a structure similar to:

```text
DevFlow/
├── devflow/
│   ├── agent/
│   │   ├── runtime.py
│   │   ├── context.py
│   │   └── prompts.py
│   ├── providers/
│   │   └── gemini.py
│   ├── tools/
│   │   ├── registry.py
│   │   ├── filesystem.py
│   │   └── execution.py
│   └── skills/
│       ├── manager.py
│       └── parser.py
│
├── .github/
│   └── skills/
│       ├── repo-understanding/
│       │   └── SKILL.md
│       └── debug-and-fix/
│           └── SKILL.md
│
├── examples/
│   └── buggy-project/
├── evals/
├── tests/
├── main.py
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

Prefer a simpler structure if it keeps responsibilities clear.

---

# Development Plan

## Phase 0 — Agentic Fundamentals ✅ COMPLETE

The current implementation already demonstrates:

- [x] Gemini API connection
- [x] system instructions
- [x] conversation state
- [x] function declarations
- [x] tool calls
- [x] execution of tools
- [x] returning observations
- [x] iterative agent loop

The final repository does not need a separate tutorial project.

---

## Phase 1A — DevFlow Core ✅ COMPLETE

**Goal:** turn the existing implementation into a safe, clean standalone engineering agent. Do not implement skills yet.

Tasks:

- [x] rename/remove tutorial-specific naming and assumptions
- [x] introduce DevFlow system instructions
- [x] make workspace explicit
- [x] enforce workspace path containment
- [x] refactor tool dispatch into a registry
- [x] normalize tool error handling/results
- [x] add `search_files`
- [x] provide controlled `run_command`
- [x] add command timeout
- [x] add maximum agent-loop iterations
- [x] isolate Gemini-specific code from the runtime where useful
- [x] add `.env.example`
- [x] clean `.gitignore`
- [x] remove virtualenv/cache/generated files from tracked/public content
- [x] add basic tool/runtime tests

### Phase 1 acceptance tests

DevFlow should independently handle:

```text
"Explain what this repository contains and how its main components relate."
```

and:

```text
"Run this application, identify the failure, fix it, and verify the result."
```

using the target workspace and the generic DevFlow tool loop.

**Phase 1A was reviewed and approved before Phase 2 began.**

---

## Phase 2 — Portable Agent Skill Runtime ✅ COMPLETE

- [x] discover skill folders from `.github/skills/`
- [x] parse and validate YAML skill metadata
- [x] expose only available skill names and descriptions to the agent
- [x] load one selected `SKILL.md` through the read-only `load_skill` tool
- [x] return clean errors for unknown and invalid skills
- [x] avoid loading every skill body into every prompt
- [x] leave scripts and referenced resources unloaded and unexecuted

Acceptance test:

> A fixture skill is represented in startup context by name and description only, then its complete `SKILL.md` is returned after the model requests `load_skill` and the agent loop continues.

Production workflow selection is deferred to the Phase 3 skills.

---

## Phase 2.1 — Skill Library Portability ✅ COMPLETE

- [x] accept one optional explicit `--skills-dir`
- [x] keep skill discovery/loading separate from the target workspace
- [x] keep the skill library read-only while workspace tools remain target-scoped
- [x] preserve metadata-only startup context and on-demand `load_skill`
- [x] validate skill names at 64 characters or fewer
- [x] validate skill descriptions at 1024 characters or fewer
- [x] retain all Phase 1A and Phase 2 tests

Production skills remain deferred to Phase 3.

---

## Phase 3 — Two Production-Style Skills

- [ ] `repo-understanding/SKILL.md`
- [ ] `debug-and-fix/SKILL.md`
- [ ] realistic tests/demo for each

---

## Phase 4 — Evaluation and Demo

Keep evaluation small and practical.

Example scenarios:

| Request | Expected behavior |
|---|---|
| Explain this repository | repo-understanding skill |
| Trace the execution path | repo-understanding skill |
| Why does this test fail? Fix it | debug-and-fix skill |
| Rename README heading | no specialized skill needed |
| Fix still fails after modification | do not report success |
| Request path outside workspace | refuse tool access |

Measure where practical:

- skill selection
- tool selection
- task completion
- verification success
- tool failure handling
- unverified-success rate
- workspace-boundary compliance

---

## 11. Codex Rules for the Current Build

1. Treat this README as the current project specification.
2. Phase 2.1 is complete; stop for review before starting Phase 3 production skills.
3. Transform the existing agent; do not create a separate replacement agent.
4. Do not preserve `YT Project` as a final project/example directory.
5. Do not create production skills until the Phase 2 runtime is reviewed.
6. Do not add MCP, RAG, LangGraph, CrewAI, AutoGen, multi-agent systems, vector databases, UI, database, cloud deployment, or local-model support now.
7. Do not rewrite working code only to match the target directory tree.
8. Make small, reviewable changes and keep the project runnable after each step.
9. Verify relevant behavior after modifications and report actual command/test results.
10. Never fabricate successful execution or test results.
11. Ask/present reasoning before making a major architectural change outside this specification.
12. Preserve appropriate attribution for materially adapted tutorial code, but do not make the tutorial the identity of the final project.

---

## 12. Non-Goals for V1

Do not implement these now:

```text
MCP
RAG
vector database
LangGraph
CrewAI
AutoGen
multi-agent orchestration
web/mobile UI
database
authentication
cloud deployment
local/open-source model runtime
long-term memory
```

---

## 13. Future Roadmap

Possible future extensions, only after V1:

### Open-source / local models

Add another provider (for example through Ollama/vLLM) for privacy, flexibility, model control, reduced vendor dependency, or cost optimization.

### MCP

Connect external tools/services such as GitHub, Jira, Linear, internal APIs, or documentation platforms.

### RAG

Use retrieval only when DevFlow needs knowledge outside the active repository, such as internal engineering documentation, coding standards, architecture decisions, or historical incident reports.

### Additional skills

Possible later capabilities:

- ML experiment management
- code review
- dependency analysis
- release preparation
- test generation
- documentation workflows

---

## 14. Attribution

The initial agent-loop implementation was informed by the freeCodeCamp Agentic AI coding-agent tutorial:

https://youtu.be/YtHdaXuOAks

The tutorial was used to learn the underlying LLM tool-calling and iterative agent-loop mechanics. DevFlow is the subsequent refactoring and extension into a standalone engineering agent with its own runtime structure, developer tools, safety boundaries, portable skill system, tests, and evaluation.

Retain attribution where external source code was materially adapted.

---

## 15. Definition of V1 Done

DevFlow V1 is complete when:

- [ ] standalone DevFlow works against an explicit workspace
- [ ] file tools cannot escape that workspace
- [ ] DevFlow can list/search/read/write relevant files
- [ ] DevFlow can execute controlled commands and observe results
- [ ] tool failures return to the agent cleanly
- [ ] agent loop has a maximum iteration limit
- [ ] model backend is not entangled with the entire application
- [ ] DevFlow discovers and progressively loads `SKILL.md` skills
- [ ] repo-understanding skill works on a realistic repository
- [ ] debug-and-fix skill reproduces, repairs, and verifies a realistic defect
- [ ] basic tests cover critical runtime/tool safety
- [ ] small evaluation demonstrates correct skill/tool behavior
- [ ] public repository contains no secrets, virtual environment, cache files, or tutorial-only artifacts
