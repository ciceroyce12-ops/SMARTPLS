import pandas as pd
import plspm.config as c
from plspm.plspm import Plspm
from plspm.scheme import Scheme
import streamlit as st

st.set_page_config(
    page_title="PLS-SEM Web Calculator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        /* Palette: Red (#D92B2B), Yellow (#F5B700), Green (#15803D), White (#FFFFFF) */
        .stApp {
            background-color: #FFFFFF;
            color: #1A1A1A;
        }

        .brand-banner {
            background: linear-gradient(135deg, #FFFFFF 0%, #FFFBEB 65%, #F0FDF4 100%);
            border: 2px solid #15803D;
            border-left: 8px solid #D92B2B;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 18px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        }

        .brand-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }

        .pill-red {
            background-color: #D92B2B;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 999px;
        }

        .pill-yellow {
            background-color: #F5B700;
            color: #1A1A1A;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 999px;
        }

        .pill-green {
            background-color: #15803D;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 999px;
        }

        .brand-title {
            margin: 0 0 6px 0;
            color: #15803D;
            font-size: clamp(1.45rem, 4vw, 2.2rem);
            font-weight: 800;
            line-height: 1.2;
        }

        .brand-sub {
            margin: 0;
            color: #2B2B2B;
            font-size: clamp(0.92rem, 2.5vw, 1.05rem);
            line-height: 1.45;
        }

        .section-tag {
            display: inline-block;
            background-color: #FEF9C3;
            color: #1A1A1A;
            border: 1.5px solid #F5B700;
            border-left: 5px solid #15803D;
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 1rem;
            margin-top: 14px;
            margin-bottom: 8px;
        }

        /* Primary button styling: Green with crisp white text */
        div.stButton > button {
            width: 100%;
            min-height: 46px;
            background-color: #15803D;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 1rem;
            border: 2px solid #15803D;
            border-radius: 10px;
            transition: all 0.15s ease;
        }

        div.stButton > button:hover {
            background-color: #D92B2B;
            border-color: #D92B2B;
            color: #FFFFFF;
        }

        /* File uploader border highlight */
        [data-testid="stFileUploaderDropzone"] {
            background-color: #FFFDF7;
            border: 2px dashed #15803D;
            border-radius: 12px;
        }

        /* Ensure dataframes scroll cleanly on small mobile viewports */
        [data-testid="stDataFrame"] {
            width: 100%;
            overflow-x: auto;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
        }

        .footer-credit {
            margin-top: 32px;
            padding: 14px 16px;
            background-color: #FFFFFF;
            border-top: 3px solid #D92B2B;
            border-bottom: 3px solid #15803D;
            text-align: center;
            font-weight: 700;
            color: #1A1A1A;
            font-size: 0.95rem;
        }

        .footer-credit span.accent-red {
            color: #D92B2B;
        }

        .footer-credit span.accent-yellow {
            background-color: #F5B700;
            color: #1A1A1A;
            padding: 2px 8px;
            border-radius: 6px;
        }

        .footer-credit span.accent-green {
            color: #15803D;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="brand-banner">
        <div class="brand-pills">
            <span class="pill-red">PLS-SEM</span>
            <span class="pill-yellow">MOBILE & PC</span>
            <span class="pill-green">FREE WEB TOOL</span>
        </div>
        <h1 class="brand-title">PLS-SEM Web Calculator</h1>
        <p class="brand-sub">Upload a numeric CSV, map survey items to constructs, and run path calculations on desktop or mobile.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-tag">1. Upload Survey Data (.CSV)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a numeric CSV file", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.markdown('<div class="section-tag">2. Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns to build constructs.")
        st.stop()

    st.markdown('<div class="section-tag">3. Assign Constructs & Run</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        x_name = st.text_input("Independent Construct Name", value="Construct_X")
        x_items = st.multiselect(f"Select items for {x_name}", numeric_cols)

    with col2:
        y_name = st.text_input("Dependent Construct Name", value="Construct_Y")
        available_for_y = [col for col in numeric_cols if col not in x_items]
        y_items = st.multiselect(f"Select items for {y_name}", available_for_y)

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
        <span class="accent-green">made</span>
        <span class="accent-red">by</span>
        <span class="accent-yellow">@ciceroyce innit</span>
    </div>
    """,
    unsafe_allow_html=True,
)
