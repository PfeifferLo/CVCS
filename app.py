# =========================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =========================================================

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from scipy.stats import pearsonr
import gspread
from google.oauth2.service_account import Credentials

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Unternehmensanalyse Österreich",
    layout="wide"
)

# =========================================================
# TITEL
# =========================================================

st.title("Unternehmensanalyse Österreich")

# =========================================================
# GOOGLE SHEETS VERBINDUNG
# =========================================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY"
).sheet1

data = sheet.get_all_records()

df_geo = pd.DataFrame(data)

# =========================================================
# NUMERISCHE SPALTEN
# =========================================================

numeric_columns = [

    "latitude",
    "longitude",

    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12",

    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6",

    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
    "Q16_11","Q16_12","Q16_13",

    "Q14_1","Q14_2","Q14_3","Q14_4","Q14_5",

    "Q15_1","Q15_2","Q15_3","Q15_4",
    "Q15_5","Q15_6","Q15_7",

    "Q5_3","Q5_4","Q5_5","Q5_6","Q5_7",
    "Q5_8","Q5_9","Q5_10","Q5_12","Q5_13",
    "Q5_14","Q5_15","Q5_16","Q5_17",
    "Q5_18","Q5_19","Q5_20",

    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8",

    "Q8_Anzahl_Rstrategien",
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8",
    "Q8_NEU_9","Q8_NEU_10","Q8_NEU_11","Q8_NEU_12",

    "Q41",
    "Q42"
]

for col in numeric_columns:

    if col in df_geo.columns:

        df_geo[col] = pd.to_numeric(
            df_geo[col],
            errors="coerce"
        )

# =========================================================
# KONSTRUKTE
# =========================================================

df_geo["VI_Mittelwert"] = df_geo[
    [
        "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
        "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
        "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
    ]
].mean(axis=1)

df_geo["VI_Closing"] = df_geo[
    ["Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"]
].mean(axis=1)

df_geo["VI_Slowing"] = df_geo[
    ["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5","Q9 NEU_6","Q9 NEU_7"]
].mean(axis=1)

df_geo["Ökonomische_Performance"] = df_geo[
    ["Q161_1","Q161_2","Q161_3","Q161_4","Q161_5","Q161_6"]
].mean(axis=1)

df_geo["Ökologische_Performance"] = df_geo[
    [
        "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
        "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
        "Q16_11","Q16_12","Q16_13"
    ]
].mean(axis=1)

df_geo["Produktlebensdauer"] = df_geo[
    ["Q16_3","Q16_4"]
].mean(axis=1)

df_geo["Toxische_Freisetzung"] = df_geo[
    ["Q16_6","Q16_7"]
].mean(axis=1)

df_geo["Loop_Closure"] = df_geo[
    ["Q14_1","Q14_2"]
].mean(axis=1)

df_geo["Open_Loops"] = df_geo[
    ["Q14_3","Q14_4","Q14_5"]
].mean(axis=1)

df_geo["Austausch"] = df_geo[
    ["Q15_1","Q15_2"]
].mean(axis=1)

df_geo["Erkenntnisse"] = df_geo[
    ["Q15_3","Q15_4","Q15_5","Q15_6","Q15_7"]
].mean(axis=1)

df_geo["Legitimität"] = df_geo[
    ["Q5_3","Q5_16","Q5_18","Q5_19","Q5_20"]
].mean(axis=1)

df_geo["Externer_Druck"] = df_geo[
    ["Q5_5","Q5_6","Q5_7"]
].mean(axis=1)

df_geo["Lern_und_Kooperationsorientierung"] = df_geo[
    ["Q5_12","Q5_13","Q5_14","Q5_15","Q5_17"]
].mean(axis=1)

df_geo["Differenzierungs_Wettbewerbsorientierung"] = df_geo[
    ["Q5_4","Q5_8","Q5_9","Q5_10"]
].mean(axis=1)

df_geo["Strategische_Integration"] = df_geo[
    ["Q6_1","Q6_2","Q6_3","Q6_4","Q6_5","Q6_6","Q6_7","Q6_8"]
].mean(axis=1)

df_geo["Anzahl_Rstrategien"] = df_geo["Q8_Anzahl_Rstrategien"]

df_geo["Firmengröße"] = df_geo["Q41"]

df_geo["Firmenalter"] = df_geo["Q42"]

# =========================================================
# VARIABLEN
# =========================================================

alle_variablen = [

    "VI_Mittelwert",
    "VI_Closing",
    "VI_Slowing",
    "Ökonomische_Performance",
    "Ökologische_Performance",
    "Produktlebensdauer",
    "Toxische_Freisetzung",
    "Loop_Closure",
    "Open_Loops",
    "Austausch",
    "Erkenntnisse",
    "Legitimität",
    "Externer_Druck",
    "Lern_und_Kooperationsorientierung",
    "Differenzierungs_Wettbewerbsorientierung",
    "Strategische_Integration",
    "Anzahl_Rstrategien",
    "Firmengröße",
    "Firmenalter"
]

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Einstellungen")

variable = st.sidebar.selectbox(
    "Variable auswählen",
    alle_variablen
)

radius = st.sidebar.slider(
    "Punktgröße",
    3,
    20,
    8
)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "Karte",
    "Korrelationen",
    "Datentabelle"
])

# =========================================================
# KARTE
# =========================================================

with tab1:

    st.subheader("Unternehmenskarte Österreich")

    map_data = df_geo.dropna(
        subset=["latitude", "longitude"]
    )

    st.write("Anzahl Punkte:", len(map_data))

    m = folium.Map(

        location=[
            map_data["latitude"].mean(),
            map_data["longitude"].mean()
        ],

        zoom_start=7,

        tiles="OpenStreetMap"
    )

    for _, row in map_data.iterrows():

        value = row[variable]

        if pd.isna(value):
            continue

        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=radius,

            color="black",

            weight=1,

            fill=True,

            fill_color="blue",

            fill_opacity=0.8,

            popup=f"""
            Variable: {variable}
            Wert: {round(value,2)}
            """

        ).add_to(m)

    st_folium(
        m,
        width=1600,
        height=900
    )

# =========================================================
# KORRELATIONEN
# =========================================================

with tab2:

    st.subheader("Pearson-Korrelation")

    col1, col2 = st.columns(2)

    with col1:

        corr_x = st.selectbox(
            "Variable 1",
            alle_variablen,
            index=0
        )

    with col2:

        corr_y = st.selectbox(
            "Variable 2",
            alle_variablen,
            index=1
        )

    corr_data = df_geo[
        [corr_x, corr_y]
    ].dropna()

    corr, pval = pearsonr(
        corr_data[corr_x],
        corr_data[corr_y]
    )

    st.markdown(
        f"""
        ## Pearson r = {corr:.3f}

        ### p-Wert = {pval:.5f}
        """
    )

    fig = px.scatter(

        corr_data,

        x=corr_x,

        y=corr_y,

        template="plotly_white",

        opacity=0.75
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# DATENTABELLE
# =========================================================

with tab3:

    st.subheader("Datentabelle")

    st.dataframe(
        df_geo,
        use_container_width=True,
        height=900
    )
