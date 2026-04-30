from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_prompt(name: str) -> str:
    return (PROJECT_ROOT / "prompts" / name).read_text(encoding="utf-8")
