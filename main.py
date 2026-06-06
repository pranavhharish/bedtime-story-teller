"""
Main pipeline orchestrator — pure logic, zero UI.
app.py calls this. This file knows nothing about Streamlit.

The pipeline:
  StoryRequest → Categorize → Generate → Judge → (Rewrite → Judge) × N → StoryOutput
"""

from openai import OpenAI
from models.story_types import (
    StoryRequest, StoryOutput, StoryIteration, MythologyMapping
)
from categorizer import map_to_archetype
from generator import generate_story, _resolve_age
from judge import evaluate_story
from rewriter import rewrite_story

MAX_ITERATIONS = 3


def run_pipeline(
    client: OpenAI,
    request: StoryRequest,
    on_status=None   # Optional callback for Streamlit live status updates
) -> StoryOutput:
    """
    Runs the full story generation pipeline.
    
    Args:
        client: OpenAI client instance
        request: Parsed user story request
        on_status: Optional callback(message: str) for live UI updates
                   Streamlit's st.write() can be passed here
    
    Returns:
        StoryOutput with best story, score, and full iteration history
    """

    def status(msg: str):
        """Emit a status update if a callback was provided."""
        if on_status:
            on_status(msg)

    # ── Step 1: Categorize ─────────────────────────────────────────────
    status("📚 Finding your mythology archetype...")
    mapping: MythologyMapping = map_to_archetype(client, request)
    status(f"✨ Found: **{mapping.archetype}** from *{mapping.source_text}*")

    # ── Step 2: Generate → Judge loop ──────────────────────────────────
    age_hint     = _resolve_age(request.age_hint)
    best_story   = None
    best_score   = 0.0
    best_judge   = None
    history      = []

    for iteration in range(1, MAX_ITERATIONS + 1):

        # Generate or rewrite
        if iteration == 1:
            status(f"⏳ Crafting your story...")
            story = generate_story(client, request, mapping)
        else:
            status(f"✍️ Refining story (attempt {iteration}/{MAX_ITERATIONS})...")
            story = rewrite_story(client, story, judge_result)

        # Judge
        status(f"📖 Judge reviewing (attempt {iteration}/{MAX_ITERATIONS})...")
        judge_result = evaluate_story(client, story, mapping, age_hint)

        # Track best
        if judge_result.overall > best_score:
            best_score = judge_result.overall
            best_story = story
            best_judge = judge_result

        # Record history
        history.append(StoryIteration(
            iteration_number=iteration,
            story_text=story,
            judge_result=judge_result
        ))

        # Stop if passed
        if judge_result.passed:
            status(f"✅ Story passed! (score: {judge_result.overall:.1f}/5.0)")
            break
        else:
            if iteration < MAX_ITERATIONS:
                status(
                    f"Score: {judge_result.overall:.1f}/5.0 — "
                    f"refining these areas: "
                    f"{', '.join(judge_result.weak_dimensions().keys())}"
                )
            else:
                status(
                    f"✅ Best version ready (score: {best_score:.1f}/5.0)"
                )

    return StoryOutput(
        best_story=best_story,
        best_score=best_score,
        total_iterations=len(history),
        mythology_mapping=mapping,
        final_judge=best_judge,
        iteration_history=history
    )
