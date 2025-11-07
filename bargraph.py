import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="Absolute Growth Bar Chart")

astro_url = "https://drive.google.com/uc?export=download&id=1hmZY1_fJ157l9VVV62ewg6NDCOU2WfUp"
tsne_url = "https://drive.google.com/uc?export=download&id=1hWBkhr2iQQm8hP3oa8kB_5Org40MND1s"
names_url = "https://drive.google.com/uc?export=download&id=1_SxyudGo4_zOa-pWvd3feXJjK_cELCYz"

def add_leading_zeroes(x):
    if pd.isna(x):
        x = 0
    return "{:02d}".format(int(x))

data = pd.read_csv(astro_url)
data['years'] = data['years'].fillna(0)
data['years'] = data['years'].astype(int)
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
df["Cluster"] = df["Topic (Post Forced)"].apply(add_leading_zeroes)

bt60_names = pd.read_csv(names_url)
bt60_names = bt60_names.rename(columns={"title": "AbstractTitle"})
bt60_names["Topic (Post Forced)"] = bt60_names["Topic (Post Forced)"].fillna(0).astype(int)
df = pd.merge(
    df,
    bt60_names[["AbstractTitle", "GPT_Names", "Topic (Post Forced)"]],
    on=["AbstractTitle", "Topic (Post Forced)"], how="left"
)
df = df.rename(columns={"GPT_Names": "TopicName"})
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))
df["TopicName"] = df["TopicName"].apply(lambda x: x if len(x) <= 50 else x[:47]+"...")


topic_growth = df.groupby(["TopicName", "Year"]).size().reset_index(name="AbstractsPerYear")
def calc_total_change(g):
    g = g.sort_values("Year")
    return g["AbstractsPerYear"].iloc[-1] - g["AbstractsPerYear"].iloc[0]
total_change = topic_growth.groupby("TopicName").apply(calc_total_change).reset_index(name="TotalChange")


bar_data = total_change.sort_values("TotalChange", ascending=False).reset_index(drop=True)
bar_data["OrderRank"] = bar_data.index
bar_data["Label"] = bar_data["TotalChange"].astype(int).astype(str)


from matplotlib import cm
colors = [cm.rainbow(i/len(bar_data)) for i in range(len(bar_data))]
colors = [f"rgb({int(r*255)},{int(g*255)},{int(b*255)})" for r,g,b,_ in colors]
bar_data["Color"] = colors

bar_chart = alt.Chart(bar_data).mark_bar().encode(
    x=alt.X('OrderRank:O', title='Topics', axis=alt.Axis(labels=False, ticks=False)),
    y=alt.Y('TotalChange:Q', title='Total Abstract Change'),
    color=alt.Color('OrderRank:O', scale=alt.Scale(scheme='rainbow')),
    tooltip=[alt.Tooltip('TopicName:N', title='Topic'),
             alt.Tooltip('TotalChange:Q', title='Total Change')]
)



growth_text = alt.Chart(bar_data).mark_text(
    dy=-5, color='black', size=12
).encode(
    x='OrderRank:O',
    y='TotalChange:Q',
    text='Label:N'
)


topic_labels = alt.Chart(bar_data).mark_text(
    dy=10, color='black', size=12, angle=0, align='center'
).encode(
    x='OrderRank:O',
    y=alt.value(0),
    text='TopicName:N'
)

final_chart = (bar_chart + growth_text + topic_labels).properties(
    width=1200,
    height=500,
    title="Absolute Growth Bar Chart"
)

st.altair_chart(final_chart, use_container_width=True)
