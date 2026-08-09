from __future__ import annotations

from dataclasses import dataclass

from devflow.gemini import GeminiSession
from devflow.tools.registry import ToolRegistry


@dataclass(frozen=True)
class AgentRunResult:
    success: bool
    output: str = ""
    error: str | None = None
    iterations: int = 0


class AgentRuntime:
    def __init__(
        self,
        session: GeminiSession,
        registry: ToolRegistry,
        max_iterations: int = 20,
        verbose: bool = False,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1.")
        self._session = session
        self._registry = registry
        self._max_iterations = max_iterations
        self._verbose = verbose

    def run(self, prompt: str) -> AgentRunResult:
        self._session.add_user_prompt(prompt)

        for iteration in range(1, self._max_iterations + 1):
            try:
                turn = self._session.generate()
            except Exception as exc:
                return AgentRunResult(
                    success=False,
                    error=f"Model request failed: {exc}",
                    iterations=iteration,
                )

            if turn.tool_calls:
                for call in turn.tool_calls:
                    if self._verbose:
                        print(f"Tool call: {call.name} {call.arguments}")
                    result = self._registry.execute(call.name, call.arguments)
                    if self._verbose:
                        status = "ok" if result.success else "error"
                        print(f"Tool result ({status}): {result.output or result.error}")
                    try:
                        self._session.add_tool_result(call, result)
                    except Exception as exc:
                        return AgentRunResult(
                            success=False,
                            error=f"Could not return tool result to the model: {exc}",
                            iterations=iteration,
                        )
                continue

            if turn.text:
                return AgentRunResult(
                    success=True,
                    output=turn.text,
                    iterations=iteration,
                )

            return AgentRunResult(
                success=False,
                error="Model returned neither text nor a tool call.",
                iterations=iteration,
            )

        return AgentRunResult(
            success=False,
            error=(
                "Agent stopped after reaching the maximum iteration limit "
                f"({self._max_iterations})."
            ),
            iterations=self._max_iterations,
        )
