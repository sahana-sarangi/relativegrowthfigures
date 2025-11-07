import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="Top Growing and Declining Topics (Total Change)")

def add_leading_zeroes(x):
    if pd.isna(x):
        x = 0
    return "{:02d}".format(int(x))

astro_url = "https://drive.google.com/uc?export=download&id=1GySlfSGMIt0LZb_XCgP29DaqPL2aCISI"
tsne_url = "https://drive.google.com/uc?export=download&id=1AlqzyJQSxfK2MJGVdQriZfBtnGrzDzVS"
names_url = "https://drive.google.com/uc?export=download&id=1s6T-5KchhgOnoCX16aMYGtJ1_TiU_hqm"

data = pd.read_csv(astro_url, index_col=0)
data['years'] = data['years'].fillna(0)
data.years = data.years.astype(int)
data = data.rename(columns={"years": "Year"})

df = pd.read_csv(tsne_url, encoding="utf8")
df = df.rename(columns={
    "Topic Name (Post Forced)": "Cluster",
    "x": "TSNE-x",
    "y": "TSNE-y",
    "title": "AbstractTitle",
    "abstract": "Abstract"
})
df["Topic (Post Forced)"] = df["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(df, data, on=['AbstractTitle'], suffixes=("_df", None))
df = df.drop(columns=df.filter(regex="_df$").columns)
df['Index'] = np.arange(1, df.shape[0] + 1)
df["Cluster"] = df["Topic (Post Forced)"].apply(add_leading_zeroes)

bt60_names = pd.read_csv(names_url)
bt60_names = bt60_names.rename(columns={"title": "AbstractTitle"})
bt60_names["Topic (Post Forced)"] = bt60_names["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(df, bt60_names[["AbstractTitle", "GPT_Names", "Topic (Post Forced)"]],
              on=["AbstractTitle", "Topic (Post Forced)"], how="left")

df = df.rename(columns={"GPT_Names": "TopicName"})
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))
df["TopicName"] = df["TopicName"].apply(lambda x: x if len(x) <= 50 else x[:47] + "...")

topic_growth = df.groupby(["TopicName", "Year"]).size().reset_index(name="AbstractsPerYear")

def calc_total_change(g):
    g = g.sort_values("Year")
    return g["AbstractsPerYear"].iloc[-1] - g["AbstractsPerYear"].iloc[0]

total_change = topic_growth.groupby("TopicName").apply(calc_total_change).reset_index(name="TotalChange")

top_growth = total_change.sort_values("TotalChange", ascending=False).head(10)
top_decline = total_change.sort_values("TotalChange", ascending=True).head(10)

bar_data = pd.concat([top_growth, top_decline])
bar_data["Type"] = bar_data["TotalChange"].apply(lambda x: "Growth" if x >= 0 else "Decline")
bar_data["Label"] = bar_data["TotalChange"].round(0).astype(int).astype(str)

bar_data = bar_data.sort_values("TotalChange", ascending=False)
bar_data["Order"] = np.arange(len(bar_data))

bar_chart = alt.Chart(bar_data).mark_bar().encode(
    x=alt.X('TopicName:N', sort=bar_data["TopicName"].tolist(), title='Topic'),
    y=alt.Y('TotalChange:Q', title='Total Abstract Change'),
    color=alt.Color('Type:N', scale=alt.Scale(domain=["Growth", "Decline"], range=["#d73027", "#4575b4"])),
    tooltip=[alt.Tooltip('TopicName:N', title='Topic'),
             alt.Tooltip('TotalChange:Q', title='Total Change', format=".0f")]
)

growth_text = alt.Chart(bar_data[bar_data["Type"]=="Growth"]).mark_text(
    dy=-5, color='black', size=12
).encode(
    x='TopicName:N',
    y='TotalChange:Q',
    text='Label:N'
)

decline_text = alt.Chart(bar_data[bar_data["Type"]=="Decline"]).mark_text(
    dy=12, color='black', size=12
).encode(
    x='TopicName:N',
    y='TotalChange:Q',
    text='Label:N'
)

final_chart = (bar_chart + growth_text + decline_text).properties(
    width=1200,
    height=500,
    title="Top Growing and Declining Topics (Total Abstract Change)"
)

st.altair_chart(final_chart, use_container_width=True)
