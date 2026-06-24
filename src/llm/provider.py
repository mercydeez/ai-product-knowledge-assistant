"""Provider-agnostic dispatch for answer generation (Groq or local Ollama)."""

try:
    from src.llm.groq_client import call_groq
    from src.llm.ollama_client import call_ollama
except ImportError:
    from llm.groq_client import call_groq
    from llm.ollama_client import call_ollama


def generate_answer(
    prompt: str,
    provider: str,
    ollama_host: str,
    ollama_model: str,
    groq_api_key: str,
    groq_model: str,
) -> str:
    """Generate an answer using the configured LLM provider."""
    if provider == "groq":
        return call_groq(prompt=prompt, model=groq_model, api_key=groq_api_key)

    if provider == "ollama":
        return call_ollama(prompt=prompt, model=ollama_model, host=ollama_host)

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r}. Use 'groq' or 'ollama'.")
