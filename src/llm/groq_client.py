"""Helpers for calling the Groq hosted LLM API."""

from collections.abc import Iterator


def call_groq(prompt: str, model: str, api_key: str, temperature: float = 0.2) -> str:
    """Send a prompt to Groq's chat completions API and return the generated answer text."""
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file. "
            "Get a free key at https://console.groq.com/keys"
        )

    try:
        from groq import Groq
    except ImportError as exc:
        raise ImportError("groq is not installed. Run: pip install -r requirements.txt") from exc

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc

    answer = (response.choices[0].message.content or "").strip()

    if not answer:
        raise RuntimeError("Groq returned an empty response.")

    return answer


def call_groq_stream(prompt: str, model: str, api_key: str, temperature: float = 0.2) -> Iterator[str]:
    """Send a prompt to Groq and yield the generated answer text incrementally."""
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file. "
            "Get a free key at https://console.groq.com/keys"
        )

    try:
        from groq import Groq
    except ImportError as exc:
        raise ImportError("groq is not installed. Run: pip install -r requirements.txt") from exc

    client = Groq(api_key=api_key)

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as exc:
        raise RuntimeError(f"Groq streaming request failed: {exc}") from exc
