import streamlit as st
import numpy as np
import datetime as dt
import pandas as pd
import plotly.express as px

# SETTINGS

# st.set_page_config(layout="wide")

# FUNCTIONS

def get_age(birthdate, date):
    age = date.year - birthdate.year - ((date.month, date.day) < (birthdate.month, birthdate.day))
    return age

def contribution(P, x, t, g0, r0):
    C = (P + x * (t + 1))/(1 + r0)**t
    C = np.around(C, -2).astype(int)
    return C

def capital(P, x, t, g0, r0):
    V = (P * (1 + g0)**t + x * ((1 + g0)**t).cumsum())/(1 + r0)**t
    V = np.around(V, -2).astype(int)
    return V

# LOGIC

today = dt.date.today()
initial_date = dt.date(1900, 1, 1)

st.header("Early Retirement App")

with st.sidebar:

    birthdate = st.date_input("Birthday", min_value=initial_date, max_value=today, value=dt.date(1986, 2, 5))

    current_age = get_age(birthdate, today)
    max_age = max(69, current_age) + 1

    nominal_real = st.radio("Correct for Inflation", ("nominal", "real"))

    if nominal_real == "real":
        r = st.slider("Annualized Expected Inflation (%)", 0.0, 10.0, 3.0, 0.1) / 100
        r0 = (1 + r) ** (1 / 12) - 1
    else:
        r0 = 0

colA1, colA2 = st.columns(2)

with colA1:
    P = st.slider("Initial Balance (k$)", 0, 500, 100, 10) * 1000

with colA2:
    g = st.slider("Annualized Expected ROI (%)", 0.0, 20.0, 6.0, 0.5) / 100
    g0 = (1 + g) ** (1 / 12) - 1

tab1, tab2, tab3 = st.tabs((
    "Retirement Age",
    "Monthly Contribution",
    "Cashflow at Retirement"
))

with tab1:

    x = st.slider("Monthly Contribution ($)", 0, 5000, 1000, 100)

    t = np.arange(0, (max_age - current_age)*12)

    C = contribution(P, x, t, g0, r0)
    V = capital(P, x, t, g0, r0)

    df = pd.DataFrame([t, C, V]).T
    df.columns = ["retirement age (years)", "contribution", "capital"]

    df = df[df["retirement age (years)"]%12 == 0]
    df["retirement age (years)"] = df["retirement age (years)"]/12 + current_age

    fig = px.line(
        df,
        x="retirement age (years)",
        y=["contribution", "capital"],
        labels=dict(value="$")
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:

    t_max = st.slider("Retirement Age (years)", current_age, max_age, current_age + int((max_age - current_age)/2), 1)
    t = np.arange((t_max - current_age) * 12)

    x_list = np.arange(0, 5000, 100)

    C_list, V_list = [], []
    for x_i in x_list:
        C = contribution(P, x, t, g0, r0)[-1]
        V = capital(P, x_i, t, g0, r0)[-1]
        C_list.append(C)
        V_list.append(V)

    df = pd.DataFrame([x_list, C_list, V_list]).T
    df.columns = ["monthly contribution ($)", "contribution", "capital"]

    fig = px.line(
        df,
        x="monthly contribution ($)",
        y=["contribution", "capital"],
        labels=dict(value="$")
    )

    st.plotly_chart(fig, use_container_width=True)

with tab3:

    colB1, colB2 = st.columns(2)

    with colB1:
        div = st.slider("Dividend Yield (%)", 0.0, 10.0, 5.0, 0.5) / 100

    with colB2:
        tax = st.slider("Tax on Capital Gains (%)", 0, 100, 30, 5) / 100

    V = capital(P, x, t, g0, r0)[-1]
    cashflow = int(np.around((V * div * (1 - tax))/12, -2))

    st.metric("Monthly Cashflow at Retirement", cashflow)