import random
import html
import textwrap
import streamlit as st

from data_loader import load_movies, get_feature_columns
from recommender import recommend_movies
from explanation import explain_recommendation


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CineVerse | Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LIGHT PASTEL COLORFUL THEME
# =========================================================

st.markdown(
    """
    <style>

    /* ================= STREAMLIT TOP BAR FIX ================= */

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* ================= GLOBAL BACKGROUND ================= */

    .stApp {
        background:
            radial-gradient(
                circle at 0% 0%,
                rgba(255, 204, 224, 0.75),
                transparent 28%
            ),
            radial-gradient(
                circle at 100% 5%,
                rgba(184, 229, 255, 0.80),
                transparent 30%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(218, 204, 255, 0.80),
                transparent 38%
            ),
            #f4f2ff;

        color: #303653;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    /* ================= SIDEBAR ================= */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #fff1f7 0%,
                #eef9ff 50%,
                #f2edff 100%
            );

        border-right: 1px solid #e5daf5;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #3b4165 !important;
    }

    /* ================= HERO ================= */

    .hero {
        position: relative;
        overflow: hidden;
        padding: 3.5rem 3rem;
        border-radius: 32px;
        margin-bottom: 2rem;

        background:
            linear-gradient(
                120deg,
                #bda7f6 0%,
                #f6b0ce 48%,
                #99dff0 100%
            );

        border: 1px solid rgba(255, 255, 255, 0.85);

        box-shadow:
            0 20px 50px rgba(130, 105, 190, 0.18),
            inset 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        right: -100px;
        top: -190px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.30);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        left: 45%;
        bottom: -150px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.20);
    }

    .hero-content {
        position: relative;
        z-index: 2;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.45rem 1rem;
        border-radius: 50px;

        background: rgba(255, 255, 255, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.75);

        color: #51406f;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.6px;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 3.6rem;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -1.8px;
        color: #302653;
        margin: 0;
    }

    .hero-title span {
        color: #087e9a;
    }

    .hero-subtitle {
        max-width: 700px;
        margin-top: 1rem;
        color: #514b70;
        font-size: 1.12rem;
        line-height: 1.7;
        font-weight: 550;
    }

    /* ================= SECTION TITLES ================= */

    .section-title {
        color: #303657;
        font-size: 1.7rem;
        font-weight: 850;
        margin-top: 1.5rem;
        margin-bottom: 0.25rem;
    }

    .section-subtitle {
        color: #7d82a3;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }

    /* ================= STAT CARDS ================= */

    .stat-card {
        min-height: 125px;
        padding: 1.35rem;
        border-radius: 23px;

        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.96),
                rgba(249, 244, 255, 0.96)
            );

        border: 1px solid #e5daf6;

        box-shadow:
            0 12px 30px rgba(117, 100, 170, 0.10),
            inset 0 1px 2px rgba(255, 255, 255, 0.9);
    }

    .stat-icon {
        font-size: 1.6rem;
    }

    .stat-value {
        color: #44356d;
        font-size: 1.8rem;
        font-weight: 900;
        margin-top: 0.3rem;
    }

    .stat-label {
        color: #898da9;
        font-size: 0.85rem;
    }

    /* ================= INFO PANEL ================= */

    .info-panel {
        padding: 1.25rem;
        border-radius: 19px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.95),
                rgba(240, 249, 255, 0.95)
            );

        border: 1px solid #dce2f5;
        color: #626984;
        line-height: 1.7;

        box-shadow: 0 9px 25px rgba(105, 116, 165, 0.07);
    }

    /* ================= MOVIE CARDS ================= */

    .movie-card {
        padding: 1.5rem;
        border-radius: 25px;
        margin: 1rem 0;

        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.98),
                rgba(249, 245, 255, 0.98)
            );

        border: 1px solid #e2d8f4;

        box-shadow:
            0 14px 34px rgba(111, 95, 163, 0.11),
            inset 0 1px 2px rgba(255, 255, 255, 0.9);
    }

    .movie-card:hover {
        border-color: #b49bea;
        box-shadow: 0 18px 40px rgba(119, 97, 188, 0.17);
    }

    .movie-rank {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 11px;

        background:
            linear-gradient(
                135deg,
                #9678e8,
                #ef91bd
            );

        color: white;
        font-size: 0.78rem;
        font-weight: 850;
        margin-bottom: 0.75rem;
    }

    .movie-title {
        color: #39335e;
        font-size: 1.45rem;
        font-weight: 900;
        margin-bottom: 0.45rem;
    }

    .movie-score {
        display: inline-block;
        padding: 0.4rem 0.85rem;
        border-radius: 50px;

        background: #e2faf3;
        border: 1px solid #abe9d8;

        color: #16866e;
        font-size: 0.88rem;
        font-weight: 850;
    }

    .feature-title {
        color: #626887;
        font-size: 0.9rem;
        font-weight: 750;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
    }

    .feature-tag {
        display: inline-block;
        padding: 0.38rem 0.78rem;
        margin: 0.25rem 0.25rem 0.25rem 0;

        border-radius: 50px;

        background:
            linear-gradient(
                135deg,
                #eee5ff,
                #e0f7ff
            );

        border: 1px solid #d4c8f3;

        color: #62568d;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .empty-feature {
        color: #999db7;
        font-size: 0.85rem;
    }

    /* ================= MOOD CARDS ================= */

    .mood-card {
        min-height: 125px;
        padding: 1.2rem 0.5rem;
        text-align: center;
        border-radius: 21px;

        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.96),
                rgba(247, 242, 255, 0.98)
            );

        border: 1px solid #e3d9f5;
        box-shadow: 0 9px 23px rgba(122, 103, 172, 0.08);
    }

    .mood-emoji {
        font-size: 2.1rem;
    }

    .mood-name {
        color: #51486f;
        font-size: 0.85rem;
        font-weight: 800;
        margin-top: 0.5rem;
    }

    /* ================= BUTTONS ================= */

    .stButton > button {
        border-radius: 14px;

        background:
            linear-gradient(
                135deg,
                #9678e8,
                #ed91b9
            );

        border: 1px solid #d5c3f1;
        color: white;

        font-weight: 850;
        padding: 0.65rem 1rem;

        box-shadow: 0 8px 18px rgba(145, 112, 207, 0.15);
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        color: white;
        border-color: #7acbdc;
        transform: translateY(-2px);
        box-shadow: 0 0 24px rgba(114, 204, 224, 0.28);
    }

    /* ================= SELECT BOX ================= */

    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border: 1px solid #dcd2ef;
        border-radius: 13px;
        color: #454064;
    }

    /* ================= TABS ================= */

    button[data-baseweb="tab"] {
        color: #8589a7;
        font-weight: 800;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #8a65d7;
    }

    /* ================= FOOTER ================= */

    .footer {
        text-align: center;
        color: #969ab4;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e3ddf1;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

try:
    df = load_movies()
    feature_columns = get_feature_columns(df)

except FileNotFoundError:
    st.error(
        "❌ movies.csv was not found. Please place it inside "
        "the smart_recommender folder."
    )
    st.stop()

except Exception as error:
    st.error(f"Could not load movie data: {error}")
    st.stop()


# =========================================================
# SESSION STATE
# =========================================================

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = "✨ Any Mood"

if "favorites" not in st.session_state:
    st.session_state.favorites = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:0.8rem 0 1.2rem 0;">
            <div style="font-size:2.8rem;">🎬</div>
            <h2 style="margin:0; color:#403466;">CineVerse</h2>
            <p style="color:#8589a7; font-size:0.85rem;">
                Your personal movie universe
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("🎛️ Discovery Controls")

    top_n = st.slider(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5
    )

    st.divider()

    st.subheader("🧠 How It Works")

    st.markdown(
        """
        <div class="info-panel">
            <b>Step 1:</b> Movie features become numerical vectors.<br><br>
            <b>Step 2:</b> Cosine similarity compares the vectors.<br><br>
            <b>Step 3:</b> Similar movies are ranked.<br><br>
            <b>Step 4:</b> Ollama explains the result.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.caption(
        "Built with Python • Streamlit • NumPy • Pandas • Ollama"
    )


# =========================================================
# HERO SECTION
# =========================================================

# Native Streamlit hero section.
# This intentionally avoids rendering the HTML as a code block.
st.markdown("### ✦ PERSONALIZED MOVIE DISCOVERY")
st.title("Welcome to CineVerse")
st.markdown(
    "Tell us your vibe, choose a movie, and discover your next "
    "obsession using mathematical similarity, mood intelligence, "
    "and your local AI movie companion."
)


# =========================================================
# STATISTICS
# =========================================================

st.markdown(
    '<div class="section-title">🌈 Your Movie Universe</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Your current movie dataset and recommendation features.</div>',
    unsafe_allow_html=True
)

stat1, stat2, stat3, stat4 = st.columns(4)

with stat1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-icon">🎞️</div>
            <div class="stat-value">{len(df)}</div>
            <div class="stat-label">Movies in library</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with stat2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-icon">🧩</div>
            <div class="stat-value">{len(feature_columns)}</div>
            <div class="stat-label">Features used</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with stat3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-icon">💜</div>
            <div class="stat-value">{len(st.session_state.favorites)}</div>
            <div class="stat-label">Saved favorites</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with stat4:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-icon">🤖</div>
            <div class="stat-value">Local AI</div>
            <div class="stat-label">Powered by Ollama</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# Dataset note
st.caption(
    "ℹ️ These numbers come from your current movies.csv file. To show more movies, add more movie records to that file; the app will load them automatically."
)


# =========================================================
# TABS
# =========================================================

discover_tab, mood_tab, collection_tab, about_tab = st.tabs(
    [
        "🔎 Discover",
        "🎭 Mood Studio",
        "💜 My Collection",
        "ℹ️ About"
    ]
)


# =========================================================
# DISCOVER TAB
# =========================================================

with discover_tab:

    st.markdown(
        '<div class="section-title">🎬 Find Your Next Favorite</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Select a movie you like and discover movies with similar feature patterns.</div>',
        unsafe_allow_html=True
    )

    select_col, surprise_col = st.columns([3, 1])

    with select_col:

        selected_title = st.selectbox(
            "Choose a movie",
            options=df["title"].tolist(),
            key="movie_selector"
        )

    with surprise_col:

        st.write("")

        surprise_button = st.button(
            "🎲 Surprise Me",
            use_container_width=True
        )

    if surprise_button:

        selected_title = random.choice(df["title"].tolist())

        st.session_state.selected_movie = selected_title

        st.success(
            f"🎲 Surprise movie selected: **{selected_title}**"
        )

    discover_button = st.button(
        "✨ Discover Similar Movies",
        use_container_width=True
    )

    if discover_button or surprise_button:

        st.session_state.selected_movie = selected_title

        with st.spinner("🧮 Calculating similarity scores..."):

            results = recommend_movies(
                df,
                selected_title,
                top_n
            )

        st.session_state.recommendations = results

    results = st.session_state.recommendations

    if results is not None:

        if results.empty:

            st.warning("No recommendations found.")

        else:

            selected_movie = df[
                df["title"] == st.session_state.selected_movie
            ].iloc[0]

            st.markdown(
                f"""
                <div class="info-panel">
                    <b>Selected movie:</b> {st.session_state.selected_movie}<br>
                    <b>Calculation method:</b> Cosine similarity<br>
                    <b>Result:</b> Movies are ranked according to the closeness
                    of their numerical feature vectors.
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")

            st.markdown(
                '<div class="section-title">🌟 Your Recommendations</div>',
                unsafe_allow_html=True
            )

            for index, row in results.iterrows():

                recommended_movie = df[
                    df["title"] == row["title"]
                ].iloc[0]

                if "similarity" in row.index:
                    score = float(row["similarity"])
                elif "similarity_score" in row.index:
                    score = float(row["similarity_score"])
                else:
                    score = 0.0

                # recommender.py may return either 0–1 or 0–100.
                score_percentage = score if score > 1 else score * 100
                score_percentage = max(0.0, min(100.0, score_percentage))

                with st.spinner(
                    f"🤖 CineBuddy is explaining {row['title']}..."
                ):

                    explanation = explain_recommendation(
                        selected_title=st.session_state.selected_movie,
                        recommended_title=row["title"],
                        similarity_score=score_percentage,
                        selected_row=selected_movie,
                        recommended_row=recommended_movie,
                        feature_columns=feature_columns
                    )

                shared_features = explanation["shared_features"]

                feature_html = ""

                for feature in shared_features:

                    feature_html += (
                        f'<span class="feature-tag">✦ {feature}</span>'
                    )

                if not feature_html:

                    feature_html = (
                        '<span class="empty-feature">'
                        'No dominant shared feature identified.'
                        '</span>'
                    )

                safe_recommended_title = html.escape(str(row["title"]))

                recommendation_card = textwrap.dedent(
                    f"""
                    <div class="movie-card">
                        <div class="movie-rank">MATCH #{index + 1}</div>
                        <div class="movie-title">🎬 {safe_recommended_title}</div>
                        <div class="movie-score">Similarity: {score_percentage:.1f}%</div>
                        <div class="feature-title">Shared movie characteristics</div>
                        <div>{feature_html}</div>
                    </div>
                    """
                ).strip()

                st.markdown(
                    recommendation_card,
                    unsafe_allow_html=True
                )

                st.info(
                    f"🤖 **CineBuddy's Explanation**\n\n"
                    f"{explanation['explanation']}"
                )

                if st.button(
                    f"💜 Save {row['title']}",
                    key=f"save_{row['title']}"
                ):

                    if row["title"] not in st.session_state.favorites:

                        st.session_state.favorites.append(
                            row["title"]
                        )

                        st.success(
                            f"{row['title']} added to your collection!"
                        )

                    else:

                        st.info(
                            "This movie is already in your collection."
                        )


# =========================================================
# MOOD STUDIO TAB
# =========================================================

with mood_tab:

    st.markdown(
        '<div class="section-title">🎭 Mood Studio</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Choose the kind of movie experience you want today.</div>',
        unsafe_allow_html=True
    )

    moods = [
        ("😂", "Fun & Comedy"),
        ("🚀", "Adventure"),
        ("💖", "Romance"),
        ("🧠", "Thoughtful"),
        ("👻", "Thriller"),
        ("🌌", "Sci-Fi")
    ]

    mood_columns = st.columns(6)

    for index, (emoji, mood_name) in enumerate(moods):

        with mood_columns[index]:

            st.markdown(
                f"""
                <div class="mood-card">
                    <div class="mood-emoji">{emoji}</div>
                    <div class="mood-name">{mood_name}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "Explore",
                key=f"mood_button_{index}",
                use_container_width=True
            ):

                st.session_state.selected_mood = mood_name

                st.success(
                    f"🎭 Mood selected: {mood_name}"
                )

    st.write("")

    st.markdown(
        f"""
        <div class="info-panel">
            <b>Current mood:</b> {st.session_state.selected_mood}<br><br>
            Mood-based mathematical weighting will be connected in the
            next stage. This will allow CineVerse to prioritize different
            movie characteristics according to your selected mood.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# COLLECTION TAB
# =========================================================

with collection_tab:

    st.markdown(
        '<div class="section-title">💜 My Collection</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Save movies you want to explore later.</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.favorites:

        st.markdown(
            """
            <div class="info-panel">
                ✨ Your collection is empty.<br><br>
                Discover movies and save your favorites here.
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        for movie in st.session_state.favorites:

            left, right = st.columns([5, 1])

            with left:

                st.markdown(
                    f"""
                    <div class="movie-card">
                        <div class="movie-title">💜 {movie}</div>
                        <div style="color:#858aa7;">
                            Saved in your personal collection
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with right:

                if st.button(
                    "Remove",
                    key=f"remove_{movie}"
                ):

                    st.session_state.favorites.remove(movie)
                    st.rerun()


# =========================================================
# ABOUT TAB
# =========================================================

with about_tab:

    st.markdown(
        '<div class="section-title">ℹ️ About CineVerse</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-panel">

        <h3>What is CineVerse?</h3>

        CineVerse is a smart movie discovery application that recommends
        movies using numerical movie characteristics.

        <br><br>

        <h3>How does the recommendation work?</h3>

        <b>1. Feature Representation</b><br>
        Each movie is represented as a numerical vector.

        <br><br>

        <b>2. Cosine Similarity</b><br>
        The system measures the angle-based similarity between movie vectors.

        <br><br>

        <b>3. Ranking</b><br>
        Movies with higher similarity scores appear first.

        <br><br>

        <b>4. Explainable AI</b><br>
        Ollama provides a short explanation based only on the available
        movie features.

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🎬 CineVerse • Discover stories. Explore moods. Find your next favorite.
        <br>
        Built with Python, Streamlit, NumPy, Pandas and Ollama.
    </div>
    """,
    unsafe_allow_html=True
)