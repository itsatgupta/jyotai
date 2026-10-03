"""OpenAI-compatible HTTP transport for the constrained composition boundary."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from astrologer.composition.models import (
    CompositionProviderRequest,
    CompositionProviderResponse,
)


class LanguageModelTransportError(RuntimeError):
    """Raised when an upstream language model cannot safely complete a request."""

    def __init__(
        self,
        category: str,
        *,
        provider_id: str | None = None,
        model_id: str | None = None,
        http_status_code: int | None = None,
    ) -> None:
        super().__init__("language model provider is unavailable")
        self.category = category
        self.provider_id = provider_id
        self.model_id = model_id
        self.http_status_code = http_status_code


class OpenAICompatibleTransport:
    """Minimal synchronous adapter; it receives only a safe provider request."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        provider_id: str,
        api_key: str | None,
        timeout_seconds: float,
    ) -> None:
        self._endpoint = f"{base_url.rstrip('/')}/chat/completions"
        self._model = model
        self._provider_id = provider_id
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def complete(self, request: CompositionProviderRequest) -> CompositionProviderResponse:
        """Request one JSON-only completion from an OpenAI-compatible endpoint."""
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        body = json.dumps(
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": request.system_instructions},
                    {"role": "user", "content": request.user_payload_json},
                ],
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")
        try:
            with urlopen(
                Request(self._endpoint, data=body, headers=headers, method="POST"),
                timeout=self._timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
            output_json = payload["choices"][0]["message"]["content"]
        except HTTPError as error:
            raise LanguageModelTransportError(
                "provider_http",
                provider_id=self._provider_id,
                model_id=self._model,
                http_status_code=error.code,
            ) from error
        except TimeoutError as error:
            raise LanguageModelTransportError(
                "timeout", provider_id=self._provider_id, model_id=self._model
            ) from error
        except (URLError, OSError) as error:
            raise LanguageModelTransportError(
                "network", provider_id=self._provider_id, model_id=self._model
            ) from error
        except json.JSONDecodeError as error:
            raise LanguageModelTransportError(
                "provider_response_parse", provider_id=self._provider_id, model_id=self._model
            ) from error
        except (KeyError, IndexError, TypeError) as error:
            raise LanguageModelTransportError(
                "provider_response_shape", provider_id=self._provider_id, model_id=self._model
            ) from error
        if not isinstance(output_json, str) or not output_json.strip():
            raise LanguageModelTransportError(
                "provider_response_shape", provider_id=self._provider_id, model_id=self._model
            )
        return CompositionProviderResponse(
            output_json=output_json,
            provider_id=self._provider_id,
            model_id=self._model,
        )
