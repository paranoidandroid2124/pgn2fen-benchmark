import os

import backoff
import openai
from google import genai
from google.genai import types
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from pgn2fen.models import Provider

# ruff: noqa: E501
PROMPT_TEMPLATE = """
## Task
Your task is to convert the provided PGN representation of a chess game into a FEN string.

## Instructions
1. Read the provided PGN text carefully.
2. Convert the PGN text into a FEN string.
3. Do not include any additional text, explanations, or backticks in your response. ONLY return the FEN string.
4. Do not use code to convert the PGN to FEN. Use your own knowledge and understanding of chess to perform the conversion.

For example, if the PGN text represented the starting position of a chess game, you would return the following and nothing else:
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

## Input
{pgn_text}
""".strip()


def get_gemini_fen(
    pgn_text: str, model: str = "gemini-2.0-flash-001", thinking_budget: int | None = None
) -> str:
    """
    FEN retrieval for the Google Gemini API client.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(pgn_text=pgn_text)

    thinking_config = None
    if thinking_budget is not None and "2.5" in model:
        thinking_config = types.ThinkingConfig(thinking_budget=thinking_budget)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=1.0,
                thinking_config=thinking_config,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Error during API call: {e}") from e
    return str(response.text).strip()


OPENAI_FLEX_MODELS: list[str] = [
    "o3",
    "o3-2025-04-16",
    "o4-mini",
    "o4-mini-2025-04-16",
]


@backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=6)
def get_openai_fen(
    pgn_text: str,
    model: str = "gpt-4.1-mini-2025-04-14",
    api_key: str | None = None,
    base_url: str = "https://api.openai.com/v1",
) -> str:
    """
    FEN retrieval for the OpenAI API client. Also supports DeepSeek API.
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=900.0)

    prompt = PROMPT_TEMPLATE.format(pgn_text=pgn_text)

    try:
        service_tier = None
        if model in OPENAI_FLEX_MODELS:
            service_tier = "flex"
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            service_tier=service_tier,
        )
    except Exception as e:
        raise RuntimeError(f"Error during API call: {e}") from e
    return str(response.choices[0].message.content)

def get_huggingface_fen(pgn_text: str,
                        model_name: str = 'Qwen/Qwen3-4B) -> str:
    generator = pipeline('text-generation', model=model_Name, device=-1)
    prompt = PROMPT_TEMPLATE.format(pgn_text=pgn_text)
    raw_response = generator(prompt, max_new_tokens=1000, num_return_sequences=1)
    response = raw_response[0]['generated_text']
            
    return str(response.text).strip()

def get_fen(
    pgn_text: str,
    provider: Provider = Provider.GOOGLE,
    model: str = "gemini-2.0-flash-001",
    thinking_budget: int | None = None,
) -> str:
    """
    Get the FEN string from the PGN text using the specified provider and model.

    Args:
        pgn_text (str): The PGN text to convert.
        provider (Provider): The LLM provider to use.
        model (str): The model to use for the provider.
        thinking_budget (int | None): The maximum number of tokens for the LLM to think.
            Currently only implemented for the GOOGLE provider.

    Returns:
        str: The FEN string.

    Raises:
        ValueError: If the provider is not supported.
    """
    if provider == Provider.GOOGLE:
        return str(get_gemini_fen(pgn_text, model=model, thinking_budget=thinking_budget))
    elif provider == Provider.OPENAI:
        return str(get_openai_fen(pgn_text, model=model))
    elif provider == Provider.DEEPSEEK:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        return str(
            get_openai_fen(
                pgn_text, model=model, api_key=api_key, base_url="https://api.deepseek.com/v1"
            )
        )
    elif provider == Provider.HUGGINGFACE:
        return get_huggingface_fen(
            pgn_text, model_name
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
