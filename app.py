import os
from dotenv import load_dotenv
import streamlit as st
import sys
from pathlib import Path
from functools import lru_cache

# Load .env
script_dir = Path(__file__).resolve().parent
env_path = script_dir / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Session state
if "songs" not in st.session_state:
    st.session_state.songs = None
if "mood_pct" not in st.session_state:
    st.session_state.mood_pct = None
if "bucket" not in st.session_state:
    st.session_state.bucket = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = {}

from moodsic.mood_calculator import COLOR_TO_VALUE, calculate_mood_percentage
from moodsic.rule_engine import get_bucket
from moodsic.recommender import recommend_songs_for_genres, update_user_preferences, log_interaction

@lru_cache(maxsize=32)
def get_cached_recommendations(tuple_genres, user_id, k):
    return recommend_songs_for_genres(list(tuple_genres), user_id, k)

# Bold editorial UI with warm daylight palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

    :root {
        --bg-a: #f5efe6;
        --bg-b: #fdf8f1;
        --ink: #1f1b18;
        --muted: #6f655a;
        --card: #fffdfa;
        --line: #e9ded0;
        --accent: #0f7b6c;
        --accent-2: #d6632c;
        --good: #0a8a5b;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        font-family: 'Space Grotesk', sans-serif;
        background:
            radial-gradient(900px 420px at 10% -10%, #ffe1b8 0%, transparent 60%),
            radial-gradient(800px 360px at 100% 0%, #d9efe9 0%, transparent 55%),
            linear-gradient(140deg, var(--bg-a), var(--bg-b));
        color: var(--ink);
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        background: rgba(255, 253, 250, 0.75);
        border: 1px solid var(--line);
        border-radius: 26px;
        padding: 1.2rem 1.4rem 1.4rem;
        backdrop-filter: blur(2px);
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 30px rgba(42, 34, 27, 0.08);
    }

    .hero-kicker {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border: 1px solid #d7c8b6;
        border-radius: 999px;
        padding: 0.3rem 0.65rem;
        color: var(--muted);
        background: #fffaf4;
        margin-bottom: 0.7rem;
    }

    .hero h1 {
        font-family: 'Fraunces', serif;
        font-size: clamp(2rem, 4.5vw, 3.3rem);
        line-height: 1.02;
        margin: 0;
        color: var(--ink);
        letter-spacing: -0.02em;
    }

    .hero p {
        margin: 0.55rem 0 0;
        color: var(--muted);
        font-size: 1rem;
        max-width: 60ch;
    }

    .panel {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.2rem;
        box-shadow: 0 10px 26px rgba(42, 34, 27, 0.06);
        margin-bottom: 1rem;
    }

    .panel-title {
        margin: 0 0 0.85rem;
        color: var(--ink);
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    .stSlider label, .stSelectbox label {
        color: var(--muted) !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
    }

    .stSlider > div > div > div {
        background: #ece4d8 !important;
    }

    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
    }

    .stSelectbox > div > div {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #fffcf8;
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid #0b6659;
        background: linear-gradient(135deg, var(--accent), #14907d);
        color: #ffffff;
        font-weight: 700;
        letter-spacing: 0.02em;
        min-height: 2.7rem;
        box-shadow: 0 8px 18px rgba(15, 123, 108, 0.2);
        transition: transform 160ms ease, box-shadow 180ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 22px rgba(15, 123, 108, 0.28);
    }

    .stat {
        border: 1px solid var(--line);
        background: #fff;
        border-radius: 16px;
        padding: 0.8rem 0.9rem;
        min-height: 86px;
    }

    .stat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-weight: 700;
    }

    .stat-value {
        margin-top: 0.25rem;
        font-family: 'Fraunces', serif;
        font-size: 1.45rem;
        color: var(--ink);
        line-height: 1.1;
    }

    .meter-wrap {
        display: grid;
        place-items: center;
        margin-top: 0.4rem;
    }

    .meter {
        width: 156px;
        height: 156px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        position: relative;
        border: 1px solid #dfd2c3;
        box-shadow: inset 0 0 0 8px #fff8ef;
    }

    .meter::after {
        content: "";
        width: 118px;
        height: 118px;
        border-radius: 999px;
        background: #fff;
        position: absolute;
        z-index: 0;
    }

    .meter-value {
        z-index: 1;
        font-family: 'Fraunces', serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--ink);
    }

    .song-card {
        border: 1px solid var(--line);
        background: #fff;
        border-radius: 18px;
        padding: 0.7rem;
        margin-bottom: 0.7rem;
        transition: border-color 140ms ease, transform 140ms ease;
    }

    .song-card:hover {
        border-color: #d9c7b4;
        transform: translateY(-1px);
    }

    .art-placeholder {
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 12px;
        background: linear-gradient(140deg, #fce4c6, #dceee8);
        border: 1px solid #e5d7c8;
        display: grid;
        place-items: center;
        font-size: 0.7rem;
        text-transform: uppercase;
        font-weight: 700;
        color: var(--muted);
    }

    .song-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }

    .song-artist {
        font-size: 0.92rem;
        color: var(--muted);
        margin-bottom: 0.35rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
    }

    .chip {
        font-size: 0.67rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
        color: #5c5044;
        border: 1px solid #e5d9cc;
        background: #fffaf4;
        border-radius: 999px;
        padding: 0.18rem 0.45rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
        }

        .hero {
            padding: 1rem 1rem 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <section class="hero">
        <span class="hero-kicker">Mood Based Discovery</span>
        <h1>Moodsic</h1>
        <p>Shape a playlist from your current energy, focus, and stress profile. Faster than scrolling, more personal than random shuffle.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

USER_ID = "user_1"

with st.container():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">Set Your Current State</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        q1 = st.slider("Energy", 1, 7, 4)
    with col2:
        q2 = st.slider("Mental Activity", 1, 7, 4)
    with col3:
        q3 = st.slider("Stress Capacity", 1, 7, 4)

    color = st.selectbox("Color Association", options=list(COLOR_TO_VALUE.keys()))
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("Generate Mix", use_container_width=True):
    with st.spinner("Composing your mood mix..."):
        mood_pct = calculate_mood_percentage(q1=q1, q2=q2, q3=q3, color=color)
        bucket_result = get_bucket(mood_pct)
        songs = get_cached_recommendations(tuple(bucket_result["genres"]), USER_ID, 4)
        st.session_state.mood_pct = mood_pct
        st.session_state.bucket = bucket_result
        st.session_state.songs = songs
        st.rerun()

if (
    st.session_state.songs
    and st.session_state.mood_pct is not None
    and st.session_state.bucket is not None
):
    mood_pct = float(st.session_state.mood_pct)
    bucket_result = st.session_state.bucket
    bucket_name = str(bucket_result.get("bucket", "Unknown"))
    mood_state = bucket_name.split(":")[0]
    genres = bucket_result.get("genres", [])

    st.markdown('<div class="panel">', unsafe_allow_html=True)

    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">Mood Score</div>
                <div class="stat-value">{mood_pct:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stat_col2:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">Mood State</div>
                <div class="stat-value">{mood_state}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with stat_col3:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">Target Genres</div>
                <div class="stat-value">{", ".join(genres[:2]) if genres else "Mixed"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    angle = (mood_pct / 100) * 360
    st.markdown(
        f"""
        <div class="meter-wrap">
            <div class="meter" style="background: conic-gradient(var(--accent-2) {angle}deg, #eee3d7 {angle}deg);">
                <div class="meter-value">{int(mood_pct)}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Recommendations")
    st.caption(f"Generated from {bucket_name}")

    for song in st.session_state.songs:
        feedback_key = f"feedback_{song['id']}"

        st.markdown('<div class="song-card">', unsafe_allow_html=True)
        art_col, info_col, like_col, pass_col = st.columns([1.1, 3, 1, 1])

        with art_col:
            if song.get("image_url"):
                st.image(song["image_url"], use_container_width=True)
            else:
                st.markdown('<div class="art-placeholder">No Art</div>', unsafe_allow_html=True)

        with info_col:
            st.markdown(
                f'<div class="song-title">{song.get("title", "Unknown")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="song-artist">{song.get("artist", "Unknown")}</div>',
                unsafe_allow_html=True,
            )

            tag_html = ""
            for g in song.get("genres", [])[:3]:
                tag_html += f'<span class="chip">{g}</span>'
            if tag_html:
                st.markdown(f'<div class="chip-row">{tag_html}</div>', unsafe_allow_html=True)

        with like_col:
            if st.button("Like", key=f"like_{song['id']}", use_container_width=True):
                update_user_preferences(USER_ID, song, True)
                log_interaction(song, True)
                st.session_state.feedback_given[feedback_key] = "liked"
                st.rerun()

        with pass_col:
            if st.button("Skip", key=f"dislike_{song['id']}", use_container_width=True):
                update_user_preferences(USER_ID, song, False)
                log_interaction(song, False)
                st.session_state.feedback_given[feedback_key] = "disliked"
                st.rerun()

        if feedback_key in st.session_state.feedback_given:
            status = st.session_state.feedback_given[feedback_key]
            if status == "liked":
                st.success("Saved to your preference profile")
            else:
                st.info("Preference updated")

        st.markdown('</div>', unsafe_allow_html=True)

    reset_col1, reset_col2, reset_col3 = st.columns([1, 2, 1])
    with reset_col2:
        if st.button("Start New Session", use_container_width=True):
            st.session_state.clear()
            st.rerun()