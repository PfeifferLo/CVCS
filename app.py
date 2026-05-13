# =========================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px

from streamlit_folium import st_folium
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

df = pd.DataFrame(data)

# =========================================================
# LEERE WERTE
# =========================================================

df = df.replace("", np.nan)

# =========================================================
# KOORDINATEN FIX
# =========================================================

def fix_coordinates(x):

    if pd.isna(x):
        return np.nan

    x = str(x).replace(",", ".")

    try:
        x = float(x)

    except:
        return np.nan

    # Falls Komma fehlt
    if x > 1000:
        x = x / 1000000

    return x

df["latitude"] = df["latitude"].apply(fix_coordinates)
df["longitude"] = df["longitude"].apply(fix_coordinates)

# =========================================================
# NUMERISCHE SPALTEN
# =========================================================

numeric_columns = [

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

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================================================
# HILFSFUNKTIONEN
# =========================================================

def safe_mean(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].mean(
        axis=1,
        skipna=True
    )

def safe_sum(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].sum(
        axis=1,
        skipna=True
    )

# =========================================================
# KONSTRUKTE
# =========================================================

df["VI_Mittelwert"] = safe_mean([
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Closing"] = safe_mean([
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Slowing"] = safe_mean([
    "Q9 NEU_3","Q9 NEU_4","Q9 NEU_5",
    "Q9 NEU_6","Q9 NEU_7"
])

df["Ökonomische_Performance"] = safe_mean([
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6"
])

df["Ökologische_Performance"] = safe_mean([
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9",
    "Q16_10","Q16_11","Q16_12","Q16_13"
])

df["Produktlebensdauer"] = safe_mean([
    "Q16_3","Q16_4"
])

df["Toxische_Freisetzung"] = safe_mean([
    "Q16_6","Q16_7"
])

df["Loop_Closure"] = safe_mean([
    "Q14_1","Q14_2"
])

df["Open_Loops"] = safe_mean([
    "Q14_3","Q14_4","Q14_5"
])

df["Austausch"] = safe_mean([
    "Q15_1","Q15_2"
])

df["Erkenntnisse"] = safe_mean([
    "Q15_3","Q15_4","Q15_5",
    "Q15_6","Q15_7"
])

df["Legitimität"] = safe_mean([
    "Q5_3","Q5_16","Q5_18",
    "Q5_19","Q5_20"
])

df["Externer_Druck"] = safe_mean([
    "Q5_5","Q5_6","Q5_7"
])

df["Lern_und_Kooperationsorientierung"] = safe_mean([
    "Q5_12","Q5_13","Q5_14",
    "Q5_15","Q5_17"
])

df["Differenzierungs_Wettbewerbsorientierung"] = safe_mean([
    "Q5_4","Q5_8","Q5_9","Q5_10"
])

df["Strategische_Integration"] = safe_mean([
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8"
])

df["Anzahl_Rstrategien"] = df["Q8_Anzahl_Rstrategien"]

df["Anzahl_Closing_Strategien"] = safe_sum([
    "Q8_NEU_9","Q8_NEU_10",
    "Q8_NEU_11","Q8_NEU_12"
])

df["Anzahl_Slowing_Strategien"] = safe_sum([
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8"
])

df["Firmengröße"] = df["Q41"]
df["Firmenalter"] = df["Q42"]

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
    "Anzahl_Closing_Strategien",
    "Anzahl_Slowing_Strategien",

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

    map_data = df.dropna(
        subset=["latitude", "longitude", variable]
    ).copy()

    # Nur Österreich
    map_data = map_data[
        (map_data["latitude"] > 46) &
        (map_data["latitude"] < 49.5) &
        (map_data["longitude"] > 9) &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen auf Karte:", len(map_data))

    # =====================================================
    # KARTE
    # =====================================================

    m = folium.Map(
        location=[47.6, 14.5],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # =====================================================
    # VI VARIABLEN
    # =====================================================

    vi_variablen = [
        "VI_Mittelwert",
        "VI_Closing",
        "VI_Slowing"
    ]

    # =====================================================
    # FARBEN
    # =====================================================

    def get_color(v):

        if pd.isna(v):
            return "gray"

        if variable in vi_variablen:

            if v <= 2:
                return "#d73027"

            elif v <= 3:
                return "#fc8d59"

            elif v <= 4:
                return "#fee08b"

            elif v <= 5:
                return "#91cf60"

            elif v <= 6:
                return "#66bd63"

            else:
                return "#1a9850"

        else:

            if v <= 2:
                return "#d73027"

            elif v <= 3:
                return "#fc8d59"

            elif v <= 4:
                return "#fee08b"

            else:
                return "#1a9850"

    # =====================================================
    # LEGENDE
    # =====================================================

    if variable in vi_variablen:

        legend_html = f"""
        <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index:9999;
        background:white;
        padding:15px;
        border:2px solid grey;
        border-radius:10px;
        font-size:14px;
        ">

        <b>{variable}</b><br><br>

        <div style="background:#d73027;width:20px;height:20px;display:inline-block;"></div> 1-2<br>
        <div style="background:#fc8d59;width:20px;height:20px;display:inline-block;"></div> 2-3<br>
        <div style="background:#fee08b;width:20px;height:20px;display:inline-block;"></div> 3-4<br>
        <div style="background:#91cf60;width:20px;height:20px;display:inline-block;"></div> 4-5<br>
        <div style="background:#66bd63;width:20px;height:20px;display:inline-block;"></div> 5-6<br>
        <div style="background:#1a9850;width:20px;height:20px;display:inline-block;"></div> 6-7

        </div>
        """

    else:

        legend_html = f"""
        <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index:9999;
        background:white;
        padding:15px;
        border:2px solid grey;
        border-radius:10px;
        font-size:14px;
        ">

        <b>{variable}</b><br><br>

        <div style="background:#d73027;width:20px;height:20px;display:inline-block;"></div> 1-2<br>
        <div style="background:#fc8d59;width:20px;height:20px;display:inline-block;"></div> 2-3<br>
        <div style="background:#fee08b;width:20px;height:20px;display:inline-block;"></div> 3-4<br>
        <div style="background:#1a9850;width:20px;height:20px;display:inline-block;"></div> 4-5

        </div>
        """

    # =====================================================
    # PUNKTE
    # =====================================================

    for _, row in map_data.iterrows():

        firma = row.get("Zugehörigkeit", "Keine Angabe")

        popup = f"""
        <b>Firma:</b><br>
        {firma}<br><br>

        <b>Variable:</b><br>
        {variable}<br><br>

        <b>Wert:</b><br>
        {round(row[variable],2)}
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=radius,
            popup=folium.Popup(
                popup,
                max_width=300
            ),
            color="black",
            weight=1,
            fill=True,
            fill_color=get_color(row[variable]),
            fill_opacity=0.85
        ).add_to(m)

    # =====================================================
    # LEGENDE HINZUFÜGEN
    # =====================================================

    m.get_root().html.add_child(
        folium.Element(legend_html)
    )

    # =====================================================
    # KARTE ANZEIGEN
    # =====================================================

    st_folium(
        m,
        width=1400,
        height=850
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
            key="corr_x"
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1,
            key="corr_y"
        )

    corr_data = df[
        [corr_x, corr_y]
    ].dropna()

    if len(corr_data) > 2:

        corr, pval = pearsonr(
            corr_data[corr_x],
            corr_data[corr_y]
        )

        st.metric(
            "Pearson r",
            round(corr, 3)
        )

        st.metric(
            "p-Wert",
            round(pval, 5)
        )

        fig = px.scatter(
            corr_data,
            x=corr_x,
            y=corr_y,
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
        df,
        use_container_width=True,
        height=900
    )# =========================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px

from streamlit_folium import st_folium
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

# =========================================================
# GOOGLE SHEET LADEN
# =========================================================

sheet = client.open_by_key(
    "1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY"
).sheet1

data = sheet.get_all_records()

df = pd.DataFrame(data)

# =========================================================
# LEERE STRINGS -> NA
# =========================================================

df = df.replace("", np.nan)

# =========================================================
# KOORDINATEN FIX
# =========================================================

def fix_coordinates(x):

    if pd.isna(x):
        return np.nan

    x = str(x).replace(",", ".")

    try:
        x = float(x)

    except:
        return np.nan

    # bereits korrekt
    if 40 <= x <= 50:
        return x

    # format ohne komma
    if x > 1000000:
        return x / 10000000

    return x

df["latitude"] = df["latitude"].apply(fix_coordinates)
df["longitude"] = df["longitude"].apply(fix_coordinates)

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
    "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
    "Q16_11","Q16_12","Q16_13",

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

    # Q8
    "Q8_Anzahl_Rstrategien",
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8",
    "Q8_NEU_9","Q8_NEU_10","Q8_NEU_11","Q8_NEU_12",

    # Sonstige
    "Q41",
    "Q42"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================================================
# KONSTRUKTE
# =========================================================

def safe_mean(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].mean(axis=1, skipna=True)

def safe_sum(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].sum(axis=1, skipna=True)

# =========================================================
# VI
# =========================================================

df["VI_Mittelwert"] = safe_mean([
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Closing"] = safe_mean([
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Slowing"] = safe_mean([
    "Q9 NEU_3","Q9 NEU_4","Q9 NEU_5",
    "Q9 NEU_6","Q9 NEU_7"
])

# =========================================================
# PERFORMANCE
# =========================================================

df["Ökonomische_Performance"] = safe_mean([
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6"
])

df["Ökologische_Performance"] = safe_mean([
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
    "Q16_11","Q16_12","Q16_13"
])

# =========================================================
# UNTERKONSTRUKTE
# =========================================================

df["Produktlebensdauer"] = safe_mean([
    "Q16_3","Q16_4"
])

df["Toxische_Freisetzung"] = safe_mean([
    "Q16_6","Q16_7"
])

df["Loop_Closure"] = safe_mean([
    "Q14_1","Q14_2"
])

df["Open_Loops"] = safe_mean([
    "Q14_3","Q14_4","Q14_5"
])

df["Austausch"] = safe_mean([
    "Q15_1","Q15_2"
])

df["Erkenntnisse"] = safe_mean([
    "Q15_3","Q15_4","Q15_5",
    "Q15_6","Q15_7"
])

df["Legitimität"] = safe_mean([
    "Q5_3","Q5_16","Q5_18",
    "Q5_19","Q5_20"
])

df["Externer_Druck"] = safe_mean([
    "Q5_5","Q5_6","Q5_7"
])

df["Lern_und_Kooperationsorientierung"] = safe_mean([
    "Q5_12","Q5_13","Q5_14",
    "Q5_15","Q5_17"
])

df["Differenzierungs_Wettbewerbsorientierung"] = safe_mean([
    "Q5_4","Q5_8","Q5_9","Q5_10"
])

df["Strategische_Integration"] = safe_mean([
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8"
])

# =========================================================
# STRATEGIEN
# =========================================================

df["Anzahl_Rstrategien"] = df["Q8_Anzahl_Rstrategien"]

df["Anzahl_Closing_Strategien"] = safe_sum([
    "Q8_NEU_9","Q8_NEU_10",
    "Q8_NEU_11","Q8_NEU_12"
])

df["Anzahl_Slowing_Strategien"] = safe_sum([
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8"
])

df["Firmengröße"] = df["Q41"]
df["Firmenalter"] = df["Q42"]

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
    "Anzahl_Closing_Strategien",
    "Anzahl_Slowing_Strategien",

    "Firmengröße",
    "Firmenalter"
]

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Einstellungen")

variable = st.sidebar.selectbox(
    "Variable auswählen",
    alle_variablen,
    key="variable_select"
)

radius = st.sidebar.slider(
    "Punktgröße",
    3,
    20,
    8,
    key="radius_slider"
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

    map_data = df.dropna(
        subset=["latitude", "longitude", variable]
    ).copy()

    # Österreich Filter
    map_data = map_data[
        (map_data["latitude"] > 46) &
        (map_data["latitude"] < 49.5) &
        (map_data["longitude"] > 9) &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen auf Karte:", len(map_data))

    m = folium.Map(
        location=[47.6, 14.5],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # Farben
    def get_color(v):

        if pd.isna(v):
            return "gray"

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

    # Punkte
    for _, row in map_data.iterrows():

        popup = f"""
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> {round(row[variable],2)}
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
            fill_opacity=0.85
        ).add_to(m)

    st_folium(
        m,
        width=1400,
        height=850
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
            key="corr_x"
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1,
            key="corr_y"
        )

    corr_data = df[
        [corr_x, corr_y]
    ].dropna()

    if len(corr_data) > 2:

        corr, pval = pearsonr(
            corr_data[corr_x],
            corr_data[corr_y]
        )

        st.metric(
            "Pearson r",
            round(corr, 3)
        )

        st.metric(
            "p-Wert",
            round(pval, 5)
        )

        fig = px.scatter(
            corr_data,
            x=corr_x,
            y=corr_y,
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
        df,
        use_container_width=True,
        height=900
    )# =========================================================
# KARTE
# =========================================================

with tab1:

    st.subheader("Unternehmenskarte Österreich")

    # =====================================================
    # NUR GÜLTIGE DATEN
    # =====================================================

    map_data = df.dropna(
        subset=["latitude", "longitude", variable]
    ).copy()

    # Österreich Filter
    map_data = map_data[
        (map_data["latitude"] > 46) &
        (map_data["latitude"] < 49.5) &
        (map_data["longitude"] > 9) &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen auf Karte:", len(map_data))

    # =====================================================
    # KARTE
    # =====================================================

    m = folium.Map(
        location=[47.6, 14.5],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # =====================================================
    # VARIABLE TYPEN
    # =====================================================

    vi_variablen = [
        "VI_Mittelwert",
        "VI_Closing",
        "VI_Slowing"
    ]

    # =====================================================
    # FARBEN + LEGENDE
    # =====================================================

    # -----------------------------------------------------
    # VI 1-7
    # -----------------------------------------------------

    if variable in vi_variablen:

        def get_color(v):

            if v <= 1:
                return "#b2182b"

            elif v <= 2:
                return "#d6604d"

            elif v <= 3:
                return "#f4a582"

            elif v <= 4:
                return "#fddbc7"

            elif v <= 5:
                return "#92c5de"

            elif v <= 6:
                return "#4393c3"

            else:
                return "#2166ac"

        legend_html = f"""
        <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index:9999;
        background-color:white;
        padding:15px;
        border:2px solid grey;
        border-radius:10px;
        font-size:14px;
        ">

        <b>{variable}</b><br><br>

        <div style="background:#b2182b;width:20px;height:20px;display:inline-block;"></div> 1<br>
        <div style="background:#d6604d;width:20px;height:20px;display:inline-block;"></div> 2<br>
        <div style="background:#f4a582;width:20px;height:20px;display:inline-block;"></div> 3<br>
        <div style="background:#fddbc7;width:20px;height:20px;display:inline-block;"></div> 4<br>
        <div style="background:#92c5de;width:20px;height:20px;display:inline-block;"></div> 5<br>
        <div style="background:#4393c3;width:20px;height:20px;display:inline-block;"></div> 6<br>
        <div style="background:#2166ac;width:20px;height:20px;display:inline-block;"></div> 7

        </div>
        """

    # -----------------------------------------------------
    # STANDARD 1-5
    # -----------------------------------------------------

    else:

        def get_color(v):

            if v <= 1:
                return "#d73027"

            elif v <= 2:
                return "#fc8d59"

            elif v <= 3:
                return "#fee08b"

            elif v <= 4:
                return "#91cf60"

            else:
                return "#1a9850"

        legend_html = f"""
        <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index:9999;
        background-color:white;
        padding:15px;
        border:2px solid grey;
        border-radius:10px;
        font-size:14px;
        ">

        <b>{variable}</b><br><br>

        <div style="background:#d73027;width:20px;height:20px;display:inline-block;"></div> 1<br>
        <div style="background:#fc8d59;width:20px;height:20px;display:inline-block;"></div> 2<br>
        <div style="background:#fee08b;width:20px;height:20px;display:inline-block;"></div> 3<br>
        <div style="background:#91cf60;width:20px;height:20px;display:inline-block;"></div> 4<br>
        <div style="background:#1a9850;width:20px;height:20px;display:inline-block;"></div> 5

        </div>
        """

    # =====================================================
    # MARKER
    # =====================================================

    for _, row in map_data.iterrows():

        popup = f"""
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> {round(row[variable],2)}
        """

        folium.CircleMarker(

            location=[
                row["latitude"],
                row["longitude"]
            ],

            radius=radius,

            color="black",

            weight=1,

            fill=True,

            fill_color=get_color(row[variable]),

            fill_opacity=0.9,

            popup=popup

        ).add_to(m)

    # =====================================================
    # LEGENDE
    # =====================================================

    m.get_root().html.add_child(
        folium.Element(legend_html)
    )

    # =====================================================
    # KARTE ZEIGEN
    # =====================================================

    st_folium(
        m,
        width=1400,
        height=850
    )# =========================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px

from streamlit_folium import st_folium
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

# =========================================================
# GOOGLE SHEET LADEN
# =========================================================

sheet = client.open_by_key(
    "1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY"
).sheet1

data = sheet.get_all_records()

df = pd.DataFrame(data)

# =========================================================
# LEERE STRINGS -> NA
# =========================================================

df = df.replace("", np.nan)

# =========================================================
# KOORDINATEN FIX
# =========================================================

def fix_coordinates(x):

    if pd.isna(x):
        return np.nan

    x = str(x).replace(",", ".")

    try:
        x = float(x)

    except:
        return np.nan

    # bereits korrekt
    if 40 <= x <= 50:
        return x

    # format ohne komma
    if x > 1000000:
        return x / 10000000

    return x

df["latitude"] = df["latitude"].apply(fix_coordinates)
df["longitude"] = df["longitude"].apply(fix_coordinates)

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
    "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
    "Q16_11","Q16_12","Q16_13",

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

    # Q8
    "Q8_Anzahl_Rstrategien",
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8",
    "Q8_NEU_9","Q8_NEU_10","Q8_NEU_11","Q8_NEU_12",

    # Sonstige
    "Q41",
    "Q42"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================================================
# KONSTRUKTE
# =========================================================

def safe_mean(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].mean(axis=1, skipna=True)

def safe_sum(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].sum(axis=1, skipna=True)

# =========================================================
# VI
# =========================================================

df["VI_Mittelwert"] = safe_mean([
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Closing"] = safe_mean([
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Slowing"] = safe_mean([
    "Q9 NEU_3","Q9 NEU_4","Q9 NEU_5",
    "Q9 NEU_6","Q9 NEU_7"
])

# =========================================================
# PERFORMANCE
# =========================================================

df["Ökonomische_Performance"] = safe_mean([
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6"
])

df["Ökologische_Performance"] = safe_mean([
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
    "Q16_11","Q16_12","Q16_13"
])

# =========================================================
# UNTERKONSTRUKTE
# =========================================================

df["Produktlebensdauer"] = safe_mean([
    "Q16_3","Q16_4"
])

df["Toxische_Freisetzung"] = safe_mean([
    "Q16_6","Q16_7"
])

df["Loop_Closure"] = safe_mean([
    "Q14_1","Q14_2"
])

df["Open_Loops"] = safe_mean([
    "Q14_3","Q14_4","Q14_5"
])

df["Austausch"] = safe_mean([
    "Q15_1","Q15_2"
])

df["Erkenntnisse"] = safe_mean([
    "Q15_3","Q15_4","Q15_5",
    "Q15_6","Q15_7"
])

df["Legitimität"] = safe_mean([
    "Q5_3","Q5_16","Q5_18",
    "Q5_19","Q5_20"
])

df["Externer_Druck"] = safe_mean([
    "Q5_5","Q5_6","Q5_7"
])

df["Lern_und_Kooperationsorientierung"] = safe_mean([
    "Q5_12","Q5_13","Q5_14",
    "Q5_15","Q5_17"
])

df["Differenzierungs_Wettbewerbsorientierung"] = safe_mean([
    "Q5_4","Q5_8","Q5_9","Q5_10"
])

df["Strategische_Integration"] = safe_mean([
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8"
])

# =========================================================
# STRATEGIEN
# =========================================================

df["Anzahl_Rstrategien"] = df["Q8_Anzahl_Rstrategien"]

df["Anzahl_Closing_Strategien"] = safe_sum([
    "Q8_NEU_9","Q8_NEU_10",
    "Q8_NEU_11","Q8_NEU_12"
])

df["Anzahl_Slowing_Strategien"] = safe_sum([
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8"
])

df["Firmengröße"] = df["Q41"]
df["Firmenalter"] = df["Q42"]

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
    "Anzahl_Closing_Strategien",
    "Anzahl_Slowing_Strategien",

    "Firmengröße",
    "Firmenalter"
]

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Einstellungen")

variable = st.sidebar.selectbox(
    "Variable auswählen",
    alle_variablen,
    key="variable_select"
)

radius = st.sidebar.slider(
    "Punktgröße",
    3,
    20,
    8,
    key="radius_slider"
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

    map_data = df.dropna(
        subset=["latitude", "longitude", variable]
    ).copy()

    # Österreich Filter
    map_data = map_data[
        (map_data["latitude"] > 46) &
        (map_data["latitude"] < 49.5) &
        (map_data["longitude"] > 9) &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen auf Karte:", len(map_data))

    m = folium.Map(
        location=[47.6, 14.5],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # Farben
    def get_color(v):

        if pd.isna(v):
            return "gray"

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

    # Punkte
    for _, row in map_data.iterrows():

        popup = f"""
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> {round(row[variable],2)}
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
            fill_opacity=0.85
        ).add_to(m)

    st_folium(
        m,
        width=1400,
        height=850
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
            key="corr_x"
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1,
            key="corr_y"
        )

    corr_data = df[
        [corr_x, corr_y]
    ].dropna()

    if len(corr_data) > 2:

        corr, pval = pearsonr(
            corr_data[corr_x],
            corr_data[corr_y]
        )

        st.metric(
            "Pearson r",
            round(corr, 3)
        )

        st.metric(
            "p-Wert",
            round(pval, 5)
        )

        fig = px.scatter(
            corr_data,
            x=corr_x,
            y=corr_y,
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
        df,
        use_container_width=True,
        height=900
    )# =========================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
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

# =========================================================
# WICHTIG:
# Spreadsheet muss freigegeben sein
# für die service account mail
# =========================================================

SPREADSHEET_ID = "1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY"

try:

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    sheet = spreadsheet.sheet1

    data = sheet.get_all_records()

    df_geo = pd.DataFrame(data)

except Exception as e:

    st.error(
        """
        Google Sheet konnte nicht geladen werden.

        Prüfe:
        1. Spreadsheet-ID
        2. Freigabe für Service Account
        3. Secrets in Streamlit
        """
    )

    st.stop()

# =========================================================
# LEERE STRINGS -> NA
# =========================================================

df_geo = df_geo.replace("", np.nan)

# =========================================================
# LATITUDE / LONGITUDE FIX
# =========================================================
# Deine Daten:
# 481593365 -> 48.1593365
# 16497746  -> 16.497746
# =========================================================

df_geo["latitude"] = (
    df_geo["latitude"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

df_geo["longitude"] = (
    df_geo["longitude"]
    .astype(str)
    .str.replace(",", ".", regex=False)
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
# SKALIERUNG REPARIEREN
# =========================================================

df_geo["latitude"] = df_geo["latitude"] / 10000000
df_geo["longitude"] = df_geo["longitude"] / 1000000

# =========================================================
# ÖSTERREICH FILTER
# =========================================================

df_geo = df_geo[
    (df_geo["latitude"] > 46) &
    (df_geo["latitude"] < 49.5) &
    (df_geo["longitude"] > 9) &
    (df_geo["longitude"] < 18.5)
]

# =========================================================
# NUMERISCHE SPALTEN
# =========================================================

numeric_cols = [

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
    "Q6_5","Q6_6","Q6_7","Q6_8"
]

# =========================================================
# NUMERISCH MACHEN
# =========================================================

for col in numeric_cols:

    if col in df_geo.columns:

        df_geo[col] = (
            df_geo[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )

        df_geo[col] = pd.to_numeric(
            df_geo[col],
            errors="coerce"
        )

# =========================================================
# KONSTRUKTE
# WICHTIG:
# skipna=True
# => Firmen werden NICHT komplett NA
# =========================================================

df_geo["VI_Mittelwert"] = df_geo[
    [
        "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
        "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
        "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
    ]
].mean(axis=1, skipna=True)

df_geo["VI_Closing"] = df_geo[
    ["Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"]
].mean(axis=1, skipna=True)

df_geo["VI_Slowing"] = df_geo[
    ["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5","Q9 NEU_6","Q9 NEU_7"]
].mean(axis=1, skipna=True)

df_geo["Ökonomische_Performance"] = df_geo[
    ["Q161_1","Q161_2","Q161_3","Q161_4","Q161_5","Q161_6"]
].mean(axis=1, skipna=True)

df_geo["Ökologische_Performance"] = df_geo[
    [
        "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
        "Q16_6","Q16_7","Q16_8","Q16_9",
        "Q16_10","Q16_11","Q16_12","Q16_13"
    ]
].mean(axis=1, skipna=True)

df_geo["Loop_Closure"] = df_geo[
    ["Q14_1","Q14_2"]
].mean(axis=1, skipna=True)

df_geo["Open_Loops"] = df_geo[
    ["Q14_3","Q14_4","Q14_5"]
].mean(axis=1, skipna=True)

df_geo["Austausch"] = df_geo[
    ["Q15_1","Q15_2"]
].mean(axis=1, skipna=True)

df_geo["Erkenntnisse"] = df_geo[
    ["Q15_3","Q15_4","Q15_5","Q15_6","Q15_7"]
].mean(axis=1, skipna=True)

df_geo["Legitimität"] = df_geo[
    ["Q5_3","Q5_16","Q5_18","Q5_19","Q5_20"]
].mean(axis=1, skipna=True)

df_geo["Externer_Druck"] = df_geo[
    ["Q5_5","Q5_6","Q5_7"]
].mean(axis=1, skipna=True)

df_geo["Strategische_Integration"] = df_geo[
    ["Q6_1","Q6_2","Q6_3","Q6_4",
     "Q6_5","Q6_6","Q6_7","Q6_8"]
].mean(axis=1, skipna=True)

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
    alle_variablen,
    key="variable_select"
)

radius = st.sidebar.slider(
    "Punktgröße",
    min_value=3,
    max_value=20,
    value=8,
    key="radius_slider"
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

    # =====================================================
    # NUR KOORDINATEN MÜSSEN EXISTIEREN
    # =====================================================

    map_data = df_geo.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    st.write("Anzahl Firmen:", len(map_data))

    # =====================================================
    # OPENSTREETMAP
    # =====================================================

    m = folium.Map(

        location=[47.6, 13.5],

        zoom_start=7,

        tiles="OpenStreetMap"
    )

    # =====================================================
    # FARBEN
    # =====================================================

    def get_color(v):

        if pd.isna(v):
            return "#bdbdbd"

        elif v <= 2:
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

        value = row[variable]

        popup = f"""
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> {round(value,2) if pd.notna(value) else 'NA'}<br><br>

        <b>Latitude:</b> {row['latitude']}<br>
        <b>Longitude:</b> {row['longitude']}
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

            fill_color=get_color(value),

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
            index=0,
            key="corr_x"
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1,
            key="corr_y"
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
import numpy as np
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
# GOOGLE SHEETS LADEN
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
# SPALTEN NUMERISCH MACHEN
# =========================================================

for col in df_geo.columns:

    df_geo[col] = (
        df_geo[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

# =========================================================
# LATITUDE / LONGITUDE FIX
# =========================================================
# Deine Daten:
# 481593365 -> 48.1593365
# 16497746  -> 16.497746
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
# ALLE NUMERISCHEN VARIABLEN
# =========================================================

numeric_cols = [

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

for col in numeric_cols:

    if col in df_geo.columns:

        df_geo[col] = pd.to_numeric(
            df_geo[col],
            errors="coerce"
        )

# =========================================================
# KONSTRUKTE
# WICHTIG:
# skipna=True sorgt dafür,
# dass NICHT die ganze Firma NA wird
# =========================================================

df_geo["VI_Mittelwert"] = df_geo[
    [
        "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
        "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
        "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
    ]
].mean(axis=1, skipna=True)

df_geo["VI_Closing"] = df_geo[
    ["Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"]
].mean(axis=1, skipna=True)

df_geo["VI_Slowing"] = df_geo[
    ["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5","Q9 NEU_6","Q9 NEU_7"]
].mean(axis=1, skipna=True)

df_geo["Ökonomische_Performance"] = df_geo[
    ["Q161_1","Q161_2","Q161_3","Q161_4","Q161_5","Q161_6"]
].mean(axis=1, skipna=True)

df_geo["Ökologische_Performance"] = df_geo[
    [
        "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
        "Q16_6","Q16_7","Q16_8","Q16_9",
        "Q16_10","Q16_11","Q16_12","Q16_13"
    ]
].mean(axis=1, skipna=True)

df_geo["Loop_Closure"] = df_geo[
    ["Q14_1","Q14_2"]
].mean(axis=1, skipna=True)

df_geo["Open_Loops"] = df_geo[
    ["Q14_3","Q14_4","Q14_5"]
].mean(axis=1, skipna=True)

df_geo["Austausch"] = df_geo[
    ["Q15_1","Q15_2"]
].mean(axis=1, skipna=True)

df_geo["Erkenntnisse"] = df_geo[
    ["Q15_3","Q15_4","Q15_5","Q15_6","Q15_7"]
].mean(axis=1, skipna=True)

df_geo["Legitimität"] = df_geo[
    ["Q5_3","Q5_16","Q5_18","Q5_19","Q5_20"]
].mean(axis=1, skipna=True)

df_geo["Externer_Druck"] = df_geo[
    ["Q5_5","Q5_6","Q5_7"]
].mean(axis=1, skipna=True)

df_geo["Strategische_Integration"] = df_geo[
    ["Q6_1","Q6_2","Q6_3","Q6_4",
     "Q6_5","Q6_6","Q6_7","Q6_8"]
].mean(axis=1, skipna=True)

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
    alle_variablen,
    key="variable_selectbox"
)

radius = st.sidebar.slider(
    "Punktgröße",
    min_value=3,
    max_value=20,
    value=8,
    key="radius_slider"
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

    # =====================================================
    # NUR KOORDINATEN MÜSSEN VORHANDEN SEIN
    # =====================================================

    map_data = df_geo.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    # =====================================================
    # ÖSTERREICH FILTER
    # =====================================================

    map_data = map_data[
        (map_data["latitude"] > 46) &
        (map_data["latitude"] < 49.5) &
        (map_data["longitude"] > 9) &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen:", len(map_data))

    # =====================================================
    # KARTE
    # =====================================================

    m = folium.Map(

        location=[47.6, 13.5],

        zoom_start=7,

        tiles="OpenStreetMap"
    )

    # =====================================================
    # FARBEN
    # =====================================================

    def get_color(v):

        if pd.isna(v):
            return "#bdbdbd"

        elif v <= 2:
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
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> {row[variable]}<br><br>

        <b>Latitude:</b> {row['latitude']}<br>
        <b>Longitude:</b> {row['longitude']}
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
            index=0,
            key="corr_x"
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1,
            key="corr_y"
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
    )# =========================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px

from streamlit_folium import st_folium
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

# =========================================================
# GOOGLE SHEET LADEN
# =========================================================

sheet = client.open_by_key(
    "1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY"
).sheet1

data = sheet.get_all_records()

df = pd.DataFrame(data)

# =========================================================
# LEERE WERTE
# =========================================================

df = df.replace("", np.nan)

# =========================================================
# KOORDINATEN FIXEN
# =========================================================

def fix_coordinates(x):

    if pd.isna(x):
        return np.nan

    x = str(x).replace(",", ".")

    try:
        x = float(x)

    except:
        return np.nan

    # Falls Komma fehlt
    if x > 1000:
        x = x / 1000000

    return x

df["latitude"] = df["latitude"].apply(fix_coordinates)
df["longitude"] = df["longitude"].apply(fix_coordinates)

# =========================================================
# NUMERISCHE SPALTEN
# =========================================================

numeric_columns = [

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

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================================================
# HILFSFUNKTIONEN
# =========================================================

def safe_mean(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].mean(
        axis=1,
        skipna=True
    )

def safe_sum(columns):

    cols = [c for c in columns if c in df.columns]

    return df[cols].sum(
        axis=1,
        skipna=True
    )

# =========================================================
# KONSTRUKTE
# =========================================================

df["VI_Mittelwert"] = safe_mean([
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Closing"] = safe_mean([
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])

df["VI_Slowing"] = safe_mean([
    "Q9 NEU_3","Q9 NEU_4","Q9 NEU_5",
    "Q9 NEU_6","Q9 NEU_7"
])

df["Ökonomische_Performance"] = safe_mean([
    "Q161_1","Q161_2","Q161_3",
    "Q161_4","Q161_5","Q161_6"
])

df["Ökologische_Performance"] = safe_mean([
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9",
    "Q16_10","Q16_11","Q16_12","Q16_13"
])

df["Produktlebensdauer"] = safe_mean([
    "Q16_3","Q16_4"
])

df["Toxische_Freisetzung"] = safe_mean([
    "Q16_6","Q16_7"
])

df["Loop_Closure"] = safe_mean([
    "Q14_1","Q14_2"
])

df["Open_Loops"] = safe_mean([
    "Q14_3","Q14_4","Q14_5"
])

df["Austausch"] = safe_mean([
    "Q15_1","Q15_2"
])

df["Erkenntnisse"] = safe_mean([
    "Q15_3","Q15_4","Q15_5",
    "Q15_6","Q15_7"
])

df["Legitimität"] = safe_mean([
    "Q5_3","Q5_16","Q5_18",
    "Q5_19","Q5_20"
])

df["Externer_Druck"] = safe_mean([
    "Q5_5","Q5_6","Q5_7"
])

df["Lern_und_Kooperationsorientierung"] = safe_mean([
    "Q5_12","Q5_13","Q5_14",
    "Q5_15","Q5_17"
])

df["Differenzierungs_Wettbewerbsorientierung"] = safe_mean([
    "Q5_4","Q5_8","Q5_9","Q5_10"
])

df["Strategische_Integration"] = safe_mean([
    "Q6_1","Q6_2","Q6_3","Q6_4",
    "Q6_5","Q6_6","Q6_7","Q6_8"
])

df["Anzahl_Rstrategien"] = df["Q8_Anzahl_Rstrategien"]

df["Anzahl_Closing_Strategien"] = safe_sum([
    "Q8_NEU_9","Q8_NEU_10",
    "Q8_NEU_11","Q8_NEU_12"
])

df["Anzahl_Slowing_Strategien"] = safe_sum([
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5",
    "Q8_NEU_6","Q8_NEU_7","Q8_NEU_8"
])

df["Firmengröße"] = df["Q41"]
df["Firmenalter"] = df["Q42"]

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
    "Anzahl_Closing_Strategien",
    "Anzahl_Slowing_Strategien",

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

    map_data = df.dropna(
        subset=["latitude", "longitude", variable]
    ).copy()

    # Österreich Filter
    map_data = map_data[
        (map_data["latitude"] > 46) &
        (map_data["latitude"] < 49.5) &
        (map_data["longitude"] > 9) &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen auf Karte:", len(map_data))

    # =====================================================
    # KARTE
    # =====================================================

    m = folium.Map(
        location=[47.6, 14.5],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # =====================================================
    # FARBEN
    # =====================================================

    vi_variablen = [
        "VI_Mittelwert",
        "VI_Closing",
        "VI_Slowing"
    ]

    def get_color(v):

        if pd.isna(v):
            return "gray"

        if variable in vi_variablen:

            if v <= 2:
                return "#d73027"
            elif v <= 3:
                return "#fc8d59"
            elif v <= 4:
                return "#fee08b"
            elif v <= 5:
                return "#91cf60"
            elif v <= 6:
                return "#66bd63"
            else:
                return "#1a9850"

        else:

            if v <= 2:
                return "#d73027"
            elif v <= 3:
                return "#fc8d59"
            elif v <= 4:
                return "#fee08b"
            else:
                return "#1a9850"

    # =====================================================
    # LEGENDE
    # =====================================================

    if variable in vi_variablen:

        legend_html = f"""
        <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index:9999;
        background:white;
        padding:15px;
        border:2px solid grey;
        border-radius:10px;
        font-size:14px;
        ">

        <b>{variable}</b><br><br>

        <div style="background:#d73027;width:20px;height:20px;display:inline-block;"></div> 1-2<br>
        <div style="background:#fc8d59;width:20px;height:20px;display:inline-block;"></div> 2-3<br>
        <div style="background:#fee08b;width:20px;height:20px;display:inline-block;"></div> 3-4<br>
        <div style="background:#91cf60;width:20px;height:20px;display:inline-block;"></div> 4-5<br>
        <div style="background:#66bd63;width:20px;height:20px;display:inline-block;"></div> 5-6<br>
        <div style="background:#1a9850;width:20px;height:20px;display:inline-block;"></div> 6-7

        </div>
        """

    else:

        legend_html = f"""
        <div style="
        position: fixed;
        bottom: 40px;
        right: 40px;
        z-index:9999;
        background:white;
        padding:15px;
        border:2px solid grey;
        border-radius:10px;
        font-size:14px;
        ">

        <b>{variable}</b><br><br>

        <div style="background:#d73027;width:20px;height:20px;display:inline-block;"></div> 1-2<br>
        <div style="background:#fc8d59;width:20px;height:20px;display:inline-block;"></div> 2-3<br>
        <div style="background:#fee08b;width:20px;height:20px;display:inline-block;"></div> 3-4<br>
        <div style="background:#1a9850;width:20px;height:20px;display:inline-block;"></div> 4-5

        </div>
        """

    # =====================================================
    # PUNKTE
    # =====================================================

    for _, row in map_data.iterrows():

        # Firmenname
        firma = row.get("Zugehörigkeit", "Keine Angabe")

        popup = f"""
        <b>Firma:</b> {firma}<br><br>

        <b>Variable:</b> {variable}<br>

        <b>Wert:</b> {round(row[variable],2)}
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
            fill_opacity=0.85
        ).add_to(m)

    # Legende hinzufügen
    m.get_root().html.add_child(
        folium.Element(legend_html)
    )

    # Karte anzeigen
    st_folium(
        m,
        width=1400,
        height=850
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
            key="corr_x"
        )

    with col2:

        corr_y = st.selectbox(
            "Variable Y",
            alle_variablen,
            index=1,
            key="corr_y"
        )

    corr_data = df[
        [corr_x, corr_y]
    ].dropna()

    if len(corr_data) > 2:

        corr, pval = pearsonr(
            corr_data[corr_x],
            corr_data[corr_y]
        )

        st.metric(
            "Pearson r",
            round(corr, 3)
        )

        st.metric(
            "p-Wert",
            round(pval, 5)
        )

        fig = px.scatter(
            corr_data,
            x=corr_x,
            y=corr_y,
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
        df,
        use_container_width=True,
        height=900
    )
