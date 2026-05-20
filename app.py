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
import time

from streamlit_folium import st_folium
from scipy.stats import pearsonr
import statsmodels.api as sm

import gspread
from gspread.exceptions import APIError
from google.oauth2.service_account import Credentials

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CVCS Dashboard",
    layout="wide"
)

st.title("CVCS Dashboard")

# =========================================================
# GOOGLE SHEETS — ROBUSTE VERBINDUNG MIT RETRY + CACHE
# =========================================================

@st.cache_data(ttl=300)   # 5 Minuten Cache → verhindert Quota-Fehler bei Reload
def lade_daten():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    client = gspread.authorize(creds)

    # Retry-Logik: bis zu 4 Versuche mit exponential backoff
    max_versuche = 4
    for versuch in range(max_versuche):
        try:
            sheet = client.open_by_key(
                "1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY"
            ).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except APIError as e:
            if versuch < max_versuche - 1:
                wartezeit = 2 ** versuch   # 1s, 2s, 4s
                time.sleep(wartezeit)
            else:
                raise e

# Daten laden — Fehler abfangen und anzeigen
try:
    df = lade_daten()
except APIError as e:
    st.error(
        "❌ Google Sheets konnte nicht geladen werden. "
        "Bitte Seite neu laden oder die Google API-Berechtigungen prüfen.\n\n"
        f"Details: {str(e)}"
    )
    st.stop()
except Exception as e:
    st.error(f"❌ Unbekannter Fehler beim Laden der Daten: {str(e)}")
    st.stop()

# =========================================================
# LEERE STRINGS -> NA
# =========================================================

df = df.replace("", np.nan)

# =========================================================
# KOORDINATEN FIX — getrennt für lat / lon
# =========================================================

def fix_coord(x, valid_min, valid_max):
    """
    Bereinigt einen Koordinatenwert.
    - Komma -> Punkt
    - Falls bereits im gültigen Bereich: direkt zurück
    - Falls skaliert gespeichert (z.B. 477500000 statt 47.75): durch 10^7 teilen
    - Versuch mit 10^6-Skalierung als Fallback
    - Sonst NaN
    """
    if pd.isna(x):
        return np.nan
    x = str(x).replace(",", ".")
    try:
        x = float(x)
    except:
        return np.nan
    if valid_min <= x <= valid_max:
        return x
    scaled7 = x / 10_000_000
    if valid_min <= scaled7 <= valid_max:
        return scaled7
    scaled6 = x / 1_000_000
    if valid_min <= scaled6 <= valid_max:
        return scaled6
    return np.nan

df["latitude"]  = df["latitude"].apply(lambda x: fix_coord(x, 46.0, 49.5))
df["longitude"] = df["longitude"].apply(lambda x: fix_coord(x,  9.0, 18.5))

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
df["Design_Biologischer_Kreislauf"] = safe_mean(["Q12_9","Q12_10","Q12_11","Q12_12"])

# --- Q13 ---
df["Nutzungsorientierte_PSS"] = safe_mean(["Q13_4","Q13_5","Q13_6","Q13_7"])
df["Integrierte_PSS"]         = safe_mean(["Q13_1","Q13_2","Q13_3"])

# --- Q8 ---
df["Anzahl_Rstrategien"]        = df["Q8 Anzahl R-Strategien (Fr. 8)"] if "Q8 Anzahl R-Strategien (Fr. 8)" in df.columns else np.nan
df["Anzahl_Closing_Strategien"] = df["Anzahl_Closing_Strategien"]      if "Anzahl_Closing_Strategien"      in df.columns else np.nan
df["Anzahl_Slowing_Strategien"] = df["Anzahl_Slowing_Strategien"]      if "Anzahl_Slowing_Strategien"      in df.columns else np.nan

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
    "Strategische_Integration",
    "Legitimität", "Externer_Druck",
    "Lern_und_Kooperationsorientierung",
    "Differenzierungs_Wettbewerbsorientierung",
    "Langlebigkeit_Repairability", "Design_for_Recycling",
    "Design_Biologischer_Kreislauf",
    "Nutzungsorientierte_PSS", "Integrierte_PSS",
    "Anzahl_Rstrategien", "Anzahl_Closing_Strategien", "Anzahl_Slowing_Strategien",
    "Austausch", "Erkenntnisse",
    "Loop_Closure", "Open_Loops",
    "Produktlebensdauer", "Toxische_Freisetzung", "Ökologische_Performance",
    "Ökonomische_Performance",
    "Firmengröße", "Firmenalter"
]

vi_variablen = ["VI_Mittelwert", "VI_Closing", "VI_Slowing"]

# =========================================================
# LEGENDE — Konfiguration pro Variable
# =========================================================

LEGENDE_CONFIG = {
    "Anzahl_Rstrategien": {
        "stufen": [
            (1,  "#ffffcc", "1"),
            (2,  "#ffeda0", "2"),
            (3,  "#fed976", "3"),
            (4,  "#feb24c", "4"),
            (5,  "#fd8d3c", "5"),
            (6,  "#fc4e2a", "6"),
            (7,  "#e31a1c", "7"),
            (8,  "#bd0026", "8"),
            (9,  "#800026", "9"),
            (10, "#6b0020", "10"),
            (11, "#4d0015", "11"),
            (12, "#2d000c", "12"),
        ]
    },
    "Anzahl_Closing_Strategien": {
        "stufen": [
            (1, "#fee5d9", "1"),
            (2, "#fcae91", "2"),
            (3, "#fb6a4a", "3"),
            (4, "#cb181d", "4"),
        ]
    },
    "Anzahl_Slowing_Strategien": {
        "stufen": [
            (1, "#edf8e9", "1"),
            (2, "#bae4b3", "2"),
            (3, "#74c476", "3"),
            (4, "#31a354", "4"),
            (5, "#006d2c", "5"),
            (6, "#00441b", "6"),
        ]
    },
    "Firmenalter": {
        "stufen": [
            (1, "#ffffcc", "1  –  unter 5 Jahre"),
            (2, "#a1dab4", "2  –  5–9 Jahre"),
            (3, "#41b6c4", "3  –  10–49 Jahre"),
            (4, "#225ea8", "4  –  50+ Jahre"),
        ]
    },
    "Firmengröße": {
        "stufen": [
            (1, "#f7fbff", "1  –  1–9 MA"),
            (2, "#c6dbef", "2  –  10–49 MA"),
            (3, "#6baed6", "3  –  50–249 MA"),
            (4, "#2171b5", "4  –  250–499 MA"),
            (5, "#08306b", "5  –  500+ MA"),
        ]
    },
}

# =========================================================
# FARB-FUNKTIONEN & LEGENDE
# =========================================================

def get_color_and_legend(variable):
    if variable in vi_variablen:
        def color_fn(v):
            if v <= 1:   return "#b2182b"
            elif v <= 2: return "#d6604d"
            elif v <= 3: return "#f4a582"
            elif v <= 4: return "#fddbc7"
            elif v <= 5: return "#92c5de"
            elif v <= 6: return "#4393c3"
            else:        return "#2166ac"
        legend = f"""
        <div style="position:fixed;bottom:40px;right:40px;z-index:9999;
        background-color:white;padding:15px;border:2px solid grey;
        border-radius:10px;font-size:14px;">
        <b>{variable}</b><br><br>
        <div style="background:#b2182b;width:20px;height:20px;display:inline-block;"></div> 1<br>
        <div style="background:#d6604d;width:20px;height:20px;display:inline-block;"></div> 2<br>
        <div style="background:#f4a582;width:20px;height:20px;display:inline-block;"></div> 3<br>
        <div style="background:#fddbc7;width:20px;height:20px;display:inline-block;"></div> 4<br>
        <div style="background:#92c5de;width:20px;height:20px;display:inline-block;"></div> 5<br>
        <div style="background:#4393c3;width:20px;height:20px;display:inline-block;"></div> 6<br>
        <div style="background:#2166ac;width:20px;height:20px;display:inline-block;"></div> 7<br><br>
        <div style="background:#aaaaaa;width:20px;height:20px;display:inline-block;"></div> kein Wert (NA)
        </div>"""
        return color_fn, legend

    elif variable in LEGENDE_CONFIG:
        stufen = LEGENDE_CONFIG[variable]["stufen"]
        def color_fn(v):
            for schwelle, farbe, _ in stufen:
                if v <= schwelle:
                    return farbe
            return stufen[-1][1]
        stufen_html = "".join(
            f'<div style="background:{farbe};width:20px;height:20px;display:inline-block;"></div> {label}<br>'
            for _, farbe, label in stufen
        )
        legend = f"""
        <div style="position:fixed;bottom:40px;right:40px;z-index:9999;
        background-color:white;padding:15px;border:2px solid grey;
        border-radius:10px;font-size:14px;max-height:400px;overflow-y:auto;">
        <b>{variable}</b><br><br>
        {stufen_html}
        <br><div style="background:#aaaaaa;width:20px;height:20px;display:inline-block;"></div> kein Wert (NA)
        </div>"""
        return color_fn, legend

    else:
        def color_fn(v):
            if v <= 1:   return "#d73027"
            elif v <= 2: return "#fc8d59"
            elif v <= 3: return "#fee08b"
            elif v <= 4: return "#91cf60"
            else:        return "#1a9850"
        legend = f"""
        <div style="position:fixed;bottom:40px;right:40px;z-index:9999;
        background-color:white;padding:15px;border:2px solid grey;
        border-radius:10px;font-size:14px;">
        <b>{variable}</b><br><br>
        <div style="background:#d73027;width:20px;height:20px;display:inline-block;"></div> 1<br>
        <div style="background:#fc8d59;width:20px;height:20px;display:inline-block;"></div> 2<br>
        <div style="background:#fee08b;width:20px;height:20px;display:inline-block;"></div> 3<br>
        <div style="background:#91cf60;width:20px;height:20px;display:inline-block;"></div> 4<br>
        <div style="background:#1a9850;width:20px;height:20px;display:inline-block;"></div> 5<br><br>
        <div style="background:#aaaaaa;width:20px;height:20px;display:inline-block;"></div> kein Wert (NA)
        </div>"""
        return color_fn, legend

# =========================================================
# HILFSFUNKTION — Stufen für Filter-Checkboxen
# =========================================================

def get_stufen_fuer_variable(var):
    if var in vi_variablen:
        farben = ["#b2182b","#d6604d","#f4a582","#fddbc7","#92c5de","#4393c3","#2166ac"]
        return [(i+1, farben[i], str(i+1)) for i in range(7)]
    elif var in LEGENDE_CONFIG:
        return LEGENDE_CONFIG[var]["stufen"]
    else:
        farben = ["#d73027","#fc8d59","#fee08b","#91cf60","#1a9850"]
        return [(i+1, farben[i], str(i+1)) for i in range(5)]

def stufe_fuer_wert(v, stufen):
    for schwelle, _, _ in stufen:
        if v <= schwelle:
            return schwelle
    return stufen[-1][0]

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

# --- Filter-Checkboxen je Stufe ---
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Filter: {variable}**")

alle_stufen = get_stufen_fuer_variable(variable)

alle_an = st.sidebar.checkbox("Alle Stufen anzeigen", value=True, key="filter_alle")

aktive_stufen = set()
for schwelle, farbe, label in alle_stufen:
    cb = st.sidebar.checkbox(
        label,
        value=alle_an,
        key=f"filter_{variable}_{schwelle}",
        disabled=alle_an
    )
    if alle_an or cb:
        aktive_stufen.add(schwelle)

# NA-Firmen anzeigen?
show_na = st.sidebar.checkbox("Firmen ohne Wert (NA) anzeigen", value=True, key="filter_na")

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
        (df["latitude"]  >= 46.0) &
        (df["latitude"]  <= 49.5) &
        (df["longitude"] >=  9.0) &
        (df["longitude"] <= 18.5)
    )
    df_map = df[coords_mask].copy()

    # Firmen ohne Koordinaten
    n_ohne_koordinaten = df["latitude"].isna().sum()

    # Aufteilen: mit Wert vs. NA für gewählte Variable
    map_data_all = df_map[df_map[variable].notna()].copy()
    map_data_na  = df_map[df_map[variable].isna()].copy()

    # Filter anwenden
    if not alle_an:
        map_data_colored = map_data_all[
            map_data_all[variable].apply(
                lambda v: stufe_fuer_wert(v, alle_stufen) in aktive_stufen
            )
        ].copy()
    else:
        map_data_colored = map_data_all.copy()

    # Anzahl aktuell sichtbarer Firmen
    n_sichtbar_farbig = len(map_data_colored)
    n_sichtbar_na     = len(map_data_na) if show_na else 0
    n_sichtbar_gesamt = n_sichtbar_farbig + n_sichtbar_na

    # --------------------------------------------------
    # METRIKEN — ganz oben, live aktualisiert
    # --------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🗺️ Firmen gesamt auf Karte",        len(df_map))
    m2.metric("✅ Aktuell angezeigte Firmen",        n_sichtbar_gesamt)
    m3.metric(f"🎨 Davon mit Wert ({variable[:20]}…)" if len(variable) > 20 else f"🎨 Davon mit Wert",
              n_sichtbar_farbig)
    m4.metric("❌ Ohne Koordinaten (nicht kartierbar)", n_ohne_koordinaten)

    st.markdown("---")

    # --------------------------------------------------
    # KARTE
    # --------------------------------------------------
    m = folium.Map(location=[47.6, 14.5], zoom_start=7, tiles="OpenStreetMap")

    get_color, legend_html = get_color_and_legend(variable)

    # Marker — farbig (gefilterte Firmen mit Wert)
    for idx, row in map_data_colored.iterrows():
        firma = row["Zugehörigkeit"] if "Zugehörigkeit" in row and pd.notna(row["Zugehörigkeit"]) else "k.A."
        popup_text = (
            f"<b>Firma:</b> {firma}<br>"
            f"<b>Variable:</b> {variable}<br>"
            f"<b>Wert:</b> {round(row[variable], 2)}<br>"
            f"<hr style='margin:6px 0'>"
            f"<small style='color:#555'>Zeilen-ID: {idx}</small><br>"
            f"<a href='#datensatz_{idx}' "
            f"style='font-size:12px;color:#1a73e8;text-decoration:none;font-weight:bold;'>"
            f"📋 Zum Datensatz springen</a>"
        )
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color="black", weight=1,
            fill=True,
            fill_color=get_color(row[variable]),
            fill_opacity=0.9,
            popup=folium.Popup(popup_text, max_width=280)
        ).add_to(m)

    # Marker — grau (NA) — nur wenn show_na aktiv
    if show_na:
        for idx, row in map_data_na.iterrows():
            firma = row["Zugehörigkeit"] if "Zugehörigkeit" in row and pd.notna(row["Zugehörigkeit"]) else "k.A."
            popup_text = (
                f"<b>Firma:</b> {firma}<br>"
                f"<b>Variable:</b> {variable}<br>"
                f"<b>Wert:</b> kein Wert (NA)<br>"
                f"<hr style='margin:6px 0'>"
                f"<small style='color:#555'>Zeilen-ID: {idx}</small><br>"
                f"<a href='#datensatz_{idx}' "
                f"style='font-size:12px;color:#1a73e8;text-decoration:none;font-weight:bold;'>"
                f"📋 Zum Datensatz springen</a>"
            )
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=radius,
                color="black", weight=1,
                fill=True,
                fill_color="#aaaaaa",
                fill_opacity=0.7,
                popup=folium.Popup(popup_text, max_width=280)
            ).add_to(m)

    m.get_root().html.add_child(folium.Element(legend_html))

    # st_folium gibt last_object_clicked_popup zurück wenn ein Marker angeklickt wird
    karten_klick = st_folium(m, width=1400, height=850, returned_objects=["last_object_clicked_popup"])

    # Geklickten Index aus Popup-Text extrahieren und in session_state speichern
    if karten_klick and karten_klick.get("last_object_clicked_popup"):
        popup_inhalt = karten_klick["last_object_clicked_popup"]
        # Zeilen-ID aus Popup-Text parsen
        import re
        treffer = re.search(r"Zeilen-ID:\s*(\d+)", popup_inhalt)
        if treffer:
            st.session_state["angeklickte_firma_idx"] = int(treffer.group(1))

    # Hinweis wenn eine Firma angeklickt wurde
    if "angeklickte_firma_idx" in st.session_state:
        idx_sel = st.session_state["angeklickte_firma_idx"]
        firma_sel = df.loc[idx_sel, "Zugehörigkeit"] if "Zugehörigkeit" in df.columns and pd.notna(df.loc[idx_sel, "Zugehörigkeit"]) else "k.A."
        st.info(
            f"📌 Zuletzt angeklickt: **{firma_sel}** (Zeile {idx_sel}) — "
            f"Tab **'Datentabelle'** öffnen um die Zeile hervorzuheben.",
            icon=None
        )

# =========================================================
# TAB 2 — DESKRIPTIVE STATISTIK
# =========================================================

with tab2:

    st.subheader("Deskriptive Statistik")

    desc_vars = st.multiselect(
        "Variablen auswählen",
        alle_variablen,
        default=alle_variablen[:6],
        key="desc_vars"
    )

    if desc_vars:

        desc_df = df[desc_vars].describe().T
        desc_df["missing"]   = df[desc_vars].isna().sum().values
        desc_df["missing_%"] = (df[desc_vars].isna().mean() * 100).round(1).values
        desc_df["Schiefe"]   = df[desc_vars].skew()
        desc_df["Wölbung"]   = df[desc_vars].kurtosis()
        desc_df = desc_df.drop(columns=["min", "25%", "75%"])

        desc_df = desc_df.rename(columns={
            "count": "N",
            "mean":  "Mittelwert",
            "std":   "Std.-Abw.",
            "50%":   "Median",
            "max":   "Max"
        })

        st.dataframe(desc_df.round(3), use_container_width=True)

        st.markdown("---")
        st.subheader("Histogramm / Verteilung")

        hist_var = st.selectbox(
            "Variable für Histogramm",
            desc_vars,
            key="hist_var"
        )

        fig_hist = px.histogram(
            df[hist_var].dropna(),
            x=hist_var, nbins=20, marginal="box",
            title=f"Verteilung: {hist_var}",
            color_discrete_sequence=["#4393c3"]
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# =========================================================
# TAB 3 — KORRELATIONEN & HEATMAP
# =========================================================

with tab3:

    st.subheader("Pearson-Korrelation (Paarweise)")

    col1, col2 = st.columns(2)
    with col1:
        corr_x = st.selectbox("Variable X", alle_variablen, key="corr_x")
    with col2:
        corr_y = st.selectbox("Variable Y", alle_variablen, index=1, key="corr_y")

    corr_data = df[[corr_x, corr_y]].dropna()

    if len(corr_data) > 2:
        corr_val, pval = pearsonr(corr_data[corr_x], corr_data[corr_y])
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Pearson r", round(corr_val, 3))
        mc2.metric("p-Wert",    round(pval, 5))
        mc3.metric("N",         len(corr_data))

        fig_scatter = px.scatter(
            corr_data, x=corr_x, y=corr_y,
            trendline="ols",
            title=f"Streudiagramm: {corr_x} vs. {corr_y}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.subheader("Korrelationsmatrix (Heatmap)")

    heatmap_vars = st.multiselect(
        "Variablen für Heatmap auswählen",
        alle_variablen,
        default=alle_variablen[:8],
        key="heatmap_vars"
    )

    if len(heatmap_vars) >= 2:

        corr_matrix = df[heatmap_vars].corr(method="pearson")

        fig_heat = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdYlGn",
            zmin=-1, zmax=1,
            title="Pearson-Korrelationsmatrix",
            aspect="auto"
        )
        fig_heat.update_layout(height=600, xaxis=dict(side="top"))
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("**Signifikanztabelle (p-Werte)**")

        pval_matrix = pd.DataFrame(index=heatmap_vars, columns=heatmap_vars, dtype=float)
        for v1 in heatmap_vars:
            for v2 in heatmap_vars:
                if v1 == v2:
                    pval_matrix.loc[v1, v2] = np.nan
                else:
                    tmp = df[[v1, v2]].dropna()
                    if len(tmp) > 2:
                        _, p = pearsonr(tmp[v1], tmp[v2])
                        pval_matrix.loc[v1, v2] = round(p, 4)
                    else:
                        pval_matrix.loc[v1, v2] = np.nan

        fig_pval = px.imshow(
            pval_matrix.astype(float),
            text_auto=".4f",
            color_continuous_scale=[
                [0.000, "#1a9850"],
                [0.010, "#91cf60"],
                [0.050, "#fee08b"],
                [0.100, "#fc8d59"],
                [1.000, "#d73027"],
            ],
            zmin=0, zmax=1,
            title="p-Werte (grün = signifikant, rot = nicht signifikant)",
            aspect="auto"
        )
        fig_pval.update_layout(
            height=600,
            xaxis=dict(side="top"),
            coloraxis_colorbar=dict(title="p-Wert")
        )
        st.plotly_chart(fig_pval, use_container_width=True)

    else:
        st.info("Bitte mindestens 2 Variablen auswählen.")

# =========================================================
# TAB 4 — REGRESSION
# =========================================================

with tab4:

    st.subheader("Multiple lineare Regression")

    reg_y = st.selectbox(
        "Zielvariable (Y)",
        alle_variablen,
        index=alle_variablen.index("Ökonomische_Performance"),
        key="reg_y"
    )

    reg_x_options = [v for v in alle_variablen if v != reg_y]

    reg_x = st.multiselect(
        "Prädiktoren (X)",
        reg_x_options,
        default=reg_x_options[:3],
        key="reg_x"
    )

    if reg_x:

        reg_data = df[[reg_y] + reg_x].dropna()

        if len(reg_data) > len(reg_x) + 1:

            X     = sm.add_constant(reg_data[reg_x])
            y_reg = reg_data[reg_y]
            model = sm.OLS(y_reg, X).fit()

            st.markdown(
                f"**N = {len(reg_data)} | "
                f"R² = {round(model.rsquared, 3)} | "
                f"adj. R² = {round(model.rsquared_adj, 3)} | "
                f"F-p = {round(model.f_pvalue, 5)}**"
            )

            # Standardisierte Koeffizienten (Beta)
            reg_data_std = reg_data.copy()
            for col in [reg_y] + reg_x:
                col_std = reg_data_std[col].std()
                if col_std > 0:
                    reg_data_std[col] = (reg_data_std[col] - reg_data_std[col].mean()) / col_std
                else:
                    reg_data_std[col] = 0.0

            X_std       = sm.add_constant(reg_data_std[reg_x])
            y_std       = reg_data_std[reg_y]
            model_std   = sm.OLS(y_std, X_std).fit()
            beta_series = model_std.params

            coef_df = pd.DataFrame({
                "Koeffizient": model.params,
                "Beta (std.)": beta_series,
                "Std.-Fehler": model.bse,
                "t-Wert":      model.tvalues,
                "p-Wert":      model.pvalues,
                "CI 2.5%":     model.conf_int()[0],
                "CI 97.5%":    model.conf_int()[1]
            }).round(4)

            pval_colors = []
            for p in coef_df["p-Wert"]:
                if p < 0.001:  pval_colors.append("#c6efce")
                elif p < 0.01: pval_colors.append("#d9ead3")
                elif p < 0.05: pval_colors.append("#fff2cc")
                elif p < 0.1:  pval_colors.append("#fce4d6")
                else:          pval_colors.append("#ffffff")

            fig_coef_table = go.Figure(data=[go.Table(
                header=dict(
                    values=["Prädiktor"] + list(coef_df.columns),
                    fill_color="#4393c3",
                    font=dict(color="white", size=12),
                    align="center"
                ),
                cells=dict(
                    values=[
                        coef_df.index.tolist(),
                        coef_df["Koeffizient"].tolist(),
                        coef_df["Beta (std.)"].tolist(),
                        coef_df["Std.-Fehler"].tolist(),
                        coef_df["t-Wert"].tolist(),
                        coef_df["p-Wert"].tolist(),
                        coef_df["CI 2.5%"].tolist(),
                        coef_df["CI 97.5%"].tolist(),
                    ],
                    fill_color=[
                        ["#f5f5f5"] * len(coef_df),
                        ["#f5f5f5"] * len(coef_df),
                        ["#f5f5f5"] * len(coef_df),
                        ["#f5f5f5"] * len(coef_df),
                        ["#f5f5f5"] * len(coef_df),
                        pval_colors,
                        ["#f5f5f5"] * len(coef_df),
                        ["#f5f5f5"] * len(coef_df),
                    ],
                    align="center",
                    font=dict(size=11)
                )
            )])
            fig_coef_table.update_layout(
                title="Regressionskoeffizienten (p-Wert: grün = signifikant | Beta = standardisierter Koeffizient)",
                height=350
            )
            st.plotly_chart(fig_coef_table, use_container_width=True)

            # Koeffizientenplot (unstandardisiert)
            fig_coef = px.bar(
                coef_df.drop("const", errors="ignore").reset_index(),
                x="index", y="Koeffizient",
                error_y="Std.-Fehler",
                title="Regressionskoeffizienten (unstandardisiert)",
                labels={"index": "Prädiktor"},
                color="Koeffizient",
                color_continuous_scale="RdBu"
            )
            fig_coef.add_hline(y=0, line_dash="dash", line_color="black")
            st.plotly_chart(fig_coef, use_container_width=True)

            # Standardisierter Koeffizientenplot (Beta)
            beta_plot_df = coef_df.drop("const", errors="ignore").reset_index()
            fig_beta = px.bar(
                beta_plot_df,
                x="index", y="Beta (std.)",
                title="Standardisierte Regressionskoeffizienten (Beta)",
                labels={"index": "Prädiktor"},
                color="Beta (std.)",
                color_continuous_scale="RdBu"
            )
            fig_beta.add_hline(y=0, line_dash="dash", line_color="black")
            st.plotly_chart(fig_beta, use_container_width=True)

            # Residualplot
            resid_df = pd.DataFrame({
                "Vorhergesagt": model.fittedvalues,
                "Residuen":     model.resid
            })
            fig_resid = px.scatter(
                resid_df, x="Vorhergesagt", y="Residuen",
                title="Residuen vs. Vorhergesagte Werte",
                color_discrete_sequence=["#4393c3"]
            )
            fig_resid.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig_resid, use_container_width=True)

        else:
            st.warning("Nicht genug Beobachtungen für die Regression.")
    else:
        st.info("Bitte mindestens einen Prädiktor auswählen.")

# =========================================================
# TAB 5 — FEHLENDE WERTE
# =========================================================

with tab5:

    st.subheader("Analyse fehlender Werte")

    missing_df = pd.DataFrame({
        "Variable":      alle_variablen,
        "Fehlend (N)":   [df[v].isna().sum() for v in alle_variablen],
        "Fehlend (%)":   [(df[v].isna().mean() * 100).round(1) for v in alle_variablen],
        "Vorhanden (N)": [df[v].notna().sum() for v in alle_variablen]
    }).sort_values("Fehlend (%)", ascending=False)

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Variablen gesamt",       len(alle_variablen))
    col_m2.metric("Beobachtungen gesamt",   len(df))
    col_m3.metric("Ø fehlend pro Variable", f"{missing_df['Fehlend (%)'].mean():.1f}%")

    st.dataframe(missing_df, use_container_width=True)

    fig_miss = px.bar(
        missing_df,
        x="Variable", y="Fehlend (%)",
        title="Fehlende Werte pro Variable (%)",
        color="Fehlend (%)",
        color_continuous_scale="Reds",
        text="Fehlend (%)"
    )
    fig_miss.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_miss.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_miss, use_container_width=True)

    st.markdown("---")
    st.subheader("Fehlende-Werte-Muster (Heatmap)")

    miss_heatmap_vars = st.multiselect(
        "Variablen für Muster-Heatmap",
        alle_variablen,
        default=alle_variablen[:10],
        key="miss_heatmap_vars"
    )

    if miss_heatmap_vars:
        miss_matrix = df[miss_heatmap_vars].isna().astype(int)
        fig_miss_heat = px.imshow(
            miss_matrix.T,
            color_continuous_scale=[[0, "#d4edda"], [1, "#f8d7da"]],
            labels=dict(color="Fehlend"),
            title="Fehlende Werte pro Firma (rot = fehlend, grün = vorhanden)",
            aspect="auto"
        )
        fig_miss_heat.update_layout(height=500)
        st.plotly_chart(fig_miss_heat, use_container_width=True)

# =========================================================
# TAB 6 — DATENTABELLE
# =========================================================

with tab6:

    st.subheader("Datentabelle")

    # Wenn eine Firma auf der Karte angeklickt wurde → Zeile hervorheben
    if "angeklickte_firma_idx" in st.session_state:
        idx_sel = st.session_state["angeklickte_firma_idx"]

        if idx_sel in df.index:
            firma_sel = (
                df.loc[idx_sel, "Zugehörigkeit"]
                if "Zugehörigkeit" in df.columns and pd.notna(df.loc[idx_sel, "Zugehörigkeit"])
                else "k.A."
            )

            st.success(
                f"📌 Hervorgehobene Firma: **{firma_sel}** — Zeile **{idx_sel}** "
                f"(oben in der Tabelle angezeigt)"
            )

            # Ausgewählte Zeile oben, Rest darunter
            zeile_sel  = df.loc[[idx_sel]]
            rest_df    = df.drop(index=idx_sel)
            df_anzeige = pd.concat([zeile_sel, rest_df])

            # Styling: ausgewählte Zeile gelb hinterlegen
            def highlight_first(row):
                if row.name == idx_sel:
                    return ["background-color: #fff9c4; font-weight: bold"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df_anzeige.style.apply(highlight_first, axis=1),
                use_container_width=True,
                height=900
            )

            if st.button("🔄 Markierung zurücksetzen", key="reset_marker"):
                del st.session_state["angeklickte_firma_idx"]
                st.rerun()
        else:
            st.dataframe(df, use_container_width=True, height=900)
    else:
        st.dataframe(df, use_container_width=True, height=900)
