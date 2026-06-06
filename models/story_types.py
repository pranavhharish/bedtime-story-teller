"""
Data models for the Bedtime Story Teller pipeline.
All components communicate through these dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StoryRequest:
    """Raw input from the user via Streamlit UI."""
    raw_input: str                        # "a small elephant scared of the dark"
    character_name: Optional[str] = None  # "Gajju" or None
    age_hint: Optional[str] = None        # "Little one (5-7)" or "Growing up (8-10)"
    extra_wishes: Optional[str] = None    # "make it funny" or None


@dataclass
class MythologyMapping:
    """Output of the Categorizer — which archetype + source to draw from."""
    archetype: str          # "Ganesha — Remover of Obstacles"
    source_text: str        # "Puranas"
    moral_theme: str        # "The light you need is already inside you"
    tone: str               # "wonder + warmth"
    inspired_by: str        # Human readable explanation for UI display
    character_seeds: str    # Suggested character traits based on archetype
    wisdom_figure: str = "a wise old creature"           # Who plays the guide role
    suggested_setting: str = "a village near a great forest"  # Evocative setting


@dataclass
class JudgeScore:
    """Scores for one evaluation dimension."""
    score: float            # 1.0 to 5.0
    critique: str           # Specific feedback for this dimension


@dataclass
class JudgeResult:
    """Full output of the LLM Judge."""
    age_appropriateness: JudgeScore
    story_arc: JudgeScore
    emotional_warmth: JudgeScore
    pacing: JudgeScore
    engagement: JudgeScore
    mythology_integrity: JudgeScore
    overall: float          # Average of all 6 scores
    passed: bool            # overall >= 4.0
    priority_fixes: list    # Top 2-3 actionable fixes for rewriter

    def scores_dict(self) -> dict:
        """Returns dimension name → score for easy UI rendering."""
        return {
            "Age Appropriateness": self.age_appropriateness.score,
            "Story Arc":           self.story_arc.score,
            "Emotional Warmth":    self.emotional_warmth.score,
            "Pacing":              self.pacing.score,
            "Engagement":          self.engagement.score,
            "Mythology Integrity": self.mythology_integrity.score,
        }

    def critique_dict(self) -> dict:
        """Returns dimension name → critique text."""
        return {
            "Age Appropriateness": self.age_appropriateness.critique,
            "Story Arc":           self.story_arc.critique,
            "Emotional Warmth":    self.emotional_warmth.critique,
            "Pacing":              self.pacing.critique,
            "Engagement":          self.engagement.critique,
            "Mythology Integrity": self.mythology_integrity.critique,
        }

    def weak_dimensions(self) -> dict:
        """Returns only dimensions scoring below 4.0 — for rewriter."""
        all_critiques = self.critique_dict()
        all_scores = self.scores_dict()
        return {
            dim: all_critiques[dim]
            for dim, score in all_scores.items()
            if score < 4.0
        }


@dataclass
class StoryIteration:
    """One pass through generate → judge."""
    iteration_number: int
    story_text: str
    judge_result: JudgeResult


@dataclass
class StoryOutput:
    """Final output — best story + full history."""
    best_story: str
    best_score: float
    total_iterations: int
    mythology_mapping: MythologyMapping
    final_judge: JudgeResult
    iteration_history: list = field(default_factory=list)  # list[StoryIteration]
