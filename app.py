import pandas as pd
import plspm.config as c
from plspm.plspm import Plspm
from plspm.scheme import Scheme
import streamlit as st

st.set_page_config(page_title="PLS-SEM Calculator", layout="wide")
st.title("PLS-SEM Web Calculator (Starter)")
st.caption("Upload a numeric CSV, assign items to constructs, and inspect basic path results.")

uploaded_file = st.file_uploader("Upload survey data (.csv)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head())

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

                st.subheader("Path Coefficients")
                st.dataframe(model.path_coefficients())

                st.subheader("Construct Summary")
                st.dataframe(model.inner_summary())

                st.subheader("Outer Loadings")
                st.dataframe(model.outer_model())
            except Exception as exc:
                st.error(f"Calculation error: {exc}")
