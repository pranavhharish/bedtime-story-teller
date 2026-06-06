"""
Rewriter prompt — takes the original story + judge critique and 
surgically improves only the weak dimensions.
The key insight: fix only what's broken, keep what's working.
"""

REWRITER_SYSTEM_PROMPT = """
You are a master editor of children's literature specializing in 
stories rooted in Indian mythology and wisdom traditions.

You have received a bedtime story and a detailed critique from a 
children's literature judge. Your job is to rewrite the story 
addressing ONLY the identified weaknesses.

Critical rules:
- Keep everything that scored 4.0 or above — do not touch it
- Fix only the dimensions listed in the critique
- Do not make the story longer than the original
- Do not change the core plot or the mythology archetype
- Do not add new characters unless the critique specifically asks for it
- The moral must still feel discovered, never announced
- The ending must remain warm and safe

You are a surgical editor, not a rewriter from scratch.
"""

REWRITER_USER_PROMPT = """
Here is the original bedtime story:

---ORIGINAL STORY---
{story_text}
---END ORIGINAL---

The judge evaluated this story and found these specific problems 
that need to be fixed:

{weak_dimensions_formatted}

The judge's priority fixes are:
{priority_fixes_formatted}

Dimensions that are WORKING WELL (do NOT change these):
{strong_dimensions_formatted}

Please rewrite the story fixing ONLY the weak dimensions listed above.
Preserve everything that is working.
Do not exceed the original length.

Return only the rewritten story. No explanation, no commentary.
"""

REWRITER_USER_PROMPT_WITH_USER_NOTE = """
Here is the bedtime story:

---STORY---
{story_text}
---END STORY---

The child or parent has requested this specific change:
"{user_revision_note}"

Please revise the story to incorporate this request while:
- Keeping the mythology archetype and moral theme intact
- Maintaining the 6-beat story arc
- Keeping it appropriate for ages {age_hint}
- Not making it significantly longer

Return only the revised story. No explanation.
"""


def format_weak_dimensions(weak_dims: dict, scores: dict) -> str:
    """
    Formats weak dimensions into a clear critique block for the rewriter.
    
    Args:
        weak_dims: {dimension_name: critique_text} for scores < 4.0
        scores: {dimension_name: score} for all dimensions
    
    Returns:
        Formatted string listing each weak dimension with its score and critique
    """
    if not weak_dims:
        return "None — all dimensions passed."
    
    lines = []
    for dim, critique in weak_dims.items():
        score = scores.get(dim, "?")
        lines.append(f"- {dim} (score: {score}/5): {critique}")
    
    return "\n".join(lines)


def format_strong_dimensions(all_scores: dict, threshold: float = 4.0) -> str:
    """
    Formats strong dimensions so rewriter knows what NOT to touch.
    
    Args:
        all_scores: {dimension_name: score} for all dimensions
        threshold: minimum score to be considered strong
    
    Returns:
        Formatted string listing strong dimensions
    """
    strong = [
        f"- {dim} (score: {score}/5)"
        for dim, score in all_scores.items()
        if score >= threshold
    ]
    
    if not strong:
        return "None scored above threshold — full rewrite acceptable."
    
    return "\n".join(strong)


def format_priority_fixes(priority_fixes: list) -> str:
    """
    Formats the judge's priority fixes as a numbered list.
    
    Args:
        priority_fixes: list of actionable fix strings from judge
    
    Returns:
        Numbered list string
    """
    if not priority_fixes:
        return "No specific priority fixes given."
    
    return "\n".join(
        f"{i+1}. {fix}" 
        for i, fix in enumerate(priority_fixes)
    )
