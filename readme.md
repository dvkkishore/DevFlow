# DevFlow AI

> An agentic AI engineering assistant for understanding codebases, debugging software, and assisting with machine learning experiments through reusable VS Code Agent Skills.

> [!NOTE]
> **Status: Work in Progress**
>
> DevFlow is being built iteratively. The first milestone establishes a minimal coding-agent skeleton based on a public Agentic AI tutorial. The project then extends that foundation into an original developer workflow assistant with custom tools, reusable `SKILL.md` capabilities, VS Code integration, testing, and practical engineering workflows.

---

## 1. Overview

Developers repeatedly perform the same kinds of tasks while working across software and AI projects:

- understanding an unfamiliar repository
- locating relevant files
- tracing execution flow
- debugging errors
- modifying code
- running and verifying fixes
- comparing machine learning experiments
- documenting what changed

DevFlow explores how an LLM-based agent can perform these workflows through an iterative tool-using loop rather than simply answering questions in a chat interface.

The project focuses on three reusable engineering capabilities:

1. **Repository Understanding**
2. **Debug and Fix**
3. **ML Experiment Assistance**

These capabilities are implemented as reusable VS Code Agent Skills using `SKILL.md`.

---

# 2. Project Development Strategy

DevFlow is intentionally being developed in stages.

The first stage is not the final DevFlow system.

Instead, the project begins by implementing a minimal coding agent from first principles in order to understand the mechanics behind agentic AI.

The initial skeleton is developed while following the freeCodeCamp tutorial:

**"Build an AI Coding Agent with Python"**

Tutorial:
https://youtu.be/YtHdaXuOAks

The tutorial provides the foundation for understanding:

- LLM API interaction
- system instructions
- conversation history
- function declarations
- function/tool calling
- file-system tools
- code execution
- iterative agent loops
- feeding tool results back to the model

A small calculator/code example from the tutorial is initially used to validate that the basic agent loop works.

This tutorial implementation is treated only as the **learning skeleton** of DevFlow.

From that point onward, the repository is extended into the original DevFlow system described below.

---

# 3. From Tutorial Skeleton to DevFlow

The development path is:

```text
Tutorial Coding Agent
        |
        |  Learn the fundamentals
        v
Basic Agent Loop
        |
        |  Extend tools and behaviour
        v
DevFlow Core Agent
        |
        |  Add reusable procedures
        v
VS Code Agent Skills
        |
        |  Apply to real engineering workflows
        v
Repository Analysis
Debugging
ML Experiments
        |
        |  Verify behaviour
        v
Tests + Evaluation
````

The intention is therefore not to reproduce the tutorial project.

The tutorial provides the smallest working implementation required to understand how an agent works internally.

DevFlow then applies those concepts to workflows that are useful in everyday software and AI engineering.

---

# 4. Core Agent Loop

At the center of DevFlow is an iterative agent loop.

```text
User Request
     |
     v
LLM
     |
     | decides whether an action is required
     v
Tool Selection
     |
     v
Tool Execution
     |
     v
Observation / Tool Result
     |
     v
LLM
     |
     | continue reasoning
     |
     +----> another tool call
     |
     +----> final response
```

Example:

```text
User:
"Find why this application crashes and fix it."

Agent
  |
  +--> inspect repository
  |
  +--> read relevant files
  |
  +--> execute application
  |
  +--> observe traceback
  |
  +--> inspect failing code
  |
  +--> modify implementation
  |
  +--> execute application again
  |
  +--> verify result
  |
  +--> explain the fix
```

The important difference from a normal chatbot is that DevFlow can interact with the development environment, observe results, and use those observations to decide what to do next.

---

# 5. DevFlow Capabilities

## 5.1 Repository Understanding

DevFlow should be able to inspect a repository and build a useful mental model of it.

Example request:

```text
Understand this repository and explain how data flows from the
input through preprocessing to the model output.
```

The agent should:

1. inspect the repository structure
2. identify important configuration files
3. identify application entry points
4. detect languages and frameworks
5. inspect relevant modules
6. trace important execution paths
7. identify missing or ambiguous information
8. summarize the architecture

Reusable skill:

```text
.github/skills/repo-understanding/SKILL.md
```

---

## 5.2 Debug and Fix

DevFlow should autonomously investigate software failures instead of only suggesting possible fixes.

Example:

```text
The application fails when I run main.py.
Find the problem, make the smallest reasonable fix,
and verify that the program works.
```

Expected workflow:

```text
Reproduce Error
      |
      v
Inspect Traceback
      |
      v
Identify Relevant Code
      |
      v
Form Hypothesis
      |
      v
Apply Minimal Fix
      |
      v
Run Again
      |
      +---- failure ----> investigate again
      |
      +---- success ----> explain and verify
```

Reusable skill:

```text
.github/skills/debug-and-fix/SKILL.md
```

The agent must never claim that a fix works without attempting to verify it when execution tools are available.

---

## 5.3 ML Experiment Assistant

DevFlow should also support workflows commonly encountered during AI development.

Example:

```text
Compare the current model using learning rates
1e-3 and 1e-4 and summarize the results.
```

Possible workflow:

```text
Inspect training pipeline
        |
        v
Understand configuration
        |
        v
Run experiment A
        |
        v
Collect metrics
        |
        v
Run experiment B
        |
        v
Collect metrics
        |
        v
Compare runs
        |
        v
Update experiment log
```

Reusable skill:

```text
.github/skills/ml-experiment/SKILL.md
```

Potential outputs include:

* experiment configuration
* execution status
* metrics
* comparison tables
* observations
* recommended next experiment

---

# 6. VS Code Agent Skills

One of the main extensions beyond the original tutorial is the introduction of reusable Agent Skills.

Planned structure:

```text
.github/
|
├── agents/
│   └── devflow.agent.md
│
└── skills/
    |
    ├── repo-understanding/
    │   └── SKILL.md
    │
    ├── debug-and-fix/
    │   ├── SKILL.md
    │   └── references/
    │       └── debugging-checklist.md
    │
    └── ml-experiment/
        ├── SKILL.md
        ├── templates/
        │   └── experiment-log.md
        └── scripts/
            └── collect_metrics.py
```

Each skill contains domain-specific procedures that can be loaded when the corresponding workflow is required.

The goal is to separate:

```text
Agent
    = general behaviour and available capabilities

Tool
    = an operation the agent can execute

Skill
    = reusable procedural knowledge describing how to solve
      a particular class of tasks
```

---

# 7. DevFlow Custom Agent

The project will include a custom VS Code agent:

```text
.github/agents/devflow.agent.md
```

Its role is to behave as an engineering assistant with several key principles:

* inspect relevant context before making changes
* prefer minimal modifications
* use available skills when applicable
* execute tools only when needed
* observe tool results before continuing
* verify code changes where possible
* avoid claiming unverified success
* clearly describe modifications and reasoning
* preserve existing project behaviour unless a change is required

---

# 8. Core Tools

The initial agent skeleton provides a small collection of tools.

Initial tools:

```text
get_files_info
get_file_content
write_file
run_python_file
```

These establish the basic agentic interaction loop.

DevFlow may later extend these with development-oriented capabilities such as:

```text
search_files
run_tests
inspect_git_diff
collect_metrics
parse_test_results
inspect_project_configuration
```

The goal is not to give the agent an excessive number of tools.

Tools should be introduced only when they enable a clear engineering workflow.

---

# 9. Planned Architecture

```text
┌────────────────────────────────────┐
│                User                │
└─────────────────┬──────────────────┘
                  │
                  v
┌────────────────────────────────────┐
│          DevFlow AI Agent          │
│                                    │
│   System Instructions              │
│   Conversation Context             │
│   Tool Definitions                 │
└─────────────────┬──────────────────┘
                  │
           Skill Selection
                  │
        ┌─────────┼─────────┐
        │         │         │
        v         v         v
      Repo      Debug      ML
   Understanding & Fix   Experiment
      Skill      Skill      Skill
        │         │         │
        └─────────┼─────────┘
                  │
                  v
┌────────────────────────────────────┐
│             Tool Layer             │
│                                    │
│  Read Files                        │
│  Write Files                       │
│  Execute Code                      │
│  Run Tests                         │
│  Collect Results                   │
└─────────────────┬──────────────────┘
                  │
                  v
┌────────────────────────────────────┐
│        Local Project Workspace     │
└────────────────────────────────────┘
```

---

# 10. Repository Structure

Target structure:

```text
devflow-ai/
|
├── agent/
│   ├── main.py
│   ├── prompts.py
│   │
│   └── functions/
│       ├── get_files_info.py
│       ├── get_file_content.py
│       ├── write_file.py
│       └── run_python_file.py
│
├── .github/
│   ├── agents/
│   │   └── devflow.agent.md
│   │
│   └── skills/
│       ├── repo-understanding/
│       │   └── SKILL.md
│       │
│       ├── debug-and-fix/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── debugging-checklist.md
│       │
│       └── ml-experiment/
│           ├── SKILL.md
│           ├── templates/
│           │   └── experiment-log.md
│           └── scripts/
│               └── collect_metrics.py
│
├── examples/
│   ├── tutorial-calculator/
│   ├── buggy-application/
│   └── sample-ml-project/
│
├── tests/
│   ├── test_tools.py
│   └── test_agent_scenarios.py
│
├── docs/
│   └── architecture.md
│
├── README.md
├── requirements.txt
├── .env.example
└── LICENSE
```

The exact structure may evolve while the project is developed.

---

# 11. Development Milestones

## Phase 0 - Tutorial Skeleton

Goal:

Understand the mechanics of a coding agent by implementing the tutorial project.

Tasks:

* [ ] Configure LLM API
* [ ] Implement system instructions
* [ ] Maintain conversation history
* [ ] Implement function declarations
* [ ] Implement tool dispatch
* [ ] Read files
* [ ] Write files
* [ ] Execute Python files
* [ ] Implement iterative agent loop
* [ ] Complete tutorial calculator/debugging example

Deliverable:

```text
A minimal autonomous coding agent capable of reading,
modifying and executing code.
```

---

## Phase 1 - Refactor into DevFlow Core

Goal:

Separate the reusable agent infrastructure from the tutorial example.

Tasks:

* [ ] Refactor tool implementations
* [ ] Separate prompts from execution logic
* [ ] Improve project structure
* [ ] Add path and execution safety checks
* [ ] Improve error handling
* [ ] Add logging
* [ ] Create a clean command-line interface
* [ ] Remove tutorial-specific assumptions

Deliverable:

```text
Reusable DevFlow agent core.
```

---

## Phase 2 - Repository Understanding Skill

Tasks:

* [ ] Create `repo-understanding/SKILL.md`
* [ ] Define repository inspection procedure
* [ ] Detect project entry points
* [ ] Identify frameworks and dependencies
* [ ] Trace high-level execution flow
* [ ] Produce structured repository summaries
* [ ] Test against at least one real project

---

## Phase 3 - Debug and Fix Skill

Tasks:

* [ ] Create `debug-and-fix/SKILL.md`
* [ ] Create debugging checklist
* [ ] Reproduce errors before modifying code
* [ ] Inspect traceback and relevant files
* [ ] Apply minimal fixes
* [ ] Verify changes by rerunning the application
* [ ] Add an intentionally broken demo project

Primary demo scenario:

```text
"Find why this application fails, fix the problem,
and verify that the application works."
```

---

## Phase 4 - ML Experiment Skill

Tasks:

* [ ] Create `ml-experiment/SKILL.md`
* [ ] Create experiment-log template
* [ ] Add metric collection script
* [ ] Inspect experiment configuration
* [ ] Execute controlled experiments
* [ ] Compare metrics
* [ ] Generate experiment summaries

---

## Phase 5 - VS Code Custom Agent

Tasks:

* [ ] Create `devflow.agent.md`
* [ ] Connect reusable skills
* [ ] Test automatic skill selection
* [ ] Validate behaviour inside VS Code
* [ ] Document example workflows

---

## Phase 6 - Testing and Evaluation

Initial evaluation should focus on practical agent behaviour.

Potential scenarios:

```text
Repository understanding
Debugging
Successful code modification
Failed code modification
Tool failure
Invalid path
Runtime exception
Successful verification
ML experiment execution
```

Metrics may include:

```text
Task completion
Correct tool usage
Successful verification
Number of tool calls
Execution failures
Unverified-success rate
```

---

# 12. Example Use Cases

### Understand an unfamiliar repository

```text
"Analyze this repository and explain the main components,
entry points, and execution flow."
```

### Debug an application

```text
"Run this project, identify why it fails,
apply the smallest reasonable fix and verify it."
```

### Investigate code

```text
"Find where model predictions are post-processed
and explain how the output is generated."
```

### Run an ML experiment

```text
"Compare learning rates 0.001 and 0.0001
using the existing training pipeline."
```

### Review a change

```text
"Inspect the latest modifications and check whether
they introduce obvious runtime issues."
```

---

# 13. Scope

DevFlow currently focuses on:

* local software repositories
* Python-oriented engineering workflows
* agentic tool usage
* reusable Agent Skills
* autonomous debugging
* repository analysis
* ML experimentation
* verification of agent actions

---

# 14. Non-Goals

The initial version intentionally does not include:

* multi-agent systems
* MCP integrations
* vector databases
* RAG pipelines
* cloud deployment
* autonomous production deployment
* web application UI
* complex long-term memory

These capabilities may be explored later if they provide a clear benefit.

The current priority is understanding and implementing reliable agent behaviour with a small, explainable architecture.

---

# 15. What This Project Explores

DevFlow is primarily an engineering and learning project exploring:

### Agentic AI

How an LLM can repeatedly:

```text
observe -> decide -> act -> observe -> continue
```

rather than producing a single response.

### Tool Calling

How models select structured functions and how applications execute those functions safely.

### Agent Skills

How reusable procedural knowledge can specialize a general-purpose development agent.

### Context Engineering

How the agent receives enough information to perform a task without unnecessarily loading the entire repository.

### Verification

How an agent can validate its own modifications through execution and testing.

### Agent Reliability

How failures, tool errors, unsupported assumptions and incomplete verification should be handled.

---

# 16. Technology

Initial stack:

* Python
* Gemini API
* Git
* GitHub
* VS Code
* GitHub Copilot
* VS Code Agent Skills
* Markdown
* pytest

The stack may evolve during development.

---

# 17. Current Status

| Component                      | Status      |
| ------------------------------ | ----------- |
| Tutorial coding-agent skeleton | In Progress |
| Agent tool loop                | In Progress |
| DevFlow refactor               | Planned     |
| Repository Understanding Skill | Planned     |
| Debug and Fix Skill            | Planned     |
| ML Experiment Skill            | Planned     |
| VS Code custom agent           | Planned     |
| Automated tests                | Planned     |
| Evaluation scenarios           | Planned     |
| Demo                           | Planned     |

---

# 18. Demo Goal

The primary DevFlow demonstration will show an agent receiving an unfamiliar broken program and autonomously:

1. inspecting the repository
2. executing the application
3. observing the failure
4. locating the responsible code
5. applying a minimal correction
6. executing the program again
7. verifying that the issue has been resolved
8. summarizing the modification

This demonstrates the complete agent loop rather than a single LLM response.

---

# 19. Learning Objective

The purpose of building DevFlow from a minimal coding-agent implementation instead of immediately using a high-level agent framework is to understand the underlying mechanics directly.

This includes:

* how function schemas are exposed to an LLM
* how an LLM requests a tool call
* how the application executes the requested function
* how observations are returned to the model
* how conversation state is maintained
* how repeated tool calls form an agent loop
* how specialized skills influence agent behaviour
* how actions can be verified rather than assumed successful

Higher-level agent frameworks can then be evaluated with a clearer understanding of the abstractions they provide.

---

# 20. Attribution

The initial coding-agent skeleton was developed while following the freeCodeCamp Agentic AI tutorial:

[https://youtu.be/YtHdaXuOAks](https://youtu.be/YtHdaXuOAks)

The tutorial is used as an educational foundation for implementing the basic LLM tool-calling and agent-loop mechanics.

DevFlow extends this foundation with an original project structure, engineering use cases, reusable VS Code Agent Skills, repository-analysis workflows, autonomous debugging procedures, ML experimentation workflows, testing, evaluation and documentation.

Any source code directly adapted from external material will be identified and attributed where applicable.

---

# 21. Future Work

Potential future extensions include:

* richer evaluation datasets
* structured execution traces
* Git-aware code review
* sandboxed command execution
* TypeScript tool implementations
* model comparison
* local LLM support
* project-specific skill libraries
* prompt regression testing
* human approval for high-impact operations

These are deliberately secondary to completing and validating the core agent workflows.

```

### One thing I would tell Codex explicitly

After putting that README in the repository, give Codex an instruction along these lines:

> **Treat README.md as the current project specification. Build incrementally according to the phases defined there. We are currently implementing Phase 0 only. Do not prematurely add MCP, LangGraph, RAG, multi-agent orchestration, a frontend, or other architecture not specified for the current phase. Preserve attribution to the tutorial. Once Phase 0 is working, we will refactor the tutorial implementation into DevFlow rather than rewriting everything at once.**

This is important because otherwise coding agents have a tendency to see the final architecture and start "helpfully" building half the roadmap at once.

And I specifically like keeping the **tutorial calculator/example under `examples/tutorial-calculator/`** later rather than deleting it. It gives you a very clean Git history/story:

**tutorial skeleton → working agent loop → refactoring → original DevFlow skills → real-world workflows.**

That progression is actually useful to show in an interview because you can explain exactly where the learning material ended and where your engineering work began.
```
