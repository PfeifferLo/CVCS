import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px

from streamlit_folium import st_folium
from scipy.stats import pearsonr
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Unternehmensanalyse Oesterreich", layout="wide")
st.title("Unternehmensanalyse Oesterreich")

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

sheet = client.open_by_key("1Z8tsOECgROa69aUUbST0Z5tE0Eh-lZoBv-e0os0DZvY").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)
df = df.replace("", np.nan)

def fix_coordinates(x):
    if pd.isna(x):
        return np.nan
    x = str(x).replace(",", ".")
    try:
        x = float(x)
    except Exception:
        return np.nan
    if 40 <= x <= 50:
        return x
    if x > 1000000:
        return x / 10000000
    return x

df["latitude"]  = df["latitude"].apply(fix_coordinates)
df["longitude"] = df["longitude"].apply(fix_coordinates)

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
    "Q41","Q42"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

def safe_mean(columns):
    cols = [c for c in columns if c in df.columns]
    return df[cols].mean(axis=1, skipna=True)

def safe_sum(columns):
    cols = [c for c in columns if c in df.columns]
    return df[cols].sum(axis=1, skipna=True)

df["VI_Mittelwert"] = safe_mean([
    "Q9 NEU_1","Q9 NEU_2","Q9 NEU_3","Q9 NEU_4",
    "Q9 NEU_5","Q9 NEU_6","Q9 NEU_7","Q9 NEU_8",
    "Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"
])
df["VI_Closing"] = safe_mean(["Q9 NEU_9","Q9 NEU_10","Q9 NEU_11","Q9 NEU_12"])
df["VI_Slowing"] = safe_mean(["Q9 NEU_3","Q9 NEU_4","Q9 NEU_5","Q9 NEU_6","Q9 NEU_7"])

df["Ökonomische_Performance"] = safe_mean(["Q161_1","Q161_2","Q161_3","Q161_4","Q161_5","Q161_6"])
df["Ökologische_Performance"] = safe_mean([
    "Q16_1","Q16_2","Q16_3","Q16_4","Q16_5","Q16_6","Q16_7",
    "Q16_8","Q16_9","Q16_10","Q16_11","Q16_12","Q16_13"
])
df["Produktlebensdauer"]                       = safe_mean(["Q16_3","Q16_4"])
df["Toxische_Freisetzung"]                     = safe_mean(["Q16_6","Q16_7"])
df["Loop_Closure"]                             = safe_mean(["Q14_1","Q14_2"])
df["Open_Loops"]                               = safe_mean(["Q14_3","Q14_4","Q14_5"])
df["Austausch"]                                = safe_mean(["Q15_1","Q15_2"])
df["Erkenntnisse"]                             = safe_mean(["Q15_3","Q15_4","Q15_5","Q15_6","Q15_7"])
df["Legitimität"]                             = safe_mean(["Q5_3","Q5_16","Q5_18","Q5_19","Q5_20"])
df["Externer_Druck"]                           = safe_mean(["Q5_5","Q5_6","Q5_7"])
df["Lern_und_Kooperationsorientierung"]        = safe_mean(["Q5_12","Q5_13","Q5_14","Q5_15","Q5_17"])
df["Differenzierungs_Wettbewerbsorientierung"] = safe_mean(["Q5_4","Q5_8","Q5_9","Q5_10"])
df["Strategische_Integration"]                 = safe_mean(["Q6_1","Q6_2","Q6_3","Q6_4","Q6_5","Q6_6","Q6_7","Q6_8"])

df["Anzahl_Rstrategien"]        = df["Q8_Anzahl_Rstrategien"]
df["Anzahl_Closing_Strategien"] = safe_sum(["Q8_NEU_9","Q8_NEU_10","Q8_NEU_11","Q8_NEU_12"])
df["Anzahl_Slowing_Strategien"] = safe_sum(["Q8_NEU_3","Q8_NEU_4","Q8_NEU_5","Q8_NEU_6","Q8_NEU_7","Q8_NEU_8"])

df["Firmengröße"] = df["Q41"]
df["Firmenalter"]   = df["Q42"]

alle_variablen = [
    "VI Mittelwert", "VI_Closing", "VI_Slowing",
    "Ökonomische_Performance", "Ökologische_Performance",
    "Produktlebensdauer", "Toxische_Freisetzung",
    "Loop_Closure", "Open_Loops", "Austausch", "Erkenntnisse",
    "Legitimität", "Externer_Druck",
    "Lern_und_Kooperationsorientierung",
    "Differenzierungs_Wettbewerbsorientierung",
    "Strategische_Integration",
    "Anzahl_Rstrategien", "Anzahl_Closing_Strategien", "Anzahl_Slowing_Strategien",
    "Firmengröße", "Firmenalter"
]

vi_variablen = ["VI_Mittelwert", "VI_Closing", "VI_Slowing"]

st.sidebar.header("Einstellungen")

variable = st.sidebar.selectbox(
    "Variable auswaehlen",
    alle_variablen,
    key="variable_select"
)

radius = st.sidebar.slider(
    "Punktgroesse", min_value=3, max_value=20, value=8, key="radius_slider"
)

tab1, tab2 = st.tabs(["Karte", "Korrelationen"])

with tab1:

    st.subheader("Unternehmenskarte Österreich")

    map_data = df.dropna(subset=["latitude", "longitude"]).copy()

    map_data = map_data[
        (map_data["latitude"]  > 46)   &
        (map_data["latitude"]  < 49.5) &
        (map_data["longitude"] > 9)    &
        (map_data["longitude"] < 18.5)
    ]

    st.write("Anzahl Firmen auf Karte:", len(map_data))

    m = folium.Map(location=[47.6, 14.5], zoom_start=7, tiles="OpenStreetMap")

    if variable in vi_variablen:

        def get_color(v):
            if pd.isna(v):  return "#aaaaaa"
            if v <= 1:      return "#b2182b"
            elif v <= 2:    return "#d6604d"
            elif v <= 3:    return "#f4a582"
            elif v <= 4:    return "#fddbc7"
            elif v <= 5:    return "#92c5de"
            elif v <= 6:    return "#4393c3"
            else:           return "#2166ac"

        legend_items = (
            "<div style='background:#b2182b;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>1<br>"
            "<div style='background:#d6604d;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>2<br>"
            "<div style='background:#f4a582;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>3<br>"
            "<div style='background:#fddbc7;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>4<br>"
            "<div style='background:#92c5de;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>5<br>"
            "<div style='background:#4393c3;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>6<br>"
            "<div style='background:#2166ac;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>7<br>"
            "<div style='background:#aaaaaa;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>k.A."
        )

    else:

        def get_color(v):
            if pd.isna(v):  return "#aaaaaa"
            if v <= 1:      return "#d73027"
            elif v <= 2:    return "#fc8d59"
            elif v <= 3:    return "#fee08b"
            elif v <= 4:    return "#91cf60"
            else:           return "#1a9850"

        legend_items = (
            "<div style='background:#d73027;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>1<br>"
            "<div style='background:#fc8d59;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>2<br>"
            "<div style='background:#fee08b;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>3<br>"
            "<div style='background:#91cf60;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>4<br>"
            "<div style='background:#1a9850;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>5<br>"
            "<div style='background:#aaaaaa;width:20px;height:20px;display:inline-block;margin-right:6px;'></div>k.A."
        )

    legend_html = (
        "<div style='position:fixed;bottom:40px;right:40px;z-index:9999;"
        "background-color:white;padding:15px;border:2px solid grey;"
        "border-radius:10px;font-size:14px;line-height:1.8;'>"
        "<b>" + str(variable) + "</b><br><br>"
        + legend_items
        + "</div>"
    )

    # Passe diesen Namen auf deinen exakten Spaltennamen an
    firmen_spalte = "Zugehörigkeit"

    for _, row in map_data.iterrows():

        # Firmenname — immer anzeigen, auch bei NA
        if firmen_spalte in df.columns and pd.notna(row.get(firmen_spalte)):
            firma = str(row[firmen_spalte])
        else:
            firma = "k.A."

        # Variablenwert
        if pd.notna(row[variable]):
            wert = str(round(float(row[variable]), 2))
        else:
            wert = "kein Wert"

        popup_html = (
            "<b>Firma:</b> " + firma + "<br>"
            + "<b>Variable:</b> " + str(variable) + "<br>"
            + "<b>Wert:</b> " + wert
        )

        # Tooltip zeigt Firmenname beim Hovern — auch bei grauen NA-Punkten
        tooltip_html = firma

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color="black",
            weight=1,
            fill=True,
            fill_color=get_color(row[variable]),
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=folium.Tooltip(tooltip_html)
        ).add_to(m)

    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=1400, height=850)

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

    corr_data = df[[corr_x, corr_y]].dropna()

    if len(corr_data) > 2:

        corr_val, pval = pearsonr(corr_data[corr_x], corr_data[corr_y])

        st.metric("Pearson r", round(corr_val, 3))
        st.metric("p-Wert",    round(pval, 5))

        fig = px.scatter(corr_data, x=corr_x, y=corr_y, trendline="ols")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nicht genug Daten fuer diese Kombination.")
