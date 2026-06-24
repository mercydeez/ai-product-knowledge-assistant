"""Helpers for calling a local Ollama model over HTTP."""

import json
from collections.abc import Iterator
from urllib import error, request


def call_ollama(prompt: str, model: str, host: str) -> str:
    """Send a prompt to Ollama and return the generated answer text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    request_body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url=f"{host}/api/generate",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=120) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"Ollama request failed with status {exc.code}: {error_body}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure the Ollama app or server is running."
        ) from exc

    answer = response_data.get("response", "").strip()

    if not answer:
        raise RuntimeError("Ollama returned an empty response.")

    return answer


def call_ollama_stream(prompt: str, model: str, host: str) -> Iterator[str]:
    """Send a prompt to Ollama and yield the generated answer text incrementally."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
    }

    request_body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url=f"{host}/api/generate",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=120) as response:
            for line in response:
                line = line.strip()
                if not line:
                    continue

                chunk = json.loads(line.decode("utf-8"))
                delta = chunk.get("response", "")
                if delta:
                    yield delta

                if chunk.get("done"):
                    break
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"Ollama request failed with status {exc.code}: {error_body}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure the Ollama app or server is running."
        ) from exc
