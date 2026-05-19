# =============================================================
# STREAMLIT DASHBOARD
# Unternehmensanalyse Österreich
# =============================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.graph_objects as go

from streamlit_folium import st_folium
from scipy.stats import pearsonr
import statsmodels.api as sm

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
    if 40 <= x <= 50:
        return x
    if x > 1000000:
        return x / 10000000
    return x

df["latitude"]  = df["latitude"].apply(fix_coordinates)
df["longitude"] = df["longitude"].apply(fix_coordinates)

# =========================================================
# NUMERISCHE SPALTEN
# =========================================================

numeric_columns = [
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12",
    "Q161_1","Q161_2","Q161_3","Q161_4","Q161_5","Q161_6",
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5",
    "Q16_6","Q16_7","Q16_8","Q16_9","Q16_10",
    "Q16_11","Q16_12","Q16_13",
    "Q14_1","Q14_2","Q14_3","Q14_4","Q14_5",
    "Q15_1","Q15_2","Q15_3","Q15_4","Q15_5","Q15_6","Q15_7",
    "Q5_3","Q5_4","Q5_5","Q5_6","Q5_7",
    "Q5_8","Q5_9","Q5_10","Q5_12","Q5_13",
    "Q5_14","Q5_15","Q5_16","Q5_17","Q5_18","Q5_19","Q5_20",
    "Q6_1","Q6_2","Q6_3","Q6_4","Q6_5","Q6_6","Q6_7","Q6_8",
    "Q8_Anzahl_Rstrategien",
    "Q8_NEU_3","Q8_NEU_4","Q8_NEU_5","Q8_NEU_6","Q8_NEU_7",
    "Q8_NEU_8","Q8_NEU_9","Q8_NEU_10","Q8_NEU_11","Q8_NEU_12",
    "Q41","Q42",
    "Q12_1","Q12_2","Q12_3","Q12_4","Q12_5",
    "Q12_6","Q12_7","Q12_8",
    "Q12_9","Q12_10","Q12_11","Q12_12",
    "Q13_1","Q13_2","Q13_3",
    "Q13_4","Q13_5","Q13_6","Q13_7"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================================================
# KONSTRUKTE
# =========================================================

def safe_mean(columns):
    cols = [c for c in columns if c in df.columns]
    if not cols:
        return pd.Series(np.nan, index=df.index)
    return df[cols].mean(axis=1, skipna=True)

def safe_sum(columns):
    cols = [c for c in columns if c in df.columns]
    if not cols:
        return pd.Series(np.nan, index=df.index)
    return df[cols].sum(axis=1, skipna=True)

# --- VI ---
df["VI_Mittelwert"] = safe_mean([
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])
df["VI_Closing"] = safe_mean(["Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"])
df["VI_Slowing"] = safe_mean(["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5","Q9 NEU_6","Q9 NEU_7"])

# --- Q12 ---
df["Langlebigkeit_Repairability"]   = safe_mean(["Q12_1","Q12_2","Q12_3","Q12_4","Q12_5"])
df["Design_for_Recycling"]          = safe_mean(["Q12_6","Q12_7"])
df["Gesundheit_Materialien"]        = safe_mean(["Q12_8"])
df["Design_Biologischer_Kreislauf"] = safe_mean(["Q12_9","Q12_10","Q12_11","Q12_12"])

# --- Q13 ---
df["Nutzungsorientierte_Geschäftsmodelle"] = safe_mean(["Q13_4","Q13_5","Q13_6","Q13_7"])
df["Kokreative_Dienstleistungsmodelle"]    = safe_mean(["Q13_1","Q13_2","Q13_3"])

# --- Q8 ---
df["Anzahl_Rstrategien"]        = df["Q8_Anzahl_Rstrategien"] if "Q8_Anzahl_Rstrategien" in df.columns else np.nan
df["Anzahl_Closing_Strategien"] = safe_sum(["Q8_NEU_9","Q8_NEU_10","Q8_NEU_11","Q8_NEU_12"])
df["Anzahl_Slowing_Strategien"] = safe_sum(["Q8_NEU_3","Q8_NEU_4","Q8_NEU_5","Q8_NEU_6","Q8_NEU_7","Q8_NEU_8"])

# --- Q6 ---
df["Strategische_Integration"] = safe_mean(["Q6_1","Q6_2","Q6_3","Q6_4","Q6_5","Q6_6","Q6_7","Q6_8"])

# --- Q5 ---
df["Legitimität"]                              = safe_mean(["Q5_3","Q5_16","Q5_18","Q5_19","Q5_20"])
df["Externer_Druck"]                           = safe_mean(["Q5_5","Q5_6","Q5_7"])
df["Lern_und_Kooperationsorientierung"]        = safe_mean(["Q5_12","Q5_13","Q5_14","Q5_15","Q5_17"])
df["Differenzierungs_Wettbewerbsorientierung"] = safe_mean(["Q5_4","Q5_8","Q5_9","Q5_10"])

# --- Q15 ---
df["Austausch"]    = safe_mean(["Q15_1","Q15_2"])
df["Erkenntnisse"] = safe_mean(["Q15_3","Q15_4","Q15_5","Q15_6","Q15_7"])

# --- Q14 ---
df["Loop_Closure"] = safe_mean(["Q14_1","Q14_2"])
df["Open_Loops"]   = safe_mean(["Q14_3","Q14_4","Q14_5"])

# --- Q16 ---
df["Produktlebensdauer"]      = safe_mean(["Q16_3","Q16_4"])
df["Toxische_Freisetzung"]    = safe_mean(["Q16_6","Q16_7"])
df["Ökologische_Performance"] = safe_mean([
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5","Q16_6","Q16_7",
    "Q16_8","Q16_9","Q16_10","Q16_11","Q16_12","Q16_13"
])

# --- Q161 ---
df["Ökonomische_Performance"] = safe_mean(["Q161_1","Q161_2","Q161_3","Q161_4","Q161_5","Q161_6"])

# --- Firma ---
df["Firmengröße"] = df["Q41"] if "Q41" in df.columns else np.nan
df["Firmenalter"] = df["Q42"] if "Q42" in df.columns else np.nan

# =========================================================
# VARIABLEN — geordnet
# =========================================================

alle_variablen = [
    "VI_Mittelwert", "VI_Closing", "VI_Slowing",
    "Langlebigkeit_Repairability", "Design_for_Recycling",
    "Gesundheit_Materialien", "Design_Biologischer_Kreislauf",
    "Nutzungsorientierte_Geschäftsmodelle", "Kokreative_Dienstleistungsmodelle",
    "Anzahl_Rstrategien", "Anzahl_Closing_Strategien", "Anzahl_Slowing_Strategien",
    "Strategische_Integration",
    "Legitimität", "Externer_Druck",
    "Lern_und_Kooperationsorientierung", "Differenzierungs_Wettbewerbsorientierung",
    "Austausch", "Erkenntnisse",
    "Loop_Closure", "Open_Loops",
    "Produktlebensdauer", "Toxische_Freisetzung", "Ökologische_Performance",
    "Ökonomische_Performance",
    "Firmengröße", "Firmenalter"
]

vi_variablen = ["VI_Mittelwert", "VI_Closing", "VI_Slowing"]

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
    "Punktgröße", 3, 20, 8,
    key="radius_slider"
)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Karte",
    "Deskriptive Statistik",
    "Korrelationen & Heatmap",
    "Regression",
    "Fehlende Werte",
    "Datentabelle"
])

# =========================================================
# TAB 1 — KARTE
# =========================================================

with tab1:

    st.subheader("Unternehmenskarte Österreich")

    # Alle Firmen mit gültigen Koordinaten in Österreich
    coords_mask = (
        df["latitude"].notna() &
        df["longitude"].notna() &
        (df["latitude"]  > 46)   &
        (df["latitude"]  < 49.5) &
        (df["longitude"] > 9)    &
        (df["longitude"] < 18.5)
    )
    df_map = df[coords_mask].copy()

    # Aufteilen: mit Wert vs. NA für gewählte Variable
    map_data_colored = df_map[df_map[variable].notna()].copy()
    map_data_na      = df_map[df_map[variable].isna()].copy()

    col_info1, col_info2 = st.columns(2)
    col_info1.metric("Firmen mit Wert",       len(map_data_colored))
    col_info2.metric("Firmen ohne Wert (NA)", len(map_data_na))

    m = folium.Map(location=[47.6, 14.5], zoom_start=7, tiles="OpenStreetMap")

    # --------------------------------------------------
    # FARBEN + LEGENDE
    # --------------
