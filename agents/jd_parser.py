import json
import re

from pydantic import ValidationError

from agents.base import load_prompt
from core.llm import call_llm
from core.schemas import JDParseResult


TECHNICAL_ROLE_TERMS = {
    "analyst",
    "analytics",
    "data",
    "engineer",
    "developer",
    "machine learning",
    "ml",
    "software",
    "scientist",
}
TECHNICAL_SKILL_TERMS = {
    "sql",
    "python",
    "r",
    "tableau",
    "power bi",
    "dashboard",
    "a/b testing",
    "statistics",
    "analytics",
    "data analysis",
    "model",
    "api",
}
def _fallback_result() -> JDParseResult:
    return JDParseResult(
        possible_roles=[],
        inferred_focus_area="mixed",
        key_skills=[],
        confidence="low",
        summary="Could not parse job description reliably.",
    )


def _extract_json(text: str) -> dict[str, object]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_focus_area(result: JDParseResult) -> JDParseResult:
    if result.inferred_focus_area != "mixed":
        return result

    role_text = " ".join(result.possible_roles).lower()
    skills_text = " ".join(result.key_skills).lower()
    technical_role_match = any(term in role_text for term in TECHNICAL_ROLE_TERMS)
    technical_skill_matches = sum(1 for term in TECHNICAL_SKILL_TERMS if term in skills_text)

    if technical_role_match and technical_skill_matches >= 2:
        result.inferred_focus_area = "technical"
    return result


def _prefer_explicit_roles(roles: list[str], jd_text: str) -> list[str]:
    normalized_jd = re.sub(r"\s+", " ", jd_text.lower())
    explicit_roles = []

    for role in roles:
        normalized_role = re.sub(r"\s+", " ", role.lower()).strip()
        if re.search(rf"\b{re.escape(normalized_role)}\b", normalized_jd):
            explicit_roles.append(role)

    return explicit_roles or roles


class JDParserAgent:
    def __init__(self) -> None:
        self.system_prompt = load_prompt("jd_parser.md")

    def parse(self, jd_text: str) -> JDParseResult:
        user_prompt = json.dumps(
            {
                "job_description": jd_text,
                "required_schema": JDParseResult.model_json_schema(),
            },
            indent=2,
        )
        try:
            raw = call_llm(self.system_prompt, user_prompt, temperature=0.1)
            result = JDParseResult.model_validate(_extract_json(raw))
        except (RuntimeError, json.JSONDecodeError, ValidationError):
            return _fallback_result()

        result.possible_roles = _prefer_explicit_roles(result.possible_roles, jd_text)[:5]
        result.key_skills = result.key_skills[:10]
        return _normalize_focus_area(result)
