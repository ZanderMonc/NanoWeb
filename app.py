import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


def main() -> None:
    st.title('NanoWEB')
    st.sidebar.title("Switch to analysis")
    st.sidebar.title("Upload data")
    st.sidebar.title("Save data")

    df = pd.DataFrame(
        np.random.randn(100, 2),
        columns=['Displacement', 'Force'])
    c = alt.Chart(df).mark_line().encode(
        x='Displacement', y='Force')
    df_2 = pd.DataFrame(
        np.random.randn(100, 2),
        columns=['Displacement', 'Force'])
    d = alt.Chart(df_2).mark_line().encode(
        x='Displacement', y='Force')

    st.altair_chart(c, use_container_width=True)
    st.altair_chart(d, use_container_width=True)


if __name__ == "__main__":
    main()
