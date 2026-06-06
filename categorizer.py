"""
Categorizer — maps raw user input to the right mythology archetype.
One small, fast LLM call that shapes the entire story downstream.
"""

import json
from openai import OpenAI
from models.story_types import StoryRequest, MythologyMapping
from prompts.categorizer_prompt import CATEGORIZER_SYSTEM_PROMPT, CATEGORIZER_USER_PROMPT


def map_to_archetype(client: OpenAI, request: StoryRequest) -> MythologyMapping:
    """
    Takes a StoryRequest and returns a MythologyMapping.
    Uses a focused LLM call to find the right archetype.
    
    Args:
        client: OpenAI client instance
        request: The parsed user story request
    
    Returns:
        MythologyMapping with archetype, source, moral, tone, etc.
    """
    user_prompt = CATEGORIZER_USER_PROMPT.format(
        raw_input=request.raw_input,
        character_name=request.character_name or "not specified — choose a fitting name",
        age_hint=request.age_hint or "5-10",
        extra_wishes=request.extra_wishes or "none"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": CATEGORIZER_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.4,   # Low temp — we want consistent, accurate mapping
        max_tokens=600
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if model adds them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)

    return MythologyMapping(
        archetype=data["archetype"],
        source_text=data["source_text"],
        moral_theme=data["moral_theme"],
        tone=data["tone"],
        inspired_by=data["inspired_by"],
        character_seeds=data["character_seeds"],
        wisdom_figure=data.get("wisdom_figure", "a wise old creature"),
        suggested_setting=data.get("suggested_setting", "a village near a great forest"),
    )
