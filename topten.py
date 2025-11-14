'''
good code
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
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))
df["TopicName"] = df["TopicName"].apply(lambda x: x if len(x) <= 50 else x[:47] + "...")

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
        
    pct_changes = []
    for i in range(1, len(counts)):
        current_count = counts[i]
        previous_count = counts[i-1]
        
        if previous_count == 0:
            pct_changes.append(0.0) 
        else:
            pct_change = (current_count - previous_count) / previous_count
            pct_changes.append(pct_change)
            
    if not pct_changes:
        return 0.0

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

st.title("Absolute & Relative Growth of Top 20 Topics")

plot_melt = plot_df.melt(
    id_vars="TopicName",
    value_vars=["AbsoluteGrowth", "RelativeGrowthRate"],
    var_name="GrowthType",
    value_name="Value"
)

ordered_topics = plot_df["TopicName"].tolist()

base = alt.Chart(plot_melt).encode(
    x=alt.X(
        "TopicName:N",
        sort=ordered_topics,
        axis=alt.Axis(labelAngle=-40)
    ),
    xOffset="GrowthType:N",
    color=alt.Color(
        "GrowthType:N",
        legend=alt.Legend(title="Growth Type"),
        scale=alt.Scale(
            domain=["AbsoluteGrowth", "RelativeGrowthRate"],
            range=["#4C78A8", "#54A24B"]
        )
    ),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("GrowthType:N", title="Type"),
        alt.Tooltip("Value:Q", title="Value", format=".1f")
    ]
).properties(
    title="Absolute & Relative Growth for Topics with Greatest Increase and Decline"
)

bars_abs = base.transform_filter(
    alt.datum.GrowthType == "AbsoluteGrowth"
).mark_bar().encode(
    y=alt.Y(
        "Value:Q",
        axis=alt.Axis(title="Absolute Growth (Δ abstracts)"),
        scale=alt.Scale(zero=True)
    ),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("Value:Q", title="Absolute Growth", format=",.1f")
    ]
)

bars_rel = base.transform_filter(
    alt.datum.GrowthType == "RelativeGrowthRate"
).mark_bar().encode(
    y=alt.Y(
        "Value:Q",
        axis=alt.Axis(title="Relative Growth (Avg Annual % Change)", orient="right", format=".0%"),
        scale=alt.Scale(zero=True)
    ),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("Value:Q", title="Relative Growth (Avg Annual)", format=".1%")
    ]
)

final_chart = (
    alt.layer(bars_abs, bars_rel)
    .resolve_scale(y="independent")
    .properties(width=1000, height=500)
)

st.altair_chart(final_chart, use_container_width=True)
'''

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
# --- FIX APPLIED HERE ---
data["Years"] = data["Years"].fillna(0).astype(int) 
data = data.rename(columns={"Years": "Year"})
# ------------------------

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
df["TopicName"] = df["TopicName"].fillna("Topic " + df["Topic (Post Forced)"].astype(str))
df["TopicName"] = df["TopicName"].apply(lambda x: x if len(x) <= 50 else x[:47] + "...")

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
        
    pct_changes = []
    for i in range(1, len(counts)):
        current_count = counts[i]
        previous_count = counts[i-1]
        
        if previous_count == 0:
            pct_changes.append(0.0) 
        else:
            pct_change = (current_count - previous_count) / previous_count
            pct_changes.append(pct_change)
            
    if not pct_changes:
        return 0.0

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

st.title("Absolute & Relative Growth of Top 20 Topics")

plot_melt = plot_df.melt(
    id_vars="TopicName",
    value_vars=["AbsoluteGrowth", "RelativeGrowthRate"],
    var_name="GrowthType",
    value_name="Value"
)

ordered_topics = plot_df["TopicName"].tolist()

abs_max = plot_df["AbsoluteGrowth"].abs().max()
rel_max = plot_df["RelativeGrowthRate"].abs().max()

base = alt.Chart(plot_melt).properties(
    title="Absolute & Relative Growth for Topics with Greatest Increase and Decline"
)

common_encodings = dict(
    x=alt.X(
        "TopicName:N",
        sort=ordered_topics,
        axis=alt.Axis(labelAngle=-40, title="Topic Name")
    ),
    color=alt.Color(
        "GrowthType:N",
        legend=alt.Legend(title="Growth Type"),
        scale=alt.Scale(
            domain=["AbsoluteGrowth", "RelativeGrowthRate"],
            range=["#4C78A8", "#54A24B"]
        )
    ),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("GrowthType:N", title="Type"),
        alt.Tooltip("Value:Q", title="Value", format=".1f")
    ]
)

bars_abs = base.encode(
    **common_encodings,
    y=alt.Y(
        "Value:Q",
        axis=alt.Axis(title="Absolute Growth (Δ abstracts)"),
        scale=alt.Scale(domain=[-abs_max, abs_max]) 
    ),
    xOffset=alt.XOffset("GrowthType:N"),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("Value:Q", title="Absolute Growth", format=",.1f")
    ]
).transform_filter(
    alt.datum.GrowthType == "AbsoluteGrowth"
).mark_bar()

bars_rel = base.encode(
    **common_encodings,
    y=alt.Y(
        "Value:Q",
        axis=alt.Axis(title="Relative Growth (Avg Annual % Change)", orient="right", format=".0%"),
        scale=alt.Scale(domain=[-rel_max, rel_max])
    ),
    xOffset=alt.XOffset("GrowthType:N"),
    tooltip=[
        alt.Tooltip("TopicName:N", title="Topic"),
        alt.Tooltip("Value:Q", title="Relative Growth (Avg Annual)", format=".1%")
    ]
).transform_filter(
    alt.datum.GrowthType == "RelativeGrowthRate"
).mark_bar()

final_chart = (
    alt.layer(bars_abs, bars_rel)
    .resolve_scale(y="independent")
    .properties(width=1000, height=500)
)

st.altair_chart(final_chart, use_container_width=True)
