"""Provider-agnostic dispatch for answer generation (Groq or local Ollama)."""

from collections.abc import Iterator

try:
    from src.llm.groq_client import call_groq, call_groq_stream
    from src.llm.ollama_client import call_ollama, call_ollama_stream
except ImportError:
    from llm.groq_client import call_groq, call_groq_stream
    from llm.ollama_client import call_ollama, call_ollama_stream


def generate_answer(
    prompt: str,
    provider: str,
    ollama_host: str,
    ollama_model: str,
    groq_api_key: str,
    groq_model: str,
    groq_temperature: float = 0.2,
) -> str:
    """Generate an answer using the configured LLM provider."""
    if provider == "groq":
        return call_groq(prompt=prompt, model=groq_model, api_key=groq_api_key, temperature=groq_temperature)

    if provider == "ollama":
        return call_ollama(prompt=prompt, model=ollama_model, host=ollama_host)

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r}. Use 'groq' or 'ollama'.")


def generate_answer_stream(
    prompt: str,
    provider: str,
    ollama_host: str,
    ollama_model: str,
    groq_api_key: str,
    groq_model: str,
    groq_temperature: float = 0.2,
) -> Iterator[str]:
    """Generate an answer incrementally using the configured LLM provider."""
    if provider == "groq":
        yield from call_groq_stream(
            prompt=prompt, model=groq_model, api_key=groq_api_key, temperature=groq_temperature
        )
        return

    if provider == "ollama":
        yield from call_ollama_stream(prompt=prompt, model=ollama_model, host=ollama_host)
        return

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r}. Use 'groq' or 'ollama'.")
