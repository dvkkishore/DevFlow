# DevFlow AI

> A custom VS Code engineering agent with reusable Agent Skills for understanding repositories, debugging code, and assisting with everyday software/AI development workflows.

> [!NOTE]
> **Status: Active development**
>
> The agent-loop tutorial foundation is complete. DevFlow is now moving from a tutorial coding agent into an original custom-agent project built around reusable `SKILL.md` capabilities inside VS Code/Copilot.

---

## 1. What DevFlow Is

DevFlow is a developer-focused custom agent intended for tasks I repeatedly perform across software and AI projects:

- returning to an unfamiliar or older repository and quickly understanding it
- locating important files, entry points, and execution flow
- diagnosing runtime errors and failing tests
- making minimal fixes and verifying them
- assisting with repeatable engineering workflows such as experiment tracking

The project is **not** a generic chatbot and is **not** just a collection of Markdown prompts.

The main product is the **DevFlow custom agent**. Agent Skills provide modular, reusable capabilities that the agent can load for specific workflows.

```text
                         DevFlow
                      Custom Agent
                           |
              +------------+------------+
              |                         |
              v                         v
      Repository Understanding     Debug & Fix
              Skill                    Skill
              |                         |
              +------------+------------+
                           |
                           v
                    VS Code Tools
                read / search / edit
                 terminal / tests
                           |
                           v
                    Real Repository
```

A third ML Experiment skill may be added after the core two workflows are complete.

---

## 2. How the Project Started

Before building the final DevFlow agent, a minimal coding agent was implemented from first principles while following the freeCodeCamp Agentic AI tutorial:

**Build an AI Coding Agent with Python**  
https://youtu.be/YtHdaXuOAks

That implementation was used to learn the mechanics behind an agent runtime:

- LLM API calls
- system instructions
- conversation state
- function declarations
- tool/function calling
- tool dispatch
- feeding tool results back to the model
- iterative agent execution
- file reading/writing
- Python execution

The tutorial implementation is now considered a **foundation/reference implementation**, not the final DevFlow architecture.

Current tutorial tools:

```text
get_files_info
get_file_content
write_file
run_python_file
```

The tutorial code will be kept for attribution and to demonstrate the underlying agent loop, but the main DevFlow work begins from the custom-agent and Agent-Skills layer.

---

## 3. Core Concept

DevFlow separates three ideas clearly:

```text
Agent
  = the specialized engineering assistant that owns the overall behavior

Skill
  = reusable procedural knowledge for a particular workflow

Tool
  = an operation the agent can actually perform
```

Example:

```text
User: "This project crashes when I run main.py. Diagnose and fix it."

DevFlow Agent
      |
      v
loads Debug & Fix Skill
      |
      v
inspect files
      |
      v
run application
      |
      v
observe traceback
      |
      v
inspect relevant code
      |
      v
apply minimal fix
      |
      v
run again / test
      |
      v
verified result
```

The project should demonstrate this complete workflow rather than merely storing instructions in a `SKILL.md` file.

---

## 4. Current State

### Completed: Phase 0 - Agent Runtime Foundation

The tutorial coding agent is implemented with:

- Gemini API integration
- system prompt
- conversation history
- function schemas
- function-call dispatcher
- file inspection
- file reading
- file writing
- Python execution
- iterative agent loop

This phase exists to demonstrate understanding of the mechanics beneath higher-level agent platforms.

### Next: DevFlow Proper

Development now focuses on the custom VS Code agent and reusable Agent Skills.

---

## 5. Immediate Build Plan

### Phase 1 - Repository Cleanup and Foundation

Goal: turn the tutorial repository into a clean base for the actual DevFlow project.

Tasks:

- [ ] Move/rename `YT Project` to a clearly attributed reference location such as `examples/agent-loop-from-scratch`
- [ ] Remove generated `__pycache__` / `.pyc` files from Git tracking
- [ ] Ensure `.env` and virtual environments are ignored
- [ ] Add `.env.example` with no secrets
- [ ] Keep tutorial attribution visible
- [ ] Confirm the tutorial implementation still runs after cleanup
- [ ] Do not add unrelated frameworks or architecture

Target:

```text
examples/
└── agent-loop-from-scratch/
```

---

### Phase 2 - DevFlow Custom Agent

Create:

```text
.github/agents/devflow.agent.md
```

The custom agent should behave as a practical engineering assistant.

Core behavior:

- inspect relevant context before modifying files
- prefer focused/minimal changes
- use specialized skills when appropriate
- use available workspace and terminal tools to gather evidence
- verify code changes when execution/testing is available
- never claim successful execution without evidence
- avoid unrelated refactors during debugging
- clearly summarize changes and verification

The custom agent is the central component of DevFlow.

---

### Phase 3 - Repository Understanding Skill

Create:

```text
.github/skills/repo-understanding/
├── SKILL.md
└── references/
    └── analysis-checklist.md
```

Purpose:

Help DevFlow quickly understand an unfamiliar repository.

Expected workflow:

1. Inspect repository structure.
2. Identify important manifests/configuration.
3. Identify application entry points.
4. Detect main languages/frameworks.
5. Locate major modules.
6. Trace the requested execution/data flow.
7. Avoid reading irrelevant files.
8. Distinguish observed facts from assumptions.
9. Produce a concise architecture/context summary.

Example prompts:

```text
"What do we have in this repository and how does it work?"

"I have not touched this project in three months. Give me the context I need to continue working on it."

"Trace the flow from input data to model output."
```

This is intended to be a genuine daily-use workflow.

---

### Phase 4 - Debug & Fix Skill

Create:

```text
.github/skills/debug-and-fix/
├── SKILL.md
└── references/
    └── debugging-checklist.md
```

Purpose:

Perform evidence-driven debugging and verification rather than giving generic suggestions.

Required workflow:

```text
Understand problem
      |
      v
Reproduce failure
      |
      v
Collect evidence
      |
      v
Identify likely root cause
      |
      v
Apply minimal fix
      |
      v
Run/test again
      |
      +---- fail ---> investigate again
      |
      +---- pass ---> report verified result
```

Rules:

- reproduce first when possible
- inspect evidence before editing
- distinguish root cause from symptom
- make the smallest reasonable change
- do not stack speculative patches
- rerun the original failing scenario
- do not report success without verification when tools are available

This should become the main DevFlow demo.

---

### Phase 5 - Demo Project and Evaluation

Create one intentionally broken sample project under:

```text
examples/buggy-demo/
```

The demo should be small enough to understand but non-trivial enough to require multiple agent actions.

Primary demo prompt:

```text
"Run this application, find why it fails, apply the smallest reasonable fix, and verify that the issue is resolved."
```

Expected DevFlow behavior:

```text
inspect -> execute -> observe -> investigate -> edit -> execute -> verify
```

Add a small evaluation file:

```text
evals/scenarios.md
```

Initial scenarios should verify behaviors such as:

| Scenario | Expected behavior |
|---|---|
| Explain unfamiliar repository | Repository skill is relevant |
| Runtime traceback | Debug skill is relevant |
| Failing unit test | Debug skill is relevant |
| Simple README edit | Specialized skill is not required |
| Fix still fails | Agent must not claim success |
| Missing information discoverable in repo | Inspect before asking user |
| Unrelated refactor opportunity | Do not refactor during targeted fix |
| Successful repair | Report exact verification performed |

The goal is not a large benchmark. The goal is to demonstrate deliberate evaluation of agent behavior.

---

### Phase 6 - Optional ML Experiment Skill

Only start this after the custom agent, repository skill, debugging skill, and demo are complete.

Potential structure:

```text
.github/skills/ml-experiment/
├── SKILL.md
├── scripts/
│   └── compare_metrics.py
└── templates/
    └── experiment-report.md
```

Possible workflow:

```text
inspect experiment setup
      -> run controlled variants
      -> collect metrics
      -> compare results
      -> record configuration
      -> summarize findings
```

This is optional for the first public release.

---

## 6. Target Repository Structure

```text
devflow/
|
├── .github/
│   ├── agents/
│   │   └── devflow.agent.md
│   │
│   └── skills/
│       ├── repo-understanding/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── analysis-checklist.md
│       │
│       ├── debug-and-fix/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── debugging-checklist.md
│       │
│       └── ml-experiment/              # optional / later
│           ├── SKILL.md
│           ├── scripts/
│           └── templates/
│
├── examples/
│   ├── agent-loop-from-scratch/
│   └── buggy-demo/
│
├── evals/
│   └── scenarios.md
│
├── docs/
│   └── architecture.md
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

The final structure should remain small. Do not create placeholder directories unless they are needed by the current phase.

---

## 7. Scope for the First Portfolio Release

### Required

- [ ] Tutorial agent-loop implementation preserved and attributed
- [ ] Clean public repository
- [ ] DevFlow custom VS Code agent
- [ ] Repository Understanding Agent Skill
- [ ] Debug & Fix Agent Skill
- [ ] At least one real multi-step demo
- [ ] Small behavior-evaluation set
- [ ] Clear architecture and README

### Optional

- [ ] ML Experiment Skill
- [ ] Additional helper scripts
- [ ] Expanded evaluation scenarios

### Explicitly Out of Scope for Now

Do **not** add the following unless the scope changes later:

- MCP
- LangGraph
- CrewAI
- AutoGen
- multi-agent orchestration
- RAG/vector databases
- web frontend
- database
- authentication
- cloud deployment
- long-term memory

The first version should demonstrate a focused, understandable custom agent with high-quality skills rather than a large stack of unrelated AI technologies.

---

## 8. Implementation Rules While Building

When working on this repository:

1. Follow the phases in order.
2. Do not implement later phases unless explicitly requested.
3. Do not introduce a framework merely because one exists.
4. Keep the tutorial implementation clearly separated from original DevFlow work.
5. Preserve attribution for tutorial-derived code.
6. Prefer small, reviewable changes.
7. Do not create fake test results, benchmark numbers, screenshots, or claims.
8. When adding a skill, build a workflow that can be demonstrated on an actual repository.
9. Keep `SKILL.md` focused; move large checklists/templates/scripts into supporting files when useful.
10. Treat verification behavior as a core DevFlow feature.
11. Do not put secrets, API keys, virtual environments, caches, or generated files into Git.
12. Update this README when the project scope or completed phases materially change.

---

## 9. Success Criteria

The first portfolio version of DevFlow is successful if it can demonstrate the following story clearly:

> I first implemented a minimal coding-agent loop from scratch with Gemini to understand function calling, tool execution, observations, and iterative agent behavior. I then used that understanding to build DevFlow as a custom VS Code engineering agent with reusable Agent Skills for repository understanding and evidence-driven debugging. The agent applies those skills to real code, uses development tools to act on the workspace, and verifies its changes instead of only generating suggestions.

A reviewer should be able to understand this story from the repository without needing additional explanation.

---

## 10. Attribution

The initial agent-loop reference implementation was developed while following the freeCodeCamp tutorial:

**Build an AI Coding Agent with Python**  
https://youtu.be/YtHdaXuOAks

That implementation is retained as an educational foundation and is not presented as original DevFlow functionality.

DevFlow-specific custom-agent configuration, Agent Skills, workflows, evaluation scenarios, examples, documentation, and subsequent engineering work are developed as extensions beyond the tutorial.
