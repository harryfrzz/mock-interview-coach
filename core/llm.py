import os
import warnings

from dotenv import load_dotenv


load_dotenv()

warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\..*")
warnings.filterwarnings("ignore", category=FutureWarning, message=r".*google\.generativeai.*")
warnings.filterwarnings("ignore", message=r".*urllib3 v2 only supports OpenSSL.*")


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    """Call Gemini and return plain text."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        import google.generativeai as genai

    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        f"{system_prompt}\n\nUser:\n{user_prompt}",
        generation_config={"temperature": temperature},
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text.strip()
