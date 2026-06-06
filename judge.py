"""
Judge — evaluates the story on 6 dimensions and returns a structured JudgeResult.
The judge's critique is what makes the rewriter surgical rather than random.
"""

import json
from openai import OpenAI
from models.story_types import JudgeResult, JudgeScore, MythologyMapping
from prompts.judge_prompt import JUDGE_SYSTEM_PROMPT, JUDGE_USER_PROMPT


PASS_THRESHOLD = 4.0


def evaluate_story(
    client: OpenAI,
    story_text: str,
    mapping: MythologyMapping,
    age_hint: str = "5-10"
) -> JudgeResult:
    """
    Evaluates a story on 6 dimensions and returns a structured JudgeResult.
    
    Args:
        client: OpenAI client instance
        story_text: The story to evaluate
        mapping: The mythology mapping (for context on what was intended)
        age_hint: Age group string for the evaluation
    
    Returns:
        JudgeResult with scores, critiques, pass/fail, and priority fixes
    """
    user_prompt = JUDGE_USER_PROMPT.format(
        story_text=story_text,
        age_hint=age_hint,
        archetype=mapping.archetype,
        source_text=mapping.source_text,
        moral_theme=mapping.moral_theme
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.2,   # Very low temp — we want consistent, reliable evaluation
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences defensively
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)

    # Parse each dimension into a JudgeScore
    def parse_dim(key: str) -> JudgeScore:
        return JudgeScore(
            score=float(data[key]["score"]),
            critique=data[key]["critique"]
        )

    age_appropriateness = parse_dim("age_appropriateness")
    story_arc           = parse_dim("story_arc")
    emotional_warmth    = parse_dim("emotional_warmth")
    pacing              = parse_dim("pacing")
    engagement          = parse_dim("engagement")
    mythology_integrity = parse_dim("mythology_integrity")

    # Recalculate overall ourselves to ensure accuracy
    scores = [
        age_appropriateness.score,
        story_arc.score,
        emotional_warmth.score,
        pacing.score,
        engagement.score,
        mythology_integrity.score
    ]
    overall = round(sum(scores) / len(scores), 2)

    return JudgeResult(
        age_appropriateness=age_appropriateness,
        story_arc=story_arc,
        emotional_warmth=emotional_warmth,
        pacing=pacing,
        engagement=engagement,
        mythology_integrity=mythology_integrity,
        overall=overall,
        passed=overall >= PASS_THRESHOLD,
        priority_fixes=data.get("priority_fixes", [])
    )
