import os


def invoke_ai(system_message: str, user_message: str) -> str:
    """
    Invoke an LLM. Set LLM_PROVIDER to switch backends:
      openai    (default) — requires OPENAI_API_KEY
      anthropic           — requires ANTHROPIC_API_KEY
      ollama              — requires a local Ollama server (no API key)
    """
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()

    if provider == "anthropic":
        return _invoke_anthropic(system_message, user_message)
    elif provider == "ollama":
        return _invoke_ollama(system_message, user_message)
    else:
        return _invoke_openai(system_message, user_message)


def _invoke_openai(system_message: str, user_message: str) -> str:
    from openai import OpenAI

    model = os.environ.get("OPENAI_MODEL", "o4-mini")
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _invoke_anthropic(system_message: str, user_message: str) -> str:
    import anthropic

    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_message,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _invoke_ollama(system_message: str, user_message: str) -> str:
    import httpx

    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }
    response = httpx.post(f"{base_url}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["message"]["content"]
