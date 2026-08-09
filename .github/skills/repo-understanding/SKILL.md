---
name: repo-understanding
description: Build a grounded mental model of an unfamiliar or forgotten software repository by inspecting structure, dependencies, entry points, relationships, and execution or data flow. Use for repository overviews, architecture explanations, onboarding, codebase rediscovery, component mapping, or execution-path tracing.
---

# Repository Understanding

Build the smallest evidence-backed repository model that satisfies the user's request.

## Establish scope

- Infer the requested depth from the user's wording: quick orientation, component overview, or detailed execution/data-flow trace.
- Ask for clarification only when ambiguity would materially change the investigation.
- Remain read-only unless the user explicitly requests a modification.

## Inspect strategically

1. Inspect the top-level structure before opening implementation files.
2. Identify manifests, dependency files, build files, configuration, documentation, and test layout.
3. Determine the languages, frameworks, and major runtime or build systems from repository evidence.
4. Identify likely entry points from scripts, manifests, framework conventions, and executable modules.
5. Select only the modules relevant to the requested depth. Do not read the repository indiscriminately.

## Trace relationships and flow

- Use search to follow imports, symbol references, registrations, configuration keys, routes, commands, and call sites.
- Trace outward from entry points through the important orchestration and domain boundaries.
- For data flow, identify where data enters, how it is validated or transformed, where state or external systems are involved, and how results leave the system.
- Inspect tests when they clarify intended behavior, important boundaries, or component relationships.
- Stop expanding the trace when additional files no longer change the answer requested by the user.

## Maintain evidence discipline

- Treat file contents, manifests, configuration, tests, and command output as observed evidence.
- Clearly label architectural conclusions that are inferred rather than directly established.
- Do not invent missing runtime behavior, deployment details, or relationships.
- Report uncertainty and identify the evidence needed to resolve it.
- Resolve conflicting clues by inspecting the closest authoritative source rather than choosing one silently.

## Report the repository model

Tailor the detail to the request and include:

- repository purpose and technology stack
- important entry points and configuration
- major components and their responsibilities
- significant dependencies and component relationships
- relevant execution or data flow
- tests, operational commands, or documentation that help continued work
- useful continuation points for the user's likely next task
- remaining uncertainty, separated from confirmed facts
