import os
from groq import Groq
import google.generativeai as genai
from typing import Generator

# All available free models
MODELS = {
    "groq_llama33":  {"provider": "groq",   "model": "llama-3.3-70b-versatile"},
    "groq_llama31":  {"provider": "groq",   "model": "llama-3.1-8b-instant"},
    "groq_mixtral":  {"provider": "groq",   "model": "llama-3.3-70b-versatile"},  # mixtral decommissioned, fallback to llama33
    "groq_gemma":    {"provider": "groq",   "model": "llama-3.1-8b-instant"},     # gemma decommissioned, fallback to llama31
    "gemini_flash":  {"provider": "gemini", "model": "gemini-1.5-flash"},
    "gemini_flash2": {"provider": "gemini", "model": "gemini-2.0-flash"},
}


def get_active_model() -> dict:
    active = os.getenv("ACTIVE_LLM", "groq_llama")
    return MODELS.get(active, MODELS["groq_llama33"])


def call_llm(prompt: str, system_prompt: str = "") -> str:
    """
    Call the active LLM and return a complete response string.
    Automatically falls back to Gemini if Groq rate-limits.
    """
    model_config = get_active_model()
    
    try:
        if model_config["provider"] == "groq":
            return _call_groq(prompt, system_prompt, model_config["model"])
        else:
            return _call_gemini(prompt, system_prompt, model_config["model"])
    except Exception as e:
        error_str = str(e).lower()
        if "rate" in error_str or "limit" in error_str:
            print(f"Rate limit hit on {model_config['model']}, falling back to Gemini...")
            return _call_gemini(prompt, system_prompt, "gemini-1.5-flash")
        raise e


def stream_llm(prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
    """
    Stream the LLM response token by token.
    Used for the chat endpoint to show typing effect in UI.
    """
    model_config = get_active_model()

    try:
        if model_config["provider"] == "groq":
            yield from _stream_groq(prompt, system_prompt, model_config["model"])
        else:
            yield from _stream_gemini(prompt, system_prompt, model_config["model"])
    except Exception as e:
        error_str = str(e).lower()
        if "rate" in error_str or "limit" in error_str:
            print("Rate limit hit, falling back to Gemini stream...")
            yield from _stream_gemini(prompt, system_prompt, "gemini-1.5-flash")
        else:
            raise e


# ---- Groq implementations ----

def _call_groq(prompt: str, system_prompt: str, model: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        temperature=0.1  # Low temp = more factual, less hallucination
    )
    return response.choices[0].message.content


def _stream_groq(prompt: str, system_prompt: str, model: str) -> Generator[str, None, None]:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        temperature=0.1,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ---- Gemini implementations ----

def _call_gemini(prompt: str, system_prompt: str, model: str) -> str:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    m = genai.GenerativeModel(model)
    response = m.generate_content(full_prompt)
    return response.text


def _stream_gemini(prompt: str, system_prompt: str, model: str) -> Generator[str, None, None]:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    m = genai.GenerativeModel(model)
    for chunk in m.generate_content(full_prompt, stream=True):
        if chunk.text:
            yield chunk.text