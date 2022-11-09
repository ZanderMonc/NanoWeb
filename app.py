import streamlit as st


def main() -> None:
    pass


if __name__ == "__main__":
    main()


def data_upload(filename: str):
    import pandas as pd
    try:
        with open(filename) as data:
            data = pd.read_csv("./data/titanic.csv")
            st.write(data)
    except FileNotFoundError:
        st.error('File not found.')