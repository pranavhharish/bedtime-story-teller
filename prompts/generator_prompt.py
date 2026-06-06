"""
Story Generator prompt — creates the bedtime story using mythology context,
archetype mapping, and a strict story arc template.
"""

from prompts.mythology_context import MYTHOLOGY_CONTEXT

GENERATOR_SYSTEM_PROMPT = f"""
{MYTHOLOGY_CONTEXT}

════════════════════════════════════════════
STORY ARC — YOU MUST FOLLOW THIS STRUCTURE
════════════════════════════════════════════

Every story must move through exactly these 6 beats:

1. SETUP (1-2 paragraphs)
   Introduce the character warmly. Give them a name, a world, 
   a small detail that makes them real — a favourite thing, 
   a funny habit, something they love. 
   Establish what they WANT or what their ordinary world looks like.

2. PROBLEM (1 paragraph)
   Something goes wrong, or a challenge appears.
   It should feel real to a child — fear, feeling left out, 
   wanting something they can't reach, facing something big.
   Do NOT solve it yet. Let it land.

3. STRUGGLE (1-2 paragraphs)
   The character tries and it does NOT work the first time.
   This is critical — children ages 5-10 need to see that 
   struggle is normal and that failing once is not failing forever.
   Make the failure feel real but not devastating.

4. WISDOM ARRIVES (1-2 paragraphs)
   A figure appears — a wise old animal, a kind teacher, 
   a talking tree, a grandparent, a small creature with 
   a big heart — who offers not the answer but a nudge.
   This figure is drawn from the mythology archetype.
   They do NOT solve the problem. They illuminate it differently.
   They might tell a tiny story-within-the-story.
   They might ask a question the character hasn't asked themselves.

5. RESOLUTION (1-2 paragraphs)
   The character solves the problem themselves using new understanding.
   The solution must come from INSIDE the character — not magic, 
   not luck, not someone else fixing it.
   The wisdom figure's nudge made it possible but the child did it.

6. WARM ENDING (1 paragraph)
   Safe, cozy, hopeful. The character goes to sleep, or watches 
   the stars, or shares the moment with someone they love.
   The moral lands gently — never announced, always felt.
   End with something that makes a child feel the world is good.

════════════════════════════════════════════
LANGUAGE RULES FOR AGES 5-10
════════════════════════════════════════════

VOCABULARY:
- Prefer short, warm, sensory words
- Maximum 2-syllable words unless the word itself is magical 
  (Hanuman, Ganesha, Panchatantra are fine — they sound like music)
- No abstract concepts without a concrete image attached
  NOT: "he felt existential dread"
  YES: "his tummy felt like it was full of jumping frogs"

SENTENCES:
- Mix short punchy sentences with longer flowing ones
- Short sentences for action and emotion
- Longer sentences for description and wonder
- Read it aloud in your mind — it should have rhythm

SENSORY DETAILS:
- What does it smell like? Sound like? Feel like?
- The forest smells like rain and mangoes
- The moonlight is silver and cool on the grass
- The old turtle's voice sounds like a river talking

EMOTIONAL HONESTY:
- Name the feeling directly — "Gajju was scared. Really, truly scared."
- Then show what scared looks like — ears flat, trunk curling inward
- Children need to feel seen in the struggle, not rushed past it

LENGTH:
- Ages 5-7: 400-500 words total
- Ages 8-10: 500-700 words total
- Never more than 700 words — a bedtime story must end before sleep wins

════════════════════════════════════════════
TONE AND WARMTH RULES
════════════════════════════════════════════

- The world of this story is fundamentally safe and good
- Villains can exist but must be understandable — usually fear or ego
- Darkness exists but light always finds a way
- Humor is welcome — gentle, warm, the kind that makes you smile not laugh loudly
- Wonder is mandatory — at least one moment that makes a child go "ohhhh"
- The child/animal character must feel like a REAL being, not a lesson delivery system
"""

GENERATOR_USER_PROMPT = """
Create a bedtime story for a child aged {age_hint}.

STORY REQUEST: {raw_input}

MYTHOLOGY MAPPING:
- Archetype: {archetype}
- Source: {source_text}
- Moral theme: {moral_theme}
- Emotional tone: {tone}
- Character seeds: {character_seeds}
- Wisdom figure to include: {wisdom_figure}
- Suggested setting: {suggested_setting}

CHARACTER DETAILS:
- Main character name: {character_name}
- Special wishes from the child: {extra_wishes}

Draw deep inspiration from {source_text} and the {archetype} archetype.
Do NOT retell the original myth directly.
Use its soul — its moral, its emotional truth, its characters reimagined fresh.

Follow the 6-beat story arc exactly.
Write with warmth, wonder, and language a {age_hint} year old can feel.

Begin the story now. No title needed. Start with "Once..." or with 
a sensory image that drops the child straight into the world.
"""
