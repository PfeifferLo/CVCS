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
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
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
# LATITUDE / LONGITUDE FIX
# =========================================================

df_geo["latitude"] = (
    df_geo["latitude"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
)

df_geo["longitude"] = (
    df_geo["longitude"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.strip()
)

df_geo["latitude"] = pd.to_numeric(
    df_geo["latitude"],
    errors="coerce"
)

df_geo["longitude"] = pd.to_numeric(
    df_geo["longitude"],
    errors="coerce"
)

# =========================================================
# NUR ÖSTERREICH BEHALTEN
# =========================================================

df_geo = df_geo[
    (df_geo["latitude"] > 46) &
    (df_geo["latitude"] < 49.5) &
    (df_geo["longitude"] > 9) &
    (df_geo["longitude"] < 18.5)
]

# =========================================================
# NUMERISCHE VARIABLEN
# =========================================================

numeric_columns = [

    # Q9
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12",

    # Q161
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6",

    # Q16
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9",
    "Q16_10","Q16_11","Q16_12","Q16_13",

    # Q14
    "Q14_1","Q14_2","Q14_3","Q14_4","Q14_5",

    # Q15
    "Q15_1","Q15_2","Q15_3","Q15_4",
    "Q15_5","Q15_6","Q15_7",

    # Q5
    "Q5_3","Q5_4","Q5_5","Q5_6","Q5_7",
    "Q5_8","Q5_9","Q5_10","Q5_12","Q5_13",
    "Q5_14","Q5_15","Q5_16","Q5_17",
    "Q5_18","Q5_19","Q5_20",

    # Q6
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8",

    # Sonstige
    "Q41",
    "Q42"
]

# =========================================================
# ZAHLENFORMAT FIXEN
# =========================================================

for col in numeric_columns:

    if col in df_geo.columns:

        df_geo[col] = (
            df_geo[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

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
    ["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5",
     "Q9 NEU_6","Q9 NEU_7"]
].mean(axis=1)

df_geo["Oekonomische_Performance"] = df_geo[
    ["Q161_1","Q161_2","Q161_3",
     "Q161_4","Q161_5","Q161_6"]
].mean(axis=1)

df_geo["Oekologische_Performance"] = df_geo[
    [
        "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
        "Q16_6","Q16_7","Q16_8","Q16_9",
        "Q16_10","Q16_11","Q16_12","Q16_13"
    ]
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

df_geo["Legitimitaet"] = df_geo[
    ["Q5_3","Q5_16","Q5_18","Q5_19","Q5_20"]
].mean(axis=1)

df_geo["Externer_Druck"] = df_geo[
    ["Q5_5","Q5_6","Q5_7"]
].mean(axis=1)

df_geo["Strategische_Integration"] = df_geo[
    ["Q6_1","Q6_2","Q6_3","Q6_4",
     "Q6_5","Q6_6","Q6_7","Q6_8"]
].mean(axis=1)

# =========================================================
# VARIABLEN
# =========================================================

alle_variablen = [

    "VI_Mittelwert",
    "VI_Closing",
    "VI_Slowing",

    "Oekonomische_Performance",
    "Oekologische_Performance",

    "Loop_Closure",
    "Open_Loops",

    "Austausch",
    "Erkenntnisse",

    "Legitimitaet",
    "Externer_Druck",

    "Strategische_Integration"
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
        subset=["latitude", "longitude", variable]
    ).copy()

    st.write("Anzahl Firmen:", len(map_data))

    m = folium.Map(
        location=[47.7, 13.3],
        zoom_start=7,
        tiles="CartoDB positron"
    )

    # =====================================================
    # FARBEN
    # =====================================================

    def get_color(v):

        if v <= 2:
            return "#d73027"

        elif v <= 3:
            return "#fc8d59"

        elif v <= 4:
            return "#fee08b"

        elif v <= 5:
            return "#91cf60"

        else:
            return "#1a9850"

    # =====================================================
    # MARKER
    # =====================================================

    for _, row in map_data.iterrows():

        popup = f"""
        <b>{variable}</b><br>
        Wert: {round(row[variable], 2)}<br><br>

        <b>Adresse:</b><br>
        {row.get('adresse', 'Keine Adresse')}<br><br>

        <b>Latitude:</b> {row['latitude']}<br>
        <b>Longitude:</b> {row['longitude']}
        """

        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=radius,

            popup=folium.Popup(
                popup,
                max_width=350
            ),

            color="black",

            weight=1,

            fill=True,

            fill_color=get_color(row[variable]),

            fill_opacity=0.85

        ).add_to(m)

    st_folium(
        m,
        width=1500,
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
            "Variable X",
            alle_variablen,
            index=0
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1
        )

    corr_data = df_geo[
        [corr_x, corr_y]
    ].dropna()

    if len(corr_data) > 2:

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

            trendline="ols",

            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning("Zu wenige Datenpunkte.")

# =========================================================
# DATENTABELLE
# =========================================================

with tab3:

    st.subheader("Datentabelle")

    st.dataframe(
        df_geo,
        use_container_width=True,
        height=900
    )# =========================================================
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
# GOOGLE SHEETS
# =========================================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
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
# LATITUDE / LONGITUDE KORREKTUR
# =========================================================
# Problem:
# 481593365 wurde gespeichert statt 48.1593365
# 16497746 wurde gespeichert statt 16.497746
#
# Deshalb:
# latitude / 10.000.000
# longitude / 1.000.000
# =========================================================

df_geo["latitude"] = pd.to_numeric(
    df_geo["latitude"],
    errors="coerce"
)

df_geo["longitude"] = pd.to_numeric(
    df_geo["longitude"],
    errors="coerce"
)

df_geo["latitude"] = df_geo["latitude"] / 10000000
df_geo["longitude"] = df_geo["longitude"] / 1000000

# =========================================================
# NUR ÖSTERREICH BEHALTEN
# =========================================================

df_geo = df_geo[
    (df_geo["latitude"] > 46) &
    (df_geo["latitude"] < 49.5) &
    (df_geo["longitude"] > 9) &
    (df_geo["longitude"] < 18.5)
]

# =========================================================
# NUMERISCHE VARIABLEN
# =========================================================

numeric_columns = [

    # Q9
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12",

    # Q161
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6",

    # Q16
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9",
    "Q16_10","Q16_11","Q16_12","Q16_13",

    # Q14
    "Q14_1","Q14_2","Q14_3","Q14_4","Q14_5",

    # Q15
    "Q15_1","Q15_2","Q15_3","Q15_4",
    "Q15_5","Q15_6","Q15_7",

    # Q5
    "Q5_3","Q5_4","Q5_5","Q5_6","Q5_7",
    "Q5_8","Q5_9","Q5_10","Q5_12","Q5_13",
    "Q5_14","Q5_15","Q5_16","Q5_17",
    "Q5_18","Q5_19","Q5_20",

    # Q6
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8",

    # Sonstige
    "Q41",
    "Q42"
]

# =========================================================
# ZAHLENFORMAT FIXEN
# =========================================================

for col in numeric_columns:

    if col in df_geo.columns:

        df_geo[col] = (
            df_geo[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

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
    ["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5",
     "Q9 NEU_6","Q9 NEU_7"]
].mean(axis=1)

df_geo["Ökonomische_Performance"] = df_geo[
    ["Q161_1","Q161_2","Q161_3",
     "Q161_4","Q161_5","Q161_6"]
].mean(axis=1)

df_geo["Ökologische_Performance"] = df_geo[
    [
        "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
        "Q16_6","Q16_7","Q16_8","Q16_9",
        "Q16_10","Q16_11","Q16_12","Q16_13"
    ]
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

df_geo["Strategische_Integration"] = df_geo[
    ["Q6_1","Q6_2","Q6_3","Q6_4",
     "Q6_5","Q6_6","Q6_7","Q6_8"]
].mean(axis=1)

# =========================================================
# VARIABLEN
# =========================================================

alle_variablen = [

    "VI_Mittelwert",
    "VI_Closing",
    "VI_Slowing",

    "Ökonomische_Performance",
    "Ökologische_Performance",

    "Loop_Closure",
    "Open_Loops",

    "Austausch",
    "Erkenntnisse",

    "Legitimität",
    "Externer_Druck",

    "Strategische_Integration"
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
        subset=["latitude", "longitude", variable]
    ).copy()

    st.write("Anzahl Firmen:", len(map_data))

    # =====================================================
    # OPENSTREETMAP
    # =====================================================

    m = folium.Map(

        location=[47.7, 13.3],

        zoom_start=7,

        tiles="OpenStreetMap"
    )

    # =====================================================
    # FARBEN
    # =====================================================

    def get_color(v):

        if v <= 2:
            return "#d73027"

        elif v <= 3:
            return "#fc8d59"

        elif v <= 4:
            return "#fee08b"

        elif v <= 5:
            return "#91cf60"

        else:
            return "#1a9850"

    # =====================================================
    # MARKER
    # =====================================================

    for _, row in map_data.iterrows():

        popup = f"""
        <b>{variable}</b><br>
        Wert: {round(row[variable],2)}<br><br>

        <b>Latitude:</b> {row['latitude']}<br>
        <b>Longitude:</b> {row['longitude']}
        """

        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=radius,

            popup=popup,

            color="black",

            weight=1,

            fill=True,

            fill_color=get_color(row[variable]),

            fill_opacity=0.9

        ).add_to(m)

    # =====================================================
    # KARTE ZEIGEN
    # =====================================================

    st_folium(
        m,
        width=1500,
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
            "Variable X",
            alle_variablen,
            index=0
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
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

        trendline="ols",

        template="plotly_white"
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
    )# =========================================================
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
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
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
# LATITUDE / LONGITUDE FIX
# =========================================================
# Google Sheets hat die Kommas entfernt:
#
# 481593365  -> 48.1593365
# 16497746   -> 16.497746
# =========================================================

df_geo["latitude"] = pd.to_numeric(
    df_geo["latitude"],
    errors="coerce"
)

df_geo["longitude"] = pd.to_numeric(
    df_geo["longitude"],
    errors="coerce"
)

# Dezimalstellen zurückbringen
df_geo["latitude"] = df_geo["latitude"] / 10000000
df_geo["longitude"] = df_geo["longitude"] / 1000000

# =========================================================
# NUMERISCHE SPALTEN
# =========================================================

numeric_columns = [

    # Q9
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12",

    # Q161
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6",

    # Q16
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9",
    "Q16_10","Q16_11","Q16_12","Q16_13",

    # Q14
    "Q14_1","Q14_2","Q14_3","Q14_4","Q14_5",

    # Q15
    "Q15_1","Q15_2","Q15_3","Q15_4",
    "Q15_5","Q15_6","Q15_7",

    # Q5
    "Q5_3","Q5_4","Q5_5","Q5_6","Q5_7",
    "Q5_8","Q5_9","Q5_10","Q5_12","Q5_13",
    "Q5_14","Q5_15","Q5_16","Q5_17",
    "Q5_18","Q5_19","Q5_20",

    # Q6
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8",

    # Q41 / Q42
    "Q41",
    "Q42"
]

# =========================================================
# KOMMA -> PUNKT
# =========================================================

for col in numeric_columns:

    if col in df_geo.columns:

        df_geo[col] = (
            df_geo[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )

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
    ["Q161_1","Q161_2","Q161_3",
     "Q161_4","Q161_5","Q161_6"]
].mean(axis=1)

df_geo["Ökologische_Performance"] = df_geo[
    [
        "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
        "Q16_6","Q16_7","Q16_8","Q16_9",
        "Q16_10","Q16_11","Q16_12","Q16_13"
    ]
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

df_geo["Strategische_Integration"] = df_geo[
    ["Q6_1","Q6_2","Q6_3","Q6_4",
     "Q6_5","Q6_6","Q6_7","Q6_8"]
].mean(axis=1)

# =========================================================
# VARIABLEN
# =========================================================

alle_variablen = [

    "VI_Mittelwert",
    "VI_Closing",
    "VI_Slowing",

    "Ökonomische_Performance",
    "Ökologische_Performance",

    "Loop_Closure",
    "Open_Loops",

    "Austausch",
    "Erkenntnisse",

    "Legitimität",
    "Externer_Druck",

    "Strategische_Integration"
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
        subset=["latitude", "longitude", variable]
    ).copy()

    st.write("Anzahl Firmen:", len(map_data))

    # DEBUG
    st.write(
        map_data[
            ["latitude", "longitude"]
        ].head()
    )

    # =====================================================
    # OPENSTREETMAP
    # =====================================================

    m = folium.Map(

        location=[47.7, 13.3],

        zoom_start=7,

        tiles="OpenStreetMap"
    )

    # =====================================================
    # FARBEN
    # =====================================================

    def get_color(v):

        if v <= 2:
            return "red"

        elif v <= 3:
            return "orange"

        elif v <= 4:
            return "beige"

        elif v <= 5:
            return "green"

        else:
            return "darkgreen"

    # =====================================================
    # MARKER
    # =====================================================

    for _, row in map_data.iterrows():

        popup = f"""
        <b>{variable}</b><br>
        Wert: {round(row[variable],2)}
        """

        folium.CircleMarker(

            location=[
                float(row["latitude"]),
                float(row["longitude"])
            ],

            radius=radius,

            popup=popup,

            color="black",

            weight=1,

            fill=True,

            fill_color=get_color(row[variable]),

            fill_opacity=0.9

        ).add_to(m)

    # =====================================================
    # KARTE ZEIGEN
    # =====================================================

    st_folium(
        m,
        width=1400,
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
            "Variable X",
            alle_variablen,
            index=0
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
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

        trendline="ols"
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
