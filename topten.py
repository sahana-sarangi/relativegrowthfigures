import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="Absolute & Relative Growth of Topics")
alt.data_transformers.disable_max_rows()

def add_leading_zeroes(x):
    if pd.isna(x):
        x = 0
    return "{:02d}".format(int(x))

astro_url = "https://drive.google.com/uc?export=download&id=1hmZY1_fJ157l9VVV62ewg6NDCOU2WfUp"
tsne_url = "https://drive.google.com/uc?export=download&id=1hWBkhr2iQQm8hP3oa8kB_5Org40MND1s"
names_url = "https://drive.google.com/uc?export=download&id=1_SxyudGo4_zOa-pWvd3feXJjK_cELCYz"

data = pd.read_csv(astro_url, index_col=0)
data["years"] = data["years"].fillna(0).astype(int)
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

df = pd.merge(df, data, on=["AbstractTitle"], suffixes=("_df", None))
df = df.drop(columns=df.filter(regex="_df$").columns)
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
df["TopicName"] = df["TopicName"].fillna(
    "Topic " + df["Topic (Post Forced)"].astype(str)
)
df["TopicName"] = df["TopicName"].apply(
    lambda x: x if len(x) <= 50 else x[:47] + "..."
)

topic_year = (
    df.groupby(["TopicName", "Year"])
    .size()
    .reset_index(name="AbstractsPerYear")
)

def calc_relative_growth(g):
    g = g.sort_values("Year")
    counts = g["AbstractsPerYear"].values
    if len(counts) < 2:
        return 0.0
    pct_changes = (counts[1:] - counts[:-1]) / counts[:-1]
    return np.mean(pct_changes)

relative = (
    topic_year.groupby("TopicName")
    .apply(calc_relative_growth)
    .reset_index(name="RelativeGrowthRate")
)

absolute = (
    topic_year.sort_values("Year")
    .groupby("TopicName")
    .apply(lambda g: g["AbstractsPerYear"].iloc[-1] - g["AbstractsPerYear"].iloc[0])
    .reset_index(name="AbsoluteGrowth")
)

growth = absolute.merge(relative, on="TopicName", how="left")

top_inc = growth.nlargest(10, "AbsoluteGrowth")
top_dec = growth.nsmallest(10, "AbsoluteGrowth")

plot_df = pd.concat([top_inc, top_dec], ignore_index=True)
plot_df = plot_df.sort_values("AbsoluteGrowth", ascending=False)

st.title("Absolute Growth & Relative Growth of Top Topics")

base = alt.Chart(plot_df).encode(
    x=alt.X("TopicName:N", sort=None, axis=alt.Axis(labelAngle=-40)),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("AbsoluteGrowth:Q", title="Absolute Growth", format=","),
        alt.Tooltip("RelativeGrowthRate:Q", title="Relative Growth", format=".2%")
    ]
)

bars = base.mark_bar(color="#4C78A8", opacity=0.85).encode(
    y=alt.Y("AbsoluteGrowth:Q", axis=alt.Axis(title="Absolute Growth (Δ abstracts)"))
)

line = base.mark_line(
    color="#54A24B",
    strokeWidth=2,
    point=alt.OverlayMarkDef(filled=True, size=50)
).encode(
    y=alt.Y(
        "RelativeGrowthRate:Q",
        axis=alt.Axis(title="Relative Growth (Avg % per year)", orient="right", format=".0%"),
        scale=alt.Scale(zero=False)
    )
)

final_chart = (
    alt.layer(bars, line)
    .resolve_scale(y="independent")
    .properties(
        width=900,
        height=500,
        title="Top 10 Topics with Highest Increase and Decrease in Abstract Counts"
    )
)

st.altair_chart(final_chart, use_container_width=True)
