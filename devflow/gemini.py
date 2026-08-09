from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types

from devflow.tools.registry import ToolDefinition, ToolResult


@dataclass(frozen=True)
class GeminiToolCall:
    name: str
    arguments: dict[str, Any]
    call_id: str | None = None


@dataclass(frozen=True)
class GeminiTurn:
    text: str
    tool_calls: tuple[GeminiToolCall, ...]


class GeminiSession:
    """Concrete Gemini conversation state for the Phase 1A runtime."""

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        tools: tuple[ToolDefinition, ...],
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._messages: list[types.Content] = []

        declarations = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters_json_schema=tool.parameters,
            )
            for tool in tools
        ]
        self._config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=declarations)],
            system_instruction=system_prompt,
        )

    def add_user_prompt(self, prompt: str) -> None:
        self._messages.append(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )

    def generate(self) -> GeminiTurn:
        response = self._client.models.generate_content(
            model=self._model,
            contents=self._messages,
            config=self._config,
        )
        if not response.candidates or response.candidates[0].content is None:
            raise RuntimeError("Gemini returned no response candidate.")

        self._messages.append(response.candidates[0].content)
        calls = tuple(
            GeminiToolCall(
                name=call.name or "",
                arguments=dict(call.args or {}),
                call_id=call.id,
            )
            for call in (response.function_calls or [])
        )
        text = "" if calls else (response.text or "")
        return GeminiTurn(text=text, tool_calls=calls)

    def add_tool_result(self, call: GeminiToolCall, result: ToolResult) -> None:
        function_response = types.FunctionResponse(
            id=call.call_id,
            name=call.name,
            response=result.as_function_response(),
        )
        self._messages.append(
            types.Content(
                role="user",
                parts=[types.Part(function_response=function_response)],
            )
        )
