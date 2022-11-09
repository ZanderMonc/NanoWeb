import streamlit as st
import pandas as pd
import os


def main() -> None:
    pass


if __name__ == "__main__":
    main()


def data_upload(filename: str):
    try:
        with open(filename) as data:
            data_in = pd.read_csv(data)
            st.write(data_in)
            st.write('Data uploaded successfully')
    except FileNotFoundError:
        st.error('File not found.')


def data_export(data, filename):
    try:
        with open(filename) as f:
            st.download_button('Download CSV', f, 'data.csv')
    except FileNotFoundError:
        st.error('File not found.')


# def export_test():
#     df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
#     data_export(df, 'data.csv')


