import pandas as pd
import plspm.config as c
from plspm.plspm import Plspm
from plspm.scheme import Scheme
import streamlit as st

st.set_page_config(
    page_title="PLS-SEM Calculator | @ciceroyce",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Responsive styling: White + Red + Yellow + Green + Mobile & PC friendly
st.markdown(
    """
    <style>
        :root {
            --bg-white: #ffffff;
            --surface-soft: #fffdf7;
            --red-main: #d62828;
            --red-dark: #a61c1c;
            --yellow-main: #f7b500;
            --yellow-soft: #fff6d1;
            --green-main: #1b8a4b;
            --green-soft: #e6f6ec;
            --text-dark: #1f2933;
            --border-light: #e5e7eb;
        }

        .stApp {
            background-color: var(--bg-white);
            color: var(--text-dark);
            padding-bottom: 72px;
        }

        .hero-banner {
            background: linear-gradient(120deg, var(--red-main) 0%, #e63946 58%, var(--yellow-main) 100%);
            color: #ffffff;
            padding: 20px 22px;
            border-radius: 14px;
            border-bottom: 5px solid var(--green-main);
            margin-bottom: 18px;
        }

        .hero-banner h1 {
            margin: 0 0 6px 0;
            font-size: clamp(1.45rem, 3vw, 2.1rem);
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .hero-banner p {
            margin: 0;
            font-size: clamp(0.9rem, 1.8vw, 1.02rem);
            opacity: 0.96;
        }

        .palette-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 18px;
        }

        .badge-red {
            background-color: #fdeCEC;
            color: var(--red-dark);
            border: 1px solid var(--red-main);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .badge-yellow {
            background-color: var(--yellow-soft);
            color: #7a5600;
            border: 1px solid var(--yellow-main);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .badge-green {
            background-color: var(--green-soft);
            color: var(--green-main);
            border: 1px solid var(--green-main);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        /* File uploader styling */
        [data-testid="stFileUploaderDropzone"] {
            background-color: var(--surface-soft);
            border: 2px dashed var(--green-main);
            border-radius: 12px;
        }

        /* Primary button styling */
        .stButton > button {
            width: 100%;
            background-color: var(--red-main);
            color: #ffffff;
            font-weight: 700;
            border: 2px solid var(--red-dark);
            border-radius: 10px;
            padding: 0.65rem 1.1rem;
            transition: all 0.15s ease-in-out;
        }

        .stButton > button:hover {
            background-color: var(--green-main);
            border-color: var(--green-main);
            color: #ffffff;
        }

        /* Centered bottom credit */
        .bottom-credit {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            background-color: rgba(255, 255, 255, 0.96);
            border-top: 3px solid var(--yellow-main);
            color: var(--text-dark);
            padding: 10px 14px;
            font-size: 0.9rem;
            font-weight: 600;
            z-index: 999;
        }

        .bottom-credit span.handle {
            color: var(--red-main);
            font-weight: 800;
        }

        @media (max-width: 640px) {
            .hero-banner {
                padding: 16px;
                border-radius: 10px;
            }
            .bottom-credit {
                font-size: 0.82rem;
                padding: 8px 10px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-banner">
        <h1>PLS-SEM Web Calculator</h1>
        <p>Upload a numeric CSV, assign survey items to constructs, and view PLS path outputs on mobile or desktop.</p>
    </div>
    <div class="palette-strip">
        <span class="badge-red">Red: Action &amp; Paths</span>
        <span class="badge-yellow">Yellow: Setup &amp; Notes</span>
        <span class="badge-green">Green: Data &amp; Results</span>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload survey data (.csv)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns to build constructs.")
        st.stop()

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

                st.success("Calculation completed.")

                st.subheader("Path Coefficients")
                st.dataframe(model.path_coefficients(), use_container_width=True)

                st.subheader("Construct Summary")
                st.dataframe(model.inner_summary(), use_container_width=True)

                st.subheader("Outer Loadings")
                st.dataframe(model.outer_model(), use_container_width=True)
            except Exception as exc:
                st.error(f"Calculation error: {exc}")

st.markdown(
    """
    <div class="bottom-credit">
        made by <span class="handle">@ciceroyce</span>
    </div>
    """,
    unsafe_allow_html=True,
)
