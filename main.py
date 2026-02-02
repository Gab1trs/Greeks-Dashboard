import streamlit as st

with st.sidebar:
    Spot = st.slider(
        label='Spot',
        min_value=0.0,
        max_value=200.0,
        value=100.0,
        step=0.5
    )