import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="Absolute Growth - top 10s")

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
df = pd.merge(
    df,
    bt60_names[["AbstractTitle", "GPT_Names", "Topic (Post Forced)"]],
    on=["AbstractTitle", "Topic (Post Forced)"],
    how="left"
)

df = df.rename(columns={"GPT_Names": "TopicName"})
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))
df["TopicName"] = df["TopicName"].apply(lambda x: x if len(x) <= 50 else x[:47] + "...")

topic_growth = (
    df.groupby(["TopicName", "Year"])
    .size()
    .reset_index(name="AbstractsPerYear")
)

def calc_absolute_growth(g):
    g = g.sort_values("Year")
    counts = g["AbstractsPerYear"].values
    if len(counts) < 2:
        return 0.0
    deltas = counts[1:] - counts[:-1]
    return np.mean(deltas)

absolute_growth = (
    topic_growth.groupby("TopicName")
    .apply(calc_absolute_growth)
    .reset_index(name="AbsoluteGrowth")
)


top_growth = absolute_growth.sort_values("AbsoluteGrowth", ascending=False).head(10)
top_decline = absolute_growth.sort_values("AbsoluteGrowth").head(10)

bar_data = pd.concat([top_growth, top_decline])

bar_data["Type"] = bar_data["AbsoluteGrowth"].apply(lambda x: "Growth" if x >= 0 else "Decline")
bar_data["AbsoluteGrowthLabel"] = bar_data["AbsoluteGrowth"].round(1).astype(str)

bar_chart = alt.Chart(bar_data).mark_bar().encode(
    x=alt.X('TopicName:N', sort=alt.SortField(field="AbsoluteGrowth", order="descending"), title='Topic'),
    y=alt.Y('AbsoluteGrowth:Q', title='Average # Abstracts Change per Year'),
    color=alt.Color('Type:N', scale=alt.Scale(domain=["Growth", "Decline"], range=["#d73027", "#4575b4"])),
    tooltip=[
        alt.Tooltip('TopicName:N', title='Topic'),
        alt.Tooltip('AbsoluteGrowth:Q', title='Avg Δ Abstracts/Year', format=".2f")
    ]
)

text = bar_chart.mark_text(
    dy=-5,
    color='black',
    size=12
).encode(
    text='AbsoluteGrowthLabel:N'
)

final_chart = (bar_chart + text).properties(width=1000, height=500, title="Absolute Growth Bar Graph - top 10s")

st.altair_chart(final_chart, use_container_width=True)
