import streamlit as st

if st.button("Rerun"):
    st.experimental_rerun()

st.write("Hello, world!")