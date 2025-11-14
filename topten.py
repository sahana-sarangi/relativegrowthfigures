import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

st.set_page_config(layout="wide", page_title="Absolute and Relative Growth")

astro_url = "https://drive.google.com/uc?export=download&id=1hmZY1_fJ157l9VVV62ewg6NDCOU2WfUp"
tsne_url = "https://drive.google.com/uc?export=download&id=1aQ6ZEPjk6PP0JonYq5aVVSjP5i3zFz0F"

astro_df = pd.read_csv(astro_url)
tsne_df = pd.read_csv(tsne_url)

astro_df['Topic'] = astro_df['Topic'].astype(str)
astro_df['1990'] = pd.to_numeric(astro_df['1990'], errors='coerce').fillna(0)
astro_df['2020'] = pd.to_numeric(astro_df['2020'], errors='coerce').fillna(0)
astro_df['Absolute Growth'] = astro_df['2020'] - astro_df['1990']
astro_df['Relative Growth'] = np.where(astro_df['1990'] == 0, np.nan, astro_df['Absolute Growth'] / astro_df['1990'])

top_abs_increase = astro_df.nlargest(10, 'Absolute Growth')
top_abs_decrease = astro_df.nsmallest(10, 'Absolute Growth')
subset_df = pd.concat([top_abs_increase, top_abs_decrease])

subset_df = pd.melt(
    subset_df,
    id_vars=['Topic'],
    value_vars=['Absolute Growth', 'Relative Growth'],
    var_name='Metric',
    value_name='Value'
)

subset_df['Metric'] = subset_df['Metric'].replace({
    'Absolute Growth': 'Absolute Growth',
    'Relative Growth': 'Relative Growth (%)'
})

subset_df['Value'] = subset_df.apply(
    lambda row: row['Value'] * 100 if row['Metric'] == 'Relative Growth (%)' else row['Value'],
    axis=1
)

abs_min = subset_df[subset_df['Metric'] == 'Absolute Growth']['Value'].min()
abs_max = subset_df[subset_df['Metric'] == 'Absolute Growth']['Value'].max()

rel_min = subset_df[subset_df['Metric'] == 'Relative Growth (%)']['Value'].min()
rel_max = subset_df[subset_df['Metric'] == 'Relative Growth (%)']['Value'].max()

primary_zero_position = (0 - abs_min) / (abs_max - abs_min)
relative_zero_value = rel_min + primary_zero_position * (rel_max - rel_min)

scale_abs = alt.Scale(domain=[abs_min, abs_max])
scale_rel = alt.Scale(domain=[rel_min, rel_max])

color_scale = alt.Scale(
    domain=['Absolute Growth', 'Relative Growth, year to year'],
    range=['#4C78A8', '#E45756']
)

base = alt.Chart(subset_df).encode(
    x=alt.X('Topic:N', sort='-y', axis=alt.Axis(labelAngle=-40))
)

abs_bars = base.transform_filter(
    alt.datum.Metric == 'Absolute Growth'
).mark_bar().encode(
    y=alt.Y('Value:Q', scale=scale_abs, axis=alt.Axis(title='Absolute Growth')),
    color=alt.Color('Metric:N', scale=color_scale, legend=alt.Legend(title="Metric"))
)

rel_line = base.transform_filter(
    alt.datum.Metric == 'Relative Growth (%)'
).mark_line(size=3).encode(
    y=alt.Y('Value:Q', scale=scale_rel, axis=alt.Axis(title='Relative Growth (%)')),
    color=alt.Color('Metric:N', scale=color_scale, legend=None)
)

rel_points = base.transform_filter(
    alt.datum.Metric == 'Relative Growth (%)'
).mark_point(size=60).encode(
    y=alt.Y('Value:Q', scale=scale_rel),
    color=alt.Color('Metric:N', scale=color_scale, legend=None)
)

chart = alt.layer(abs_bars, rel_line, rel_points).resolve_scale(
    y='independent'
).properties(
    width=900,
    height=500,
    title='Absolute and Relative Growth of Top Increasing and Decreasing'
)

st.altair_chart(chart, use_container_width=True)
