"""
Streamlit frontend — all UI lives here.
Calls main.run_pipeline() for all logic.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from models.story_types import StoryRequest
from main import run_pipeline
from rewriter import revise_with_user_note

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌙 Bedtime Story Teller",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .story-box {
        background-color: #fdf6e3;
        border-left: 4px solid #e8a020;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        font-size: 1.05rem;
        line-height: 1.8;
        color: #3d2b1f;
        font-family: Georgia, serif;
    }
    .mapping-box {
        background-color: #f0f4ff;
        border-left: 4px solid #5566cc;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: #1a1a3e;
    }
    .score-label {
        font-size: 0.85rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)


# ── OpenAI client ──────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=api_key)


# ── Session state init ─────────────────────────────────────────────────
def init_state():
    defaults = {
        "stage":        "input",   # input | processing | output
        "request":      None,
        "output":       None,
        "client":       None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()


# ══════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════
st.markdown("# 🌙 Bedtime Story Teller")
st.caption("Stories rooted in the wisdom of Indian Mythology")
st.divider()


# ══════════════════════════════════════════════════════════════════════
# SCREEN: INPUT
# ══════════════════════════════════════════════════════════════════════
if st.session_state.stage == "input":

    st.markdown("### Tell me about your story ✨")
    st.markdown(
        "Draw from ancient India — epics, fables, clever courts, "
        "and the wisdom of the ages."
    )

    story_idea = st.text_area(
        "What should the story be about?",
        placeholder="e.g. a small elephant who is scared of the dark...",
        height=100
    )

    col1, col2 = st.columns(2)

    with col1:
        char_name = st.text_input(
            "Character name",
            placeholder="Gajju, Arjun, Maya... (optional)"
        )

    with col2:
        age_hint = st.radio(
            "Who's listening?",
            ["Little one (5–7)", "Growing up (8–10)"],
            horizontal=True
        )

    extra = st.text_input(
        "Any special wishes?",
        placeholder="make it funny, include a talking crow... (optional)"
    )

    st.markdown("")

    if st.button("🪔 Tell Me A Story", type="primary", use_container_width=True):
        if not story_idea.strip():
            st.warning("Please tell me what the story should be about!")
        else:
            st.session_state.request = StoryRequest(
                raw_input=story_idea.strip(),
                character_name=char_name.strip() or None,
                age_hint=age_hint,
                extra_wishes=extra.strip() or None
            )
            st.session_state.client = get_client()
            st.session_state.stage  = "processing"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════
# SCREEN: PROCESSING
# ══════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "processing":

    st.markdown("### 🪔 Weaving your story...")

    with st.status("Drawing from ancient wisdom...", expanded=True) as status_box:

        status_messages = []

        def on_status(msg: str):
            status_messages.append(msg)
            st.write(msg)

        output = run_pipeline(
            client=st.session_state.client,
            request=st.session_state.request,
            on_status=on_status
        )

        status_box.update(
            label=f"✅ Your story is ready! (score: {output.best_score:.1f}/5.0)",
            state="complete"
        )

    st.session_state.output = output
    st.session_state.stage  = "output"
    st.rerun()


# ══════════════════════════════════════════════════════════════════════
# SCREEN: OUTPUT
# ══════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "output":

    output  = st.session_state.output
    mapping = output.mythology_mapping
    judge   = output.final_judge

    # ── Mythology mapping card ─────────────────────────────────────────
    st.markdown(
        f"""
        <div class="mapping-box">
        <b>✨ Inspired by:</b> {mapping.archetype} &nbsp;·&nbsp; 
        <i>{mapping.source_text}</i><br>
        <b>💡 Moral:</b> {mapping.moral_theme}<br><br>
        <span style="color:#3a3a5c; font-size:0.9rem">{mapping.inspired_by}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Story display ──────────────────────────────────────────────────
    st.markdown("### 📖 Your Bedtime Story")
    story_html = output.best_story.replace("\n", "<br>")
    st.markdown(
        f'<div class="story-box">{story_html}</div>',
        unsafe_allow_html=True
    )

    st.markdown("")

    # ── Judge scores ───────────────────────────────────────────────────
    with st.expander(f"📊 Story Quality — {output.best_score:.1f} / 5.0", expanded=False):
        scores = judge.scores_dict()

        for dim, score in scores.items():
            col1, col2 = st.columns([5, 1])
            with col1:
                color = "normal" if score >= 4.0 else "off"
                st.progress(
                    score / 5.0,
                    text=f"{dim}"
                )
            with col2:
                emoji = "✅" if score >= 4.0 else "⚠️"
                st.markdown(f"**{score}** {emoji}")

        st.markdown(f"**Overall: {output.best_score:.1f} / 5.0**")
        st.markdown(f"*Refined over {output.total_iterations} iteration(s)*")

    st.divider()

    # ── Revision section ───────────────────────────────────────────────
    st.markdown("### ✏️ Want to change anything?")

    revision_note = st.text_input(
        "What would you like to change?",
        placeholder="make it funnier, add a talking parrot, change the ending..."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✏️ Revise Story", use_container_width=True):
            if revision_note.strip():
                with st.spinner("Revising your story..."):
                    revised = revise_with_user_note(
                        client=st.session_state.client,
                        story_text=output.best_story,
                        user_note=revision_note.strip(),
                        request=st.session_state.request
                    )
                    # Update the output with revised story
                    st.session_state.output.best_story = revised
                    st.rerun()
            else:
                st.warning("Tell me what you'd like to change!")

    with col2:
        if st.button("🔄 New Story", use_container_width=True):
            # Clear everything and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ── Download button ────────────────────────────────────────────────
    st.markdown("")
    st.download_button(
        label="📥 Save Story as Text",
        data=f"🌙 Bedtime Story\n\nInspired by: {mapping.archetype}\n"
             f"Source: {mapping.source_text}\n"
             f"Moral: {mapping.moral_theme}\n\n"
             f"{'─' * 50}\n\n"
             f"{output.best_story}",
        file_name="bedtime_story.txt",
        mime="text/plain",
        use_container_width=True
    )
