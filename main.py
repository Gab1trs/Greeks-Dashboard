import streamlit as st
import datetime as dt
import numpy as np
import pandas as pd
from scipy.stats import norm

st.set_page_config(layout="wide", page_title="Option Dashboard")

if 'legs' not in st.session_state:
    st.session_state.legs = [
        {'strike': 100.0, 'vol': 20.0, 'type': 'Call', 'side': 'Long', 'maturity': 3.0/12.0, 'unit': 'Months', 'quantity': 1, 'premium': 0.0}
    ]

def input_synchro(label, min_val, max_val, default_val, step, key_suffix):
    if key_suffix not in st.session_state:
        st.session_state[key_suffix] = default_val

    def update_from_slider():
        current_value = st.session_state[f'{key_suffix}_slider']
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

    S = input_synchro('Spot ($S$)', 0.0, 200.0, 100.0, 1.0, 'spot')
    R = input_synchro('Interest rate $r$ (%)', 0.0, 20.0, 3.0, 0.1, 'rate')
    D = input_synchro('Dividends $q$ (%)', 0.0, 20.0, 0.0, 0.1, 'div')

    st.header("Positions")

    def update_unit_callback(i):
        st.session_state.legs[i]['unit'] = st.session_state[f'unit_select_{i}']

    for i, leg in enumerate(st.session_state.legs):
        with st.expander(f"Leg #{i+1}", expanded=True):
            
            if st.button("Delete leg", key=f"del_{i}"):
                st.session_state.legs.pop(i)
                st.rerun()

            c1, c2 = st.columns(2)
            with c1:
                Type = st.selectbox(
                    "**Option type**",
                    ("Call", "Put"),
                    key=f'type_{i}'
                )
            with c2:
                Side = st.selectbox(
                    "**Long or Short ?**",
                    ("Long", "Short"),
                    key=f'side_{i}'
                )

            c3, c4 = st.columns(2)
            with c3:
                Quantity = st.number_input("Quantity",
                    1.0,
                    key=f'quantity_{i}'
                )

            K = input_synchro('Strike ($K$)', 0.0, 200.0, leg['strike'], 1.0, key_suffix=f'strike_{i}')
            V = input_synchro('Volatility $\sigma$ (%)', 0.0, 100.0, leg['vol'], 0.5, key_suffix=f'vol_{i}')
            
            T_years_ref = leg.get('maturity', 1.0)
            current_unit = leg.get('unit', 'Years')
            units = ["Years", "Months", "Days", "Custom"]
            idx_unit = units.index(current_unit) if current_unit in units else 0

            Maturity_choice = st.selectbox(
                "Time unit", 
                units, 
                index=idx_unit, 
                key=f'unit_select_{i}',
                on_change=update_unit_callback, args=(i,) 
            )


            MAX_YEARS = 15.0
            MAX_MONTHS = 30.0    
            MAX_DAYS = 365.0 

            if Maturity_choice == "Years":
                val_calc = T_years_ref
                safe_val = min(val_calc, MAX_YEARS)
                
                Maturity_years = input_synchro(
                    '**Maturity (Years)**', 0.1, MAX_YEARS, 
                    round(safe_val, 3), 
                    0.25, key_suffix=f'maturity_years_{i}'
                )
                st.session_state.legs[i]['maturity'] = Maturity_years
            
            elif Maturity_choice == "Months":
                val_calc = T_years_ref * 12
                safe_val = min(val_calc, MAX_MONTHS)

                Maturity_months = input_synchro(
                    '**Maturity (Months)**', 1.0, MAX_MONTHS, 
                    round(safe_val, 1), 
                    1.0, key_suffix=f'maturity_months_{i}'
                )
                st.session_state.legs[i]['maturity'] = Maturity_months / 12.0
            
            elif Maturity_choice == "Days":
                val_calc = T_years_ref * 365
                safe_val = min(val_calc, MAX_DAYS)

                Maturity_days = input_synchro(
                    '**Maturity (Days)**', 1.0, MAX_DAYS, 
                    int(safe_val), 
                    1.0, key_suffix=f'maturity_days_{i}'
                )
                st.session_state.legs[i]['maturity'] = Maturity_days / 365.0
            
            elif Maturity_choice == "Custom":
                today = dt.date.today()
                target_date = today + dt.timedelta(days=int(T_years_ref * 365))
                max_date = today + dt.timedelta(days=15*365)
                safe_date = min(target_date, max_date)

                date_exp = st.date_input(
                    '**Maturity Date**',
                    value=safe_date,
                    min_value=today + dt.timedelta(days=1),
                    max_value=max_date,
                    key=f'maturity_custom_{i}'
                )
                st.session_state.legs[i]['maturity'] = (date_exp - today).days / 365.0

            
            st.session_state.legs[i]['strike'] = K
            st.session_state.legs[i]['vol'] = V
            st.session_state.legs[i]['type'] = Type
            st.session_state.legs[i]['side'] = Side
            st.session_state.legs[i]['quantity'] = Quantity
    
    
    if st.button("Add leg"):
        last_maturity = st.session_state.legs[-1]['maturity'] if st.session_state.legs else 3.0/12.0
        new_leg = {'strike': 100.0, 'vol': 20.0, 'type': 'Call', 'side':'Long', 'maturity': last_maturity, 'quantity': 1.0}
        st.session_state.legs.append(new_leg)
        st.rerun()


st.title("Option strategies and Greeks dashboard")

col_selection, col_empty = st.columns([1,3])
with col_selection:
    premium_choice = st.selectbox("Display Payoff with Premium?", ("Yes", "No"), index=1)

st.header("Payoff")

premium=0
for leg in st.session_state.legs:
    d1=(np.log(S/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    d2=d1-((leg['vol']/100)*np.sqrt(leg['maturity']))
    Call=S*np.exp(-D/100*leg['maturity'])*norm.cdf(d1)-leg['strike']*np.exp(-R/100*leg['maturity'])*norm.cdf(d2)
    Put=leg['strike']*np.exp(-R/100*leg['maturity'])*norm.cdf(-d2)-S*np.exp(-D/100*leg['maturity'])*norm.cdf(-d1)

    if leg['side']=='Long':
        if leg['type']=="Call":
            premium+=Call
        if leg['type']=="Put":
            premium+=Put

    if leg['side']=='Short':
        if leg['type']=="Call":
            premium-=Call
        if leg['type']=="Put":
            premium-=Put

#payoff
payoff = pd.DataFrame()
payoff['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    if leg['type']=="Call":
        intrinsic=np.maximum((payoff['spot']-leg['strike']), 0)
    if leg['type']=="Put":
        intrinsic=np.maximum((leg['strike'])-payoff['spot'], 0)

    direction=1 if leg['side']=='Long' else -1

    payoff[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in payoff.columns if c != 'spot']
payoff["Total Payoff"] = payoff[cols_to_sum].sum(axis=1)

if premium_choice=='Yes':
    payoff["P&L Net"] = payoff["Total Payoff"] - premium

chart_data = payoff.set_index('spot')
if premium_choice == 'Yes':
    col_show = "P&L Net" 
else:
    col_show = "Total Payoff"
st.line_chart(chart_data[col_show])

#delta
delta = pd.DataFrame()
delta['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    d1=(np.log(delta['spot']/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    if leg['type']=="Call":
        intrinsic=np.exp(-D*leg['maturity'])*norm.cdf(d1)
    if leg['type']=="Put":
        intrinsic=np.exp(-D*leg['maturity'])*norm.cdf(-d1)

    direction=1 if leg['side']=='Long' else -1

    delta[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in delta.columns if c != 'spot']
delta["Total Delta"] = delta[cols_to_sum].sum(axis=1)
chart_data = delta.set_index('spot')

c1, c2 = st.columns(2)

with c1:
    st.header("Delta")
    st.line_chart(chart_data["Total Delta"])

#gamma
gamma = pd.DataFrame()
gamma['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    d1=(np.log(gamma['spot']/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    
    intrinsic=(np.exp(-D*leg['maturity'])*norm.pdf(d1))/(gamma['spot']*leg['vol']*np.sqrt(leg['maturity']))

    direction=1 if leg['side']=='Long' else -1

    gamma[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in gamma.columns if c != 'spot']
gamma["Total Gamma"] = gamma[cols_to_sum].sum(axis=1)
chart_data = gamma.set_index('spot')

with c2:
    st.header("Gamma")
    st.line_chart(chart_data["Total Gamma"])

#vega
vega = pd.DataFrame()
vega['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    d1=(np.log(vega['spot']/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    
    intrinsic=vega['spot']*np.exp(-D*leg['maturity'])*norm.pdf(d1)*np.sqrt(leg['maturity'])

    direction=1 if leg['side']=='Long' else -1

    vega[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in vega.columns if c != 'spot']
vega["Total Vega"] = vega[cols_to_sum].sum(axis=1)/100
chart_data = vega.set_index('spot')

c3, c4 = st.columns(2)

with c3:
    st.header("Vega")
    st.line_chart(chart_data["Total Vega"])

#theta
theta = pd.DataFrame()
theta['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    d1=(np.log(theta['spot']/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    d2=d1-((leg['vol']/100)*np.sqrt(leg['maturity']))
    A=(-(theta['spot']*np.exp(-D*leg['maturity'])*norm.pdf(d1)*leg['vol']))/(2*np.sqrt(leg['maturity']))

    if leg['type']=="Call":
        intrinsic=A-R*leg['strike']*np.exp(-R*leg['maturity'])*norm.cdf(d2)+D*theta['spot']*np.exp(-D*leg['maturity'])*norm.cdf(d1)
    if leg['type']=="Put":
        intrinsic=A+R*leg['strike']*np.exp(-R*leg['maturity'])*norm.cdf(-d2)-D*theta['spot']*np.exp(-D*leg['maturity'])*norm.cdf(-d1)

    direction=1 if leg['side']=='Long' else -1

    theta[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in theta.columns if c != 'spot']
theta["Total Theta"] = theta[cols_to_sum].sum(axis=1)/365
chart_data = theta.set_index('spot')

with c4:
    st.header("Theta")
    st.line_chart(chart_data["Total Theta"])

#rho
rho = pd.DataFrame()
rho['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    d1=(np.log(rho['spot']/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    d2=d1-((leg['vol']/100)*np.sqrt(leg['maturity']))

    if leg['type']=="Call":
        intrinsic=leg['strike']*leg['maturity']*np.exp(-R*leg['maturity'])*norm.cdf(d2)
    if leg['type']=="Put":
        intrinsic=-leg['strike']*leg['maturity']*np.exp(-R*leg['maturity'])*norm.cdf(-d2)

    direction=1 if leg['side']=='Long' else -1

    rho[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in rho.columns if c != 'spot']
rho["Total Rho"] = rho[cols_to_sum].sum(axis=1)/100
chart_data = rho.set_index('spot')

c5,c6=st.columns(2)

with c5:
    st.header("Rho")
    st.line_chart(chart_data["Total Rho"])

#phi
phi = pd.DataFrame()
phi['spot']=np.linspace(0,200,200)

for i, leg in enumerate(st.session_state.legs):
    d1=(np.log(phi['spot']/leg['strike'])+((R/100-D/100+((leg['vol']/100)**2/2))*leg['maturity']))/((leg['vol']/100)*np.sqrt(leg['maturity']))
    d2=d1-((leg['vol']/100)*np.sqrt(leg['maturity']))

    if leg['type']=="Call":
        intrinsic=-leg['maturity']*phi['spot']*np.exp(-D*leg['maturity'])*norm.cdf(d1)
    if leg['type']=="Put":
        intrinsic=leg['maturity']*phi['spot']*np.exp(-D*leg['maturity'])*norm.cdf(-d1)

    direction=1 if leg['side']=='Long' else -1

    phi[f'leg{i+1}']=intrinsic*direction*leg['quantity']

cols_to_sum = [c for c in phi.columns if c != 'spot']
phi["Total Phi"] = phi[cols_to_sum].sum(axis=1)/100
chart_data = phi.set_index('spot')

with c6:
    st.header("Phi")
    st.line_chart(chart_data["Total Phi"])