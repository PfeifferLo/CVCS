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
    page_title="CVCS Dashboard",
    layout="wide"
)

st.title("CVCS Dashboard")

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
df["Design_Biologischer_Kreislauf"] = safe_mean(["Q12_9","Q12_10","Q12_11","Q12_12"])

# --- Q13 ---
df["Nutzungsorientierte_PSS"] = safe_mean(["Q13_4","Q13_5","Q13_6","Q13_7"])
df["Integrierte_PSS"]    = safe_mean(["Q13_1","Q13_2","Q13_3"])

# --- Q8 ---
df["Anzahl_Rstrategien"] = df["Q8 Anzahl R-Strategien (Fr. 8)"]
df["Anzahl_Closing_Strategien"] = df["Anzahl_Closing_Strategien"]
df["Anzahl_Slowing_Strategien"] = df["Anzahl_Slowing_Strategien"]

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
    "VI_Mittelwert", "VI_Closing", "VI_Slowing","Strategische_Integration","Legitimität", "Externer_Druck", "Lern_und_Kooperationsorientierung", "Differenzierungs_Wettbewerbsorientierung",
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
    col_info1.metric("Firmen mit Wert (Kleineres n, da die Adresscodierung nicht bei allen Firmen funktionierte)",       len(map_data_colored))
    col_info2.metric("Firmen ohne Wert (NA)", len(map_data_na))

    m = folium.Map(location=[47.6, 14.5], zoom_start=7, tiles="OpenStreetMap")

    # --------------------------------------------------
    # FARBEN + LEGENDE
    # --------------------------------------------------

    if variable in vi_variablen:

        def get_color(v):
            if v <= 1:   return "#b2182b"
            elif v <= 2: return "#d6604d"
            elif v <= 3: return "#f4a582"
            elif v <= 4: return "#fddbc7"
            elif v <= 5: return "#92c5de"
            elif v <= 6: return "#4393c3"
            else:        return "#2166ac"

        legend_html = f"""
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
        </div>
        """

    else:

        def get_color(v):
            if v <= 1:   return "#d73027"
            elif v <= 2: return "#fc8d59"
            elif v <= 3: return "#fee08b"
            elif v <= 4: return "#91cf60"
            else:        return "#1a9850"

        legend_html = f"""
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
        </div>
        """

    # --------------------------------------------------
    # MARKER — farbig (mit Wert)
    # --------------------------------------------------

    for _, row in map_data_colored.iterrows():
        firma = row["Zugehörigkeit"] if "Zugehörigkeit" in row and pd.notna(row["Zugehörigkeit"]) else "k.A."
        popup = f"""
        <b>Firma:</b> {firma}<br>
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> {round(row[variable], 2)}
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color="black", weight=1,
            fill=True,
            fill_color=get_color(row[variable]),
            fill_opacity=0.9,
            popup=folium.Popup(popup, max_width=250)
        ).add_to(m)

    # --------------------------------------------------
    # MARKER — grau (NA)
    # --------------------------------------------------

    for _, row in map_data_na.iterrows():
        firma = row["Zugehörigkeit"] if "Zugehörigkeit" in row and pd.notna(row["Zugehörigkeit"]) else "k.A."
        popup = f"""
        <b>Firma:</b> {firma}<br>
        <b>Variable:</b> {variable}<br>
        <b>Wert:</b> kein Wert (NA)
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color="black", weight=1,
            fill=True,
            fill_color="#aaaaaa",
            fill_opacity=0.7,
            popup=folium.Popup(popup, max_width=250)
        ).add_to(m)

    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=1400, height=850)

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
        desc_df["Schiefe"] = df[desc_vars].skew()
        desc_df["Wölbung"] = df[desc_vars].kurtosis()
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
        m1, m2, m3 = st.columns(3)
        m1.metric("Pearson r", round(corr_val, 3))
        m2.metric("p-Wert",    round(pval, 5))
        m3.metric("N",         len(corr_data))

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

        # Grün = +1, Rot = -1, X-Achse oben
        fig_heat = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdYlGn",
            zmin=-1, zmax=1,
            title="Pearson-Korrelationsmatrix",
            aspect="auto"
        )
        fig_heat.update_layout(
            height=600,
            xaxis=dict(side="top")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # --------------------------------------------------
        # p-Wert Tabelle — via Plotly go.Heatmap
        # (kein matplotlib / background_gradient!)
        # --------------------------------------------------

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

        fig_pval = go.Figure(data=go.Heatmap(
            z=pval_matrix.values.astype(float),
            x=heatmap_vars,
            y=heatmap_vars,
            colorscale=[
                [0.000, "#1a9850"],
                [0.010, "#91cf60"],
                [0.050, "#fee08b"],
                [0.100, "#fc8d59"],
                [1.000, "#d73027"],
            ],
            zmin=0, zmax=1,
            text=pval_matrix.round(4).values,
            texttemplate="%{text}",
            hoverongaps=False
        ))
        fig_pval.update_layout(
            title="p-Werte (grün = signifikant, rot = nicht signifikant)",
            height=500,
            xaxis=dict(side="top")
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

            coef_df = pd.DataFrame({
                "Koeffizient": model.params,
                "Std.-Fehler": model.bse,
                "t-Wert":      model.tvalues,
                "p-Wert":      model.pvalues,
                "CI 2.5%":     model.conf_int()[0],
                "CI 97.5%":    model.conf_int()[1]
            }).round(4)

            # Farbkodierung p-Werte ohne matplotlib
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
                        pval_colors,
                        ["#f5f5f5"] * len(coef_df),
                        ["#f5f5f5"] * len(coef_df),
                    ],
                    align="center",
                    font=dict(size=11)
                )
            )])
            fig_coef_table.update_layout(
                title="Regressionskoeffizienten (p-Wert: grün = signifikant)",
                height=350
            )
            st.plotly_chart(fig_coef_table, use_container_width=True)

            # Koeffizientenplot
            fig_coef = px.bar(
                coef_df.drop("const", errors="ignore").reset_index(),
                x="index", y="Koeffizient",
                error_y="Std.-Fehler",
                title="Regressionskoeffizienten",
                labels={"index": "Prädiktor"},
                color="Koeffizient",
                color_continuous_scale="RdBu"
            )
            fig_coef.add_hline(y=0, line_dash="dash", line_color="black")
            st.plotly_chart(fig_coef, use_container_width=True)

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
    st.dataframe(df, use_container_width=True, height=900)
