"""
Rewriter — takes story + judge critique and surgically fixes only the weak parts.
Also handles user-requested revisions after the story is shown.
"""

from openai import OpenAI
from models.story_types import JudgeResult, StoryRequest
from prompts.rewriter_prompt import (
    REWRITER_SYSTEM_PROMPT,
    REWRITER_USER_PROMPT,
    REWRITER_USER_PROMPT_WITH_USER_NOTE,
    format_weak_dimensions,
    format_strong_dimensions,
    format_priority_fixes
)


def rewrite_story(
    client: OpenAI,
    story_text: str,
    judge_result: JudgeResult
) -> str:
    """
    Rewrites the story based on judge critique — fixes only weak dimensions.
    
    Args:
        client: OpenAI client instance
        story_text: The story that needs improvement
        judge_result: The judge's full evaluation
    
    Returns:
        The improved story as a plain string
    """
    all_scores     = judge_result.scores_dict()
    weak_dims      = judge_result.weak_dimensions()

    user_prompt = REWRITER_USER_PROMPT.format(
        story_text=story_text,
        weak_dimensions_formatted=format_weak_dimensions(weak_dims, all_scores),
        priority_fixes_formatted=format_priority_fixes(judge_result.priority_fixes),
        strong_dimensions_formatted=format_strong_dimensions(all_scores)
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.75,  # Moderate — creative but focused
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()


def revise_with_user_note(
    client: OpenAI,
    story_text: str,
    user_note: str,
    request: StoryRequest
) -> str:
    """
    Revises the story based on a specific user request after story display.
    e.g. "make it funnier", "the elephant should be purple", 
         "add a scene where she meets a friend"
    
    Args:
        client: OpenAI client instance
        story_text: The current story
        user_note: The user's revision request
        request: Original story request (for age context)
    
    Returns:
        The revised story as a plain string
    """
    age_hint = request.age_hint or "5-10"

    user_prompt = REWRITER_USER_PROMPT_WITH_USER_NOTE.format(
        story_text=story_text,
        user_revision_note=user_note,
        age_hint=age_hint
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": REWRITER_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.8,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()
