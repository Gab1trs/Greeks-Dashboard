import streamlit as st
import datetime as dt
import numpy as np
import pandas as pd


st.set_page_config(layout="wide", page_title="Option Dashboard")

def input_synchro(label, min_val, max_val, default_val, step, key_suffix):
    if key_suffix not in st.session_state:
        st.session_state[key_suffix] = default_val

    def update_from_slider():
        current_value=st.session_state[f'{key_suffix}_slider']
        st.session_state[key_suffix] = current_value
        st.session_state[f"{key_suffix}_input"] = current_value
    
    def update_from_input():
        current_value = st.session_state[f"{key_suffix}_input"]
        st.session_state[key_suffix] = current_value
        st.session_state[f"{key_suffix}_slider"] = current_value

    st.write(f"**{label}**") 
    col1, col2 = st.columns([2, 1]) 
    
    with col1:
        st.slider(
            label="", 
            min_value=float(min_val),
            max_value=float(max_val),
            value=float(st.session_state[key_suffix]),
            step=float(step),
            key=f"{key_suffix}_slider",
            on_change=update_from_slider,
            label_visibility="collapsed" 
        )
        
    with col2:
        st.number_input(
            label="",
            min_value=float(min_val),
            max_value=float(max_val),
            value=float(st.session_state[key_suffix]),
            step=float(step),
            key=f"{key_suffix}_input",
            on_change=update_from_input,
            label_visibility="collapsed"
        )
    
    return st.session_state[key_suffix]


with st.sidebar:
    st.header("Parameters")

    Type = st.selectbox(
        "**Option type**",
        ("Call", "Put")
    )

    Direction = st.selectbox(
        "**Long or Short ?**",
        ("Long", "Short")
    )

    S = input_synchro('Spot ($S$)', 0.0, 200.0, 100.0, 1.0, 'spot')
    K = input_synchro('Strike ($K$)', 0.0, 200.0, 100.0, 1.0, 'strike')
    V = input_synchro('Volatility $\sigma$ (%)', 0.0, 100.0, 20.0, 0.5, 'vol')
    
    Maturity_choice = st.selectbox(
        "**Time frequency**",
        ("Years", "Months", "Days", "Custom"), index=1
    )

    if Maturity_choice == "Years":
        Maturity = st.slider('**Maturity (Years)**', 0.0, 15.0, 1.0, 0.25)
    elif Maturity_choice == "Months":
        Maturity = st.slider('**Maturity (Months)**', 0.0, 60.0, 3.0, 1.0) / 12 
    elif Maturity_choice == "Days":
        Maturity = st.slider('**Maturity (Days)**', 0.0, 360.0, 30.0, 1.0) / 365
    elif Maturity_choice == "Custom":
        today = dt.date.today()
        date_exp = st.date_input(
            '**Maturity Date**',
            value=today + dt.timedelta(days=365),
            min_value=today + dt.timedelta(days=1),
            max_value=today + dt.timedelta(days=15*365)
        )
        Maturity = (date_exp - today).days / 365
    
    R = input_synchro('Interest rate $r$ (%)', 0.0, 20.0, 3.0, 0.1, 'rate')
    D = input_synchro('Dividends $q$ (%)', 0.0, 20.0, 0.0, 0.1, 'div')



st.title("Option strategies and Greeks dashboard")

col_selection, col_vide = st.columns([1, 3])
with col_selection:
    Premium = st.selectbox("Display Payoff with Premium?", ("Yes", "No"), index=0)

st.info(f"Paramètres actuels : S={S}, K={K}, Vol={V}, T={Maturity:.2f}, r={R}, q={D}")