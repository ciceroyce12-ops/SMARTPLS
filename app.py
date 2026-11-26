import pandas as pd
import plspm.config as c
from plspm.plspm import Plspm
from plspm.scheme import Scheme
import streamlit as st

st.set_page_config(
    page_title="PLS-SEM Web Calculator | made by @ciceroyce",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        :root {
            --bg-white: #FFFFFF;
            --surface-white: #FFFDF9;
            --red-main: #D92B2B;
            --red-dark: #B51D1D;
            --yellow-main: #F6C90E;
            --yellow-soft: #FFF8D6;
            --green-main: #15803D;
            --green-soft: #ECFDF3;
            --ink-dark: #18181B;
            --border-light: #E4E4E7;
        }

        .stApp {
            background-color: var(--bg-white);
            color: var(--ink-dark);
        }

        .hero-box {
            background: var(--surface-white);
            border: 2px solid var(--green-main);
            border-left: 8px solid var(--red-main);
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 14px rgba(24, 24, 27, 0.05);
        }

        .creator-pill {
            display: inline-block;
            background-color: var(--yellow-main);
            color: var(--ink-dark);
            font-weight: 700;
            font-size: 0.85rem;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            border: 1.5px solid var(--green-main);
            margin-bottom: 0.5rem;
        }

        .hero-title {
            color: var(--green-main);
            font-size: clamp(1.45rem, 4vw, 2.2rem);
            font-weight: 800;
            line-height: 1.2;
            margin: 0.2rem 0 0.4rem 0;
        }

        .hero-sub {
            color: var(--ink-dark);
            font-size: clamp(0.92rem, 2.3vw, 1.05rem);
            margin: 0;
        }

        .section-tag {
            display: inline-block;
            background-color: var(--green-soft);
            color: var(--green-main);
            border-left: 5px solid var(--green-main);
            font-weight: 700;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            margin-top: 0.8rem;
            margin-bottom: 0.4rem;
            font-size: 1.05rem;
        }

        .stButton > button {
            width: 100%;
            background-color: var(--red-main) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border: 2px solid var(--green-main) !important;
            border-radius: 10px !important;
            padding: 0.65rem 1rem !important;
            font-size: 1rem !important;
        }

        .stButton > button:hover {
            background-color: var(--red-dark) !important;
            border-color: var(--yellow-main) !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background-color: var(--yellow-soft) !important;
            border: 2px dashed var(--green-main) !important;
            border-radius: 12px !important;
        }

        [data-testid="stDataFrame"] {
            border: 1.5px solid var(--green-main);
            border-radius: 10px;
            overflow: hidden;
            background: var(--bg-white);
        }

        .footer-credit {
            margin-top: 2rem;
            padding: 0.9rem 1rem;
            text-align: center;
            background-color: var(--green-soft);
            border-top: 3px solid var(--yellow-main);
            border-bottom: 3px solid var(--red-main);
            border-radius: 10px;
            color: var(--green-main);
            font-weight: 700;
            font-size: 0.95rem;
        }

        @media (max-width: 640px) {
            .hero-box {
                padding: 0.9rem 0.95rem;
                border-radius: 10px;
            }
            .block-container {
                padding-left: 0.85rem !important;
                padding-right: 0.85rem !important;
                padding-top: 1rem !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-box">
        <div class="creator-pill">made by @ciceroyce</div>
        <h1 class="hero-title">PLS-SEM Web Calculator</h1>
        <p class="hero-sub">Upload a numeric CSV, assign items to constructs, and run PLS path modeling on mobile or desktop.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-tag">1. Upload Dataset (.CSV)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a CSV file with numeric survey columns", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.markdown('<div class="section-tag">2. Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns to build constructs.")
        st.stop()

    st.markdown('<div class="section-tag">3. Map Constructs & Items</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        x_name = st.text_input("Independent Construct Name", value="Construct_X")
        x_items = st.multiselect(f"Select items for {x_name}", numeric_cols)

    with col2:
        y_name = st.text_input("Dependent Construct Name", value="Construct_Y")
        available_for_y = [col for col in numeric_cols if col not in x_items]
        y_items = st.multiselect(f"Select items for {y_name}", available_for_y)

    st.markdown('<div class="section-tag">4. Run Calculation</div>', unsafe_allow_html=True)
    if st.button("Run PLS Calculation"):
        if not x_items or not y_items:
            st.error("Please select at least one item for both constructs.")
        elif x_name.strip() == y_name.strip():
            st.error("Construct names must be different.")
        else:
            try:
                structure = c.Structure()
                structure.add_path([x_name], [y_name])

                config = c.Config(structure.path(), default_mode=c.Mode.A)
                config.add_lv(x_name, c.Mode.A, *x_items)
                config.add_lv(y_name, c.Mode.A, *y_items)

                model = Plspm(df, config, Scheme.PATH)

                st.markdown('<div class="section-tag">Path Coefficients</div>', unsafe_allow_html=True)
                st.dataframe(model.path_coefficients(), use_container_width=True)

                st.markdown('<div class="section-tag">Construct Summary</div>', unsafe_allow_html=True)
                st.dataframe(model.inner_summary(), use_container_width=True)

                st.markdown('<div class="section-tag">Outer Loadings</div>', unsafe_allow_html=True)
                st.dataframe(model.outer_model(), use_container_width=True)
            except Exception as exc:
                st.error(f"Calculation error: {exc}")

st.markdown(
    """
    <div class="footer-credit">
        made by @ciceroyce &bull; Red / Yellow / Green / White Responsive UI
    </div>
    """,
    unsafe_allow_html=True,
)
