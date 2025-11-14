import pandas as pd
import numpy as np
import altair as alt

astro_url = "https://drive.google.com/uc?export=download&id=1hmZY1_fJ157l9VVV62ewg6NDCOU2WfUp"
tsne_url = "https://drive.google.com/uc?export=download&id=1cNg0Z0xVn7l0t0BM1yZjz_lNyg_pAaEm"

df_abs = pd.read_csv(astro_url)
df_rel = pd.read_csv(tsne_url)

df_abs['Absolute Growth'] = df_abs['2024 Count'] - df_abs['2023 Count']
df_rel['Relative Growth'] = df_rel['Percent Change']

abs_min = df_abs['Absolute Growth'].min()
abs_max = df_abs['Absolute Growth'].max()

rel_min = df_rel['Relative Growth'].min()
rel_max = df_rel['Relative Growth'].max()

abs_zero_pos = (0 - abs_min) / (abs_max - abs_min)
rel_range = rel_max - rel_min
rel_zero_raw = rel_min + rel_range * abs_zero_pos

chart_abs = (
    alt.Chart(df_abs)
    .mark_bar()
    .encode(
        x=alt.X("Absolute Growth:Q", title="Absolute Growth"),
        y=alt.Y("Topic:N", sort="-x"),
        color=alt.Color("Absolute Growth:Q", scale=alt.Scale(scheme="redpurpleblue"))
    )
    .properties(width=350, height=500)
)

chart_rel = (
    alt.Chart(df_rel)
    .mark_bar()
    .encode(
        x=alt.X(
            "Relative Growth:Q",
            title="Relative Growth (%)",
            scale=alt.Scale(domain=[rel_min, rel_max])
        ),
        y=alt.Y("Topic:N", sort="-x"),
        color=alt.Color("Relative Growth:Q", scale=alt.Scale(scheme="redpurpleblue"))
    )
    .properties(width=350, height=500)
)

(chart_abs | chart_rel).resolve_scale(y='shared')
