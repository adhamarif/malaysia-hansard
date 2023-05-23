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



tab1, tab2 = st.tabs(["Dewan Gelak", "Dewan riuh"])

with tab1:
    st.plotly_chart(fig_1, use_container_width=True)

with tab2:
    st.plotly_chart(fig_2, use_container_width=True)









# df = mp.drop(["seat_code", "state", "seat"], axis=1).merge(attendance, on="mp", how="inner")
# n_session = len(df.drop("total", axis=1).iloc[:, 4:].columns)
# df["attendance_%"]=round((df["total"] / n_session * 100),2)
# party_counts = df["current_party"].value_counts().sort_values()


# fig, ax = plt.subplots(figsize=(5,5))

# ax.barh(party_counts.index, party_counts)
# # set the axis labels and title
# ax.set_xlabel('Number of Members')
# #ax.set_ylabel('Party')
# ax.set_title('Party Member in Parliament')

# st.pyplot(fig)

# attendance_party = df[["current_party","attendance_%"]].groupby("current_party").mean().sort_values(by="attendance_%")

