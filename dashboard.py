import os
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd
import useful_functions as uf

file_path = "hansard_malaysia/sessions/session_15"

# load all the csv file
mp = pd.read_csv(file_path + "/mp_session_15.csv")
attendance = pd.read_csv(file_path + "/attendance_session_15.csv")
summary = pd.read_csv(file_path + "/summary_session_15.csv")
mp_riuh = pd.read_csv(file_path + "/riuh_stats_session_15.csv")
mp_kelakar = pd.read_csv(file_path + "/gelak_stats_session_15.csv")
extra_info = pd.read_csv('hansard_malaysia/work_draft/filtered.csv')

df = mp.drop(["seat_code", "state", "seat"], axis=1).merge(attendance, on="mp", how="inner")

st.title("Parlimen Malaysia Overview")

# list of important column
mp_kelakar["coalition"] = uf.get_coalition(mp_kelakar)
mp_riuh["coalition"] = uf.get_coalition(mp_riuh)
df["coalition"] = uf.get_coalition(df)

# list of dropped column
to_drop_kelakar = [i for i in mp_kelakar.columns[5:-2]]
to_drop = [i for i in attendance.columns[5:-2]]

# figure
fig_1 = px.strip(mp_kelakar.drop(to_drop_kelakar, axis=1), x="total_gelak", y="coalition",
               labels={
                   "total_gelak": "Buat dewan ketawa",
                   "coalition": "Coalition"
               },
               title="Punca dewan ketawa",
               hover_name="mp",
               hover_data={
                   "coalition": False
               })

fig_2 = px.strip(mp_riuh.drop(to_drop_kelakar, axis=1), x="total_riuh", y="coalition",
               labels={
                   "total_riuh": "Buat dewan riuh",
                   "coalition": "Coalition"
               },
               title="Punca dewan riuh", 
               hover_name="mp",
               hover_data={
                   "coalition": False
               })

fig_3 = px.strip(df.drop(to_drop, axis=1), x="total", y="coalition",
               labels={
                   "total": "Kehadiran",
                   "coalition": "Coalition",
                   "current_party": "Party"
               },
               title="Kehadiran", 
               hover_name="mp",
               hover_data={
                   "coalition": False,
                   "current_party": True
               })


st.plotly_chart(fig_3)

# party = st.selectbox("Choose Party", ['UMNO', 'MIC', 'MCA', 'PBRS', 'PKR', 'DAP',
#                                'AMANAH', 'MUDA', 'UPKO', 'PAS', 'BERSATU'])

tab1, tab2 = st.tabs(["Dewan Gelak", "Dewan riuh"])

with tab1:
    st.plotly_chart(fig_1, use_container_width=True)

with tab2:
    st.plotly_chart(fig_2, use_container_width=True)

# pie plot

gender_count = extra_info['gender'].value_counts()

# Creating a pie chart
fig = px.pie(names=gender_count.index, values=gender_count.values, title='Gender')

st.plotly_chart(fig)

extra_info = extra_info.rename(columns={'constituency_seat_no': 'seat_code'})
extra_info = extra_info.merge(mp, on='seat_code', how='outer')
group_data = extra_info.groupby('current_party')['gender'].value_counts().reset_index(name='count')

# Creating a bar chart
fig = px.bar(group_data, x='current_party', y='count', color='gender', barmode='group',
             title='Gender Distribution by Party')

st.plotly_chart(fig)