import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="Absolute Growth Horizontal Bar Chart")

astro_url = "https://drive.google.com/uc?export=download&id=1hmZY1_fJ157l9VVV62ewg6NDCOU2WfUp"
tsne_url = "https://drive.google.com/uc?export=download&id=1hWBkhr2iQQm8hP3oa8kB_5Org40MND1s"
names_url = "https://drive.google.com/uc?export=download&id=1_SxyudGo4_zOa-pWvd3feXJjK_cELCYz"

data = pd.read_csv(astro_url)
data['years'] = data['years'].fillna(0)
data['years'] = data['years'].astype(int)
data = data.rename(columns={"years": "Year"})

df = pd.read_csv(tsne_url, encoding="utf8")
df = df.rename(columns={
    "Topic Name (Post Forced)": "Cluster",
    "title": "AbstractTitle",
})
df["Topic (Post Forced)"] = df["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(df, data, on='AbstractTitle')
bt60_names = pd.read_csv(names_url)
bt60_names = bt60_names.rename(columns={"title": "AbstractTitle"})
bt60_names["Topic (Post Forced)"] = bt60_names["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(df, bt60_names[["AbstractTitle", "GPT_Names", "Topic (Post Forced)"]],
              on=["AbstractTitle", "Topic (Post Forced)"], how="left")

df = df.rename(columns={"GPT_Names": "TopicName"})
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))

topic_growth = df.groupby(["TopicName", "Year"]).size().reset_index(name="AbstractsPerYear")
def calc_total_change(g):
    g = g.sort_values("Year")
    return g["AbstractsPerYear"].iloc[-1] - g["AbstractsPerYear"].iloc[0]
total_change = topic_growth.groupby("TopicName").apply(calc_total_change).reset_index(name="TotalChange")

bar_data = total_change.sort_values("TotalChange", ascending=False).reset_index(drop=True)
bar_data["Label"] = bar_data["TotalChange"].astype(int).astype(str)
bar_data["OrderRank"] = bar_data.index

bar_chart = alt.Chart(bar_data).mark_bar().encode(
    y=alt.Y('TopicName:N', sort=alt.SortField('TotalChange', order='descending'), title='Topic'),
    x=alt.X('TotalChange:Q', title='Total Abstract Change'),
    color=alt.Color('OrderRank:O', scale=alt.Scale(scheme='rainbow'), legend=None),
    tooltip=[alt.Tooltip('TopicName:N', title='Topic'),
             alt.Tooltip('TotalChange:Q', title='Total Change')]
)

labels = alt.Chart(bar_data).mark_text(
    align='left',
    dx=3,
    color='black'
).encode(
    y=alt.Y('TopicName:N', sort=alt.SortField('TotalChange', order='descending')),
    x='TotalChange:Q',
    text='Label:N'
)

final_chart = (bar_chart + labels).properties(
    width=900,
    height=600,
    title="Total Abstract Change per Topic (Most Growth → Most Decline)"
)

st.altair_chart(final_chart, use_container_width=True)
