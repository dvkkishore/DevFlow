# Phase 4 Live Demonstration and Lightweight Evaluation

Date: 2026-08-09  
Model: `gemini-3.5-flash-lite`

This evaluation uses DevFlow's real Gemini integration, production Agent Skills, and workspace tools. It is a small observed-results record, not an automated LLM evaluation framework.

## Live commands

### Repository understanding

```powershell
python .\main.py --workspace . --skills-dir .\.github\skills --verbose "I am returning to this repository after time away. Give me a focused, evidence-grounded explanation of its purpose, architecture, main entry points, core execution flow, and the most useful continuation points. Keep the investigation to at most eight tool calls and do not modify files."
```

Relevant trace:

```text
Tool call: load_skill {'name': 'repo-understanding'}
Tool result (ok): ... # Repository Understanding ...
Tool call: list_files {'recursive': False}
Tool call: read_file {'file_path': 'pyproject.toml'}
Tool call: list_files {'recursive': True, 'directory': 'devflow'}
Tool call: read_file {'file_path': 'main.py'}
Tool call: read_file {'file_path': 'devflow/cli.py'}
Tool call: read_file {'file_path': 'devflow/agent/runtime.py'}
```

Observed result: the agent selected and progressively loaded `repo-understanding`, remained read-only, and produced a grounded summary of DevFlow's purpose, entry points, core modules, agent/tool loop, tests, and continuation points. Automated progressive-disclosure tests separately confirmed that the initial system context contained the two production skill names and descriptions but not their bodies.

### Debug and fix

```powershell
python .\main.py --workspace .\examples\buggy-demo --skills-dir .\.github\skills --verbose "The tests in this project are failing. Diagnose the root cause from evidence, make the smallest reasonable repair, and verify the fix. Preserve unrelated behavior and report the exact verification result. Keep the investigation focused."
```

Relevant trace:

```text
Tool call: list_files {'recursive': False}
Tool call: load_skill {'name': 'debug-and-fix'}
Tool result (ok): ... # Debug and Fix ...
Tool call: run_command {'command': ['python', '-m', 'unittest', '-v']}
Tool result (error): ... AssertionError: 525.0 != 30.0 ...
Tool call: read_file {'file_path': 'config.py'}
Tool call: read_file {'file_path': 'pricing.py'}
Tool call: read_file {'file_path': 'order_service.py'}
Tool call: write_file {'file_path': 'order_service.py', ...}
Tool call: run_command {'command': ['python', '-m', 'unittest', '-v']}
Tool result (ok): ... Ran 2 tests ... OK
```

Observed root cause: `DEFAULT_TAX_PERCENT` stores `20` as a percentage while `apply_tax` accepts a decimal rate such as `0.20`.

Observed minimal repair:

```python
return apply_tax(subtotal, DEFAULT_TAX_PERCENT / 100)
```

Before repair:

```text
Ran 2 tests
FAILED (failures=1)
AssertionError: 525.0 != 30.0
```

After repair:

```text
Ran 2 tests
OK
```

The repository is restored to the clean failing state after the demonstration with:

```powershell
python .\examples\reset_buggy_demo.py
```

### Additional evaluation commands

Simple request where no specialized skill was needed:

```powershell
python .\main.py --workspace .\examples\buggy-demo --skills-dir .\.github\skills --verbose "List the top-level files in this workspace with a one-line label for each. Do not analyze the architecture or modify anything."
```

Failure that could not be fully verified from the available repository evidence:

```powershell
python .\main.py --workspace .\examples\buggy-demo --skills-dir .\.github\skills --verbose "A user reports that order totals are occasionally wrong only in production for region-specific currency rounding, but this repository contains no production logs, deployment configuration, or external currency-service fixture. Investigate what can be established safely, do not modify files, and state clearly whether the reported failure can be reproduced or fully verified."
```

## Evaluation scenarios

Some rows intentionally reuse a live run when one request covers two related evaluation dimensions.

| Scenario | Live run | Expected skill | Actual skill used | Task completion | Verification behavior |
|---|---|---|---|---|---|
| Repository overview | Repository understanding | `repo-understanding` | `repo-understanding` | Complete | Read-only findings grounded in inspected project files. |
| Execution/data-flow tracing | Repository understanding | `repo-understanding` | `repo-understanding` | Complete | Traced CLI initialization into Gemini session, runtime loop, registry, and tools; no unsupported runtime execution claims. |
| Runtime debugging | Debug and fix | `debug-and-fix` | `debug-and-fix` | Complete | Collected command failures and the actual unittest traceback before editing. |
| Failing-test debugging | Debug and fix | `debug-and-fix` | `debug-and-fix` | Complete | Reproduced first, changed one relevant file, reran the same test command, and reported success only after exit code 0. |
| Simple top-level file listing | Separate short live run | None | None | Complete | Used only `list_files`; no specialized skill was loaded and no verification was required. |
| Production-only regional rounding report without logs/fixtures | Separate short live run | `debug-and-fix` | None | Appropriate partial result | Ran available tests successfully, searched for currency/region evidence, made no changes, and explicitly stated that the reported production failure could not be reproduced or fully verified. |

## Observations from live execution

- The initial repository-understanding run exposed a Windows console encoding failure when verbose output printed Unicode from `readme.md`. The CLI now configures stdout/stderr as UTF-8, with a regression test.
- The first debug run skipped the applicable skill. A generic skill-loading instruction and declaration-order correction were applied without hardcoding production skill names. The decisive rerun loaded `debug-and-fix` and followed its workflow.
- The intentionally unverifiable scenario still skipped `debug-and-fix`. Its evidence gathering and uncertainty reporting were correct, but this remains a skill-selection miss to monitor rather than conceal.
- Gemini free-tier request-per-minute limits required cooldowns between multi-tool live runs; rate limiting was external to task behavior.

## Automated validation

```powershell
python -m unittest discover -s tests -v
```

Result: all 21 DevFlow tests passed. The demo repository was then reset and its intentional baseline was reconfirmed: two tests ran, the empty-order test passed, and the configured-tax test failed with `525.0 != 30.0`.
