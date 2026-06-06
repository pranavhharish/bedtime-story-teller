"""
Generator — creates the bedtime story using mythology context,
archetype mapping, and the 6-beat arc template.
"""

from typing import Optional
from openai import OpenAI
from models.story_types import StoryRequest, MythologyMapping
from prompts.generator_prompt import GENERATOR_SYSTEM_PROMPT, GENERATOR_USER_PROMPT


def generate_story(
    client: OpenAI,
    request: StoryRequest,
    mapping: MythologyMapping
) -> str:
    """
    Generates a bedtime story from a request and mythology mapping.
    
    Args:
        client: OpenAI client instance
        request: The parsed user story request
        mapping: The mythology archetype mapping from categorizer
    
    Returns:
        The generated story as a plain string
    """
    # Resolve age hint to a cleaner string for the prompt
    age_display = _resolve_age(request.age_hint)

    # Pull wisdom figure and setting from mapping if available,
    # fall back to sensible defaults
    wisdom_figure = getattr(mapping, "wisdom_figure", "a wise old creature")
    suggested_setting = getattr(mapping, "suggested_setting", "a village near a great forest")

    user_prompt = GENERATOR_USER_PROMPT.format(
        raw_input=request.raw_input,
        age_hint=age_display,
        archetype=mapping.archetype,
        source_text=mapping.source_text,
        moral_theme=mapping.moral_theme,
        tone=mapping.tone,
        character_seeds=mapping.character_seeds,
        wisdom_figure=wisdom_figure,
        suggested_setting=suggested_setting,
        character_name=request.character_name or "a name fitting the archetype",
        extra_wishes=request.extra_wishes or "none"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.85,  # Higher temp — we want creative, warm stories
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()


def _resolve_age(age_hint: Optional[str]) -> str:
    """Maps UI age selection to a clean string for prompts."""
    if not age_hint:
        return "5-10"
    if "5" in age_hint or "little" in age_hint.lower():
        return "5-7"
    if "8" in age_hint or "growing" in age_hint.lower():
        return "8-10"
    return "5-10"
