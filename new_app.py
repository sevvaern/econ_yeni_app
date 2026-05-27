import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SVIO Platform",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, .stApp { background:#0d1117; color:#c9d1d9; font-family:'Segoe UI',sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background:#161b22;
    border-right:1px solid #21262d;
}
section[data-testid="stSidebar"] * { color:#8b949e !important; }
section[data-testid="stSidebar"] .stRadio label { font-size:0.82rem; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background:#161b22;
    border:1px solid #21262d;
    border-radius:6px;
    padding:16px 20px 14px;
}
[data-testid="metric-container"] label {
    color:#8b949e !important;
    font-size:0.72rem !important;
    text-transform:uppercase;
    letter-spacing:.06em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#e6edf3 !important;
    font-size:1.55rem !important;
    font-weight:600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size:0.75rem !important;
}

/* ── Headings ── */
h1 { color:#e6edf3 !important; font-size:1.3rem !important; font-weight:600 !important; margin-bottom:.2rem !important; }
h2 { color:#c9d1d9 !important; font-size:1.0rem !important; font-weight:600 !important; }
h3 { color:#8b949e !important; font-size:.85rem !important; font-weight:500 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:#161b22;
    border-radius:6px;
    gap:2px;
    padding:3px;
}
.stTabs [data-baseweb="tab"] {
    background:transparent;
    color:#8b949e;
    border-radius:4px;
    font-size:.8rem;
    padding:5px 14px;
}
.stTabs [aria-selected="true"] {
    background:#21262d !important;
    color:#e6edf3 !important;
}

/* ── Dataframe ── */
.stDataFrame { border:1px solid #21262d; border-radius:6px; }

/* ── Divider ── */
hr { border-color:#21262d; margin:14px 0; }

/* ── Info strip ── */
.info-strip {
    background:#0d1f36;
    border-left:3px solid #1f6feb;
    border-radius:4px;
    padding:7px 13px;
    font-size:.75rem;
    color:#6e9fc5;
    margin-bottom:14px;
}

/* ── Section label ── */
.slbl {
    font-size:.68rem;
    text-transform:uppercase;
    letter-spacing:.08em;
    color:#484f58;
    margin-bottom:3px;
}

/* ── Login card ── */
.login-wrap {
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:80vh;
}
.login-card {
    background:#161b22;
    border:1px solid #21262d;
    border-radius:10px;
    padding:42px 48px 38px;
    width:380px;
    box-shadow:0 8px 32px rgba(0,0,0,.45);
}
.login-title {
    color:#e6edf3;
    font-size:1.15rem;
    font-weight:600;
    margin-bottom:4px;
}
.login-sub {
    color:#484f58;
    font-size:.75rem;
    margin-bottom:28px;
}

/* ── Status badge ── */
.badge-green { color:#3fb950; font-weight:600; font-size:.78rem; }
.badge-amber { color:#d29922; font-weight:600; font-size:.78rem; }
.badge-red   { color:#f85149; font-weight:600; font-size:.78rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def info(txt):
    st.markdown(f'<div class="info-strip">&#8505; {txt}</div>', unsafe_allow_html=True)

def slbl(txt):
    st.markdown(f'<div class="slbl">{txt}</div>', unsafe_allow_html=True)

PALETTE = ["#1f6feb","#3fb950","#d29922","#f85149","#8b949e",
           "#58a6ff","#56d364","#e3b341","#ff7b72","#79c0ff"]

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#161b22",
    font=dict(color="#8b949e", size=11),
    margin=dict(l=10, r=10, t=32, b=10),
    xaxis=dict(gridcolor="#21262d", linecolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#21262d", zerolinecolor="#21262d"),
)

def fig_layout(fig, **kw):
    fig.update_layout(**BASE, **kw)
    return fig

MONTH = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
         7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

STAGES = ["Arrival","Queue Entry","Document Check",
          "Lane Assignment","Inspection","Manual Review","Exit"]

# ─────────────────────────────────────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def generate_data():
    rng = np.random.default_rng(2024)

    stations = [
        {"station_id":"IST-01","name":"Kadikoy",       "district":"Asian Side",    "lanes":4,"ev_capable":True},
        {"station_id":"IST-02","name":"Sisli",          "district":"European Side", "lanes":3,"ev_capable":False},
        {"station_id":"IST-03","name":"Pendik",         "district":"Asian Side",    "lanes":6,"ev_capable":True},
        {"station_id":"IST-04","name":"Bagcilar",       "district":"European Side", "lanes":3,"ev_capable":False},
        {"station_id":"IST-05","name":"Umraniye",       "district":"Asian Side",    "lanes":4,"ev_capable":True},
        {"station_id":"IST-06","name":"Maltepe",        "district":"Asian Side",    "lanes":2,"ev_capable":False},
        {"station_id":"IST-07","name":"Gaziosmanpasa",  "district":"European Side", "lanes":3,"ev_capable":False},
        {"station_id":"IST-08","name":"Kartal",         "district":"Asian Side",    "lanes":5,"ev_capable":True},
        {"station_id":"IST-09","name":"Sultangazi",     "district":"European Side", "lanes":2,"ev_capable":False},
    ]
    sdf = pd.DataFrame(stations)

    fuel_types    = ["Petrol","Diesel","Electric","Hybrid","LPG"]
    vehicle_types = ["Sedan","Hatchback","SUV","Light Commercial","Minibus","Truck"]
    outcomes_pool = ["Pass","Pass","Pass","Pass","Advisory","Advisory","Fail"]

    n = 3200
    start = datetime(2024, 1, 1)

    sid = rng.choice(
        [s["station_id"] for s in stations], size=n,
        p=[0.14,0.12,0.16,0.11,0.13,0.08,0.09,0.11,0.06]
    )
    fuel = rng.choice(fuel_types, size=n, p=[0.36,0.30,0.13,0.11,0.10])
    is_ev = (fuel == "Electric") | (fuel == "Hybrid")
    vtype = rng.choice(vehicle_types, size=n, p=[0.30,0.24,0.21,0.12,0.08,0.05])

    offsets   = rng.integers(0, 365*24*60, size=n)
    arrivals  = [start + timedelta(minutes=int(m)) for m in offsets]

    base_dur  = {"Sedan":18,"Hatchback":17,"SUV":22,
                 "Light Commercial":28,"Minibus":35,"Truck":42}
    dur = np.array([base_dur[v] for v in vtype], dtype=float)
    dur += rng.normal(0, 3, n)
    dur += np.where(is_ev, rng.uniform(5,14,n), 0)
    dur  = np.clip(dur, 8, 70)

    lane_map  = {s["station_id"]:s["lanes"] for s in stations}
    lanes_arr = np.array([lane_map[s] for s in sid], dtype=float)
    queue_len = rng.integers(2, 32, size=n).astype(float)
    wait_time = (queue_len / lanes_arr) * rng.uniform(3.8, 8.2, n)
    wait_time = np.clip(wait_time, 2, 80).round(1)

    base_em = {"Petrol":1.8,"Diesel":2.6,"Electric":0.0,"Hybrid":0.6,"LPG":1.5}
    emis = np.array([base_em[f] for f in fuel]) + rng.normal(0, 0.4, n)
    emis = np.clip(emis, 0, None)
    anom_mask = (rng.random(n) < 0.028) & ((fuel=="Diesel")|(fuel=="Petrol"))
    emis[anom_mask] += rng.uniform(2.5, 5.2, int(anom_mask.sum()))

    bat_temp = np.where(is_ev, rng.normal(34,6,n), np.nan)
    bat_temp = np.where(is_ev, np.clip(bat_temp,18,64), np.nan)

    letters = list("ABCDEFGHJKLMNPRSTUVYZ")
    plates = [
        "{:02d} {}{} {:04d}".format(
            rng.integers(1,82),
            rng.choice(letters), rng.choice(letters),
            rng.integers(100,9999)
        ) for _ in range(n)
    ]

    outcomes = rng.choice(outcomes_pool, size=n)
    for i in np.where(anom_mask)[0]:
        if rng.random() < 0.5:
            outcomes[i] = "Fail"

    ids = ["INS-{:06d}".format(i) for i in range(n)]

    # Process stage durations (minutes per stage)
    stage_cols = {}
    stage_means = {"Arrival":1.2,"Queue Entry":0.5,"Document Check":3.8,
                   "Lane Assignment":2.1,"Inspection":dur,
                   "Manual Review":0.0,"Exit":1.5}
    for stg in STAGES:
        if stg == "Inspection":
            stage_cols[stg] = np.clip(dur + rng.normal(0,1.5,n), 5, 75).round(1)
        elif stg == "Manual Review":
            manual_flag = (outcomes == "Advisory") | (outcomes == "Fail")
            stage_cols[stg] = np.where(manual_flag, rng.uniform(5,20,n), 0).round(1)
        else:
            stage_cols[stg] = np.clip(
                rng.normal(stage_means[stg], stage_means[stg]*0.3, n), 0.2, None
            ).round(1)

    df = pd.DataFrame({
        "inspection_id":       ids,
        "plate":               plates,
        "station_id":          sid,
        "vehicle_type":        vtype,
        "fuel_type":           fuel,
        "is_ev":               is_ev,
        "arrival_time":        arrivals,
        "inspection_duration": dur.round(1),
        "queue_length":        queue_len.astype(int),
        "wait_time_min":       wait_time,
        "emissions_score":     emis.round(3),
        "battery_temp_c":      np.round(bat_temp, 1),
        "outcome":             outcomes,
        "anomaly_flag":        anom_mask,
    })
    for stg in STAGES:
        df["dur_"+stg.lower().replace(" ","_")] = stage_cols[stg]

    df = df.merge(sdf, on="station_id")
    df["month"]       = pd.to_datetime(df["arrival_time"]).dt.month
    df["hour"]        = pd.to_datetime(df["arrival_time"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["arrival_time"]).dt.day_name()
    df["utilisation"] = np.clip((df["queue_length"]/(df["lanes"]*8))*100, 4, 99).round(1)
    df["total_time"]  = df[[("dur_"+s.lower().replace(" ","_")) for s in STAGES]].sum(axis=1).round(1)
    return df, sdf

df, sdf = generate_data()

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────────────────────
PASSWORD = "econproject"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def do_logout():
    st.session_state.authenticated = False

# ── Login screen ──────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    col_gap1, col_card, col_gap2 = st.columns([1, 1.1, 1])
    with col_card:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;margin-bottom:6px'>"
            "<span style='font-size:2rem'>🚦</span></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='text-align:center;color:#e6edf3;font-size:1.1rem;"
            "font-weight:600;margin-bottom:4px'>SVIO Platform</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='text-align:center;color:#484f58;font-size:.76rem;"
            "margin-bottom:28px'>Smart Vehicle Inspection Operations<br>"
            "Process Mining &amp; Queue Analytics System</div>",
            unsafe_allow_html=True
        )
        pwd = st.text_input(
            "Access code", type="password",
            placeholder="Enter access code",
            label_visibility="collapsed"
        )
        login_btn = st.button("Sign In", use_container_width=True, type="primary")

        if login_btn:
            if pwd == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.markdown(
                    "<div style='color:#f85149;font-size:.78rem;"
                    "text-align:center;margin-top:8px'>"
                    "Incorrect access code. Please try again.</div>",
                    unsafe_allow_html=True
                )
        st.markdown(
            "<div style='text-align:center;color:#21262d;font-size:.68rem;"
            "margin-top:32px'>Academic Prototype &mdash; "
            "MobilityTech Research Group</div>",
            unsafe_allow_html=True
        )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  (authenticated only)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:4px 0 12px'>"
        "<span style='font-size:1.1rem'>🚦</span> "
        "<span style='color:#e6edf3;font-weight:600;font-size:.95rem'>"
        "SVIO Platform</span></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:.7rem;color:#484f58;margin-bottom:16px'>"
        "Smart Vehicle Inspection Operations</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Process Mining Analytics",
            "Queue Optimisation",
            "EV Inspection Operations",
            "Emission Monitoring",
            "Digital Twin Simulation",
            "Station Network Performance",
            "Vehicle Inspection Search",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.68rem;color:#484f58;line-height:1.8'>"
        "Academic Prototype<br>"
        "MobilityTech Research Group<br><br>"
        "Synthetic data only.<br>"
        "Not real inspection records.</div>",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Sign Out", on_click=do_logout, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Simulation helper (digital twin)
# ─────────────────────────────────────────────────────────────────────────────
def simulate(vol, ev_pct, lanes, stf):
    cap   = lanes * stf * 5.6
    util  = min(98.0, round(vol / max(cap,1)*100, 1))
    qlen  = max(0, round((vol - cap) / max(lanes,1)*0.38 + 3.5))
    wait  = round(min(qlen / max(lanes,1)*4.4 + 5, 92), 1)
    ev_v  = round(vol * ev_pct / 100)
    thru  = round(min(vol, cap))
    risk  = "High" if util > 84 else ("Moderate" if util > 63 else "Low")
    return dict(util=util, qlen=qlen, wait=wait, ev_vol=ev_v, thru=thru, risk=risk)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "Executive Overview":
    st.title("Executive Overview")
    info("Synthetically generated operational data simulating vehicle inspection station records in Istanbul. For academic research purposes only.")

    ev_df   = df[df["is_ev"]]
    pass_r  = (df["outcome"]=="Pass").mean()*100
    anom_r  = df["anomaly_flag"].sum()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Inspections",  f"{len(df):,}")
    c2.metric("Avg Wait Time",      f"{df['wait_time_min'].mean():.1f} min")
    c3.metric("EV / Hybrid Share",  f"{len(ev_df)/len(df)*100:.1f}%")
    c4.metric("Pass Rate",          f"{pass_r:.1f}%")
    c5.metric("Avg Utilisation",    f"{df['utilisation'].mean():.1f}%")
    c6.metric("Emission Flags",     f"{anom_r}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        slbl("MONTHLY INSPECTION VOLUME")
        mdf = df.groupby("month").size().reset_index(name="count")
        mdf["Month"] = mdf["month"].map(MONTH)
        fig = px.bar(mdf, x="Month", y="count",
                     color_discrete_sequence=["#1f6feb"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Inspections per Month", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("OUTCOME DISTRIBUTION")
        oc = df["outcome"].value_counts().reset_index()
        oc.columns = ["outcome","count"]
        cmap = {"Pass":"#3fb950","Advisory":"#d29922","Fail":"#f85149"}
        fig = px.pie(oc, names="outcome", values="count",
                     color="outcome", color_discrete_map=cmap, hole=0.46)
        fig.update_traces(textinfo="percent+label", textfont_size=11)
        fig_layout(fig, title="Inspection Outcomes", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        slbl("AVG WAIT TIME BY HOUR OF DAY")
        hw = df.groupby("hour")["wait_time_min"].mean().reset_index()
        fig = px.line(hw, x="hour", y="wait_time_min", markers=True,
                      color_discrete_sequence=["#58a6ff"])
        fig.update_traces(line_width=2, marker_size=4)
        fig_layout(fig, title="Hourly Wait Pattern",
                   xaxis_title="Hour", yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        slbl("FLEET COMPOSITION")
        fc = df["fuel_type"].value_counts().reset_index()
        fc.columns = ["fuel","count"]
        fig = px.bar(fc, x="fuel", y="count",
                     color="fuel", color_discrete_sequence=PALETTE)
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Fleet by Fuel Type", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    slbl("STATION UTILISATION SNAPSHOT")
    su = df.groupby("name")["utilisation"].mean().reset_index().sort_values("utilisation")
    su.columns = ["Station","Utilisation"]
    fig = px.bar(su, x="Utilisation", y="Station", orientation="h",
                 color="Utilisation",
                 color_continuous_scale=["#238636","#d29922","#f85149"])
    fig.update_traces(marker_line_width=0)
    fig.update_coloraxes(showscale=False)
    fig.add_vline(x=80, line_dash="dash", line_color="#f85149",
                  annotation_text="80% threshold", annotation_font_color="#f85149")
    fig_layout(fig, title="Average Utilisation by Station",
               xaxis_title="Utilisation (%)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PROCESS MINING ANALYTICS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Process Mining Analytics":
    st.title("Process Mining Analytics")
    info("Inspection lifecycle analysis based on simulated event-log data. Stage durations reflect typical operational sequences at vehicle inspection stations.")

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("Filters", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            sel_station = st.multiselect(
                "Station", options=sorted(df["name"].unique()),
                default=list(df["name"].unique()), key="pm_st"
            )
        with fc2:
            sel_fuel = st.multiselect(
                "Fuel Type", options=sorted(df["fuel_type"].unique()),
                default=list(df["fuel_type"].unique()), key="pm_fuel"
            )
        with fc3:
            sel_outcome = st.multiselect(
                "Outcome", options=["Pass","Advisory","Fail"],
                default=["Pass","Advisory","Fail"], key="pm_out"
            )

    fdf = df.copy()
    if sel_station:  fdf = fdf[fdf["name"].isin(sel_station)]
    if sel_fuel:     fdf = fdf[fdf["fuel_type"].isin(sel_fuel)]
    if sel_outcome:  fdf = fdf[fdf["outcome"].isin(sel_outcome)]

    st.markdown(f"**{len(fdf):,}** inspection records in current filter.")
    st.markdown("---")

    # ── Stage duration means ──────────────────────────────────────────────────
    stage_cols = [("dur_"+s.lower().replace(" ","_")) for s in STAGES]
    means      = fdf[stage_cols].mean().values
    stage_df   = pd.DataFrame({"Stage": STAGES, "Avg Duration (min)": means.round(2)})

    col_l, col_r = st.columns(2)
    with col_l:
        slbl("AVERAGE DURATION PER PROCESS STAGE")
        fig = px.bar(stage_df, x="Stage", y="Avg Duration (min)",
                     color="Avg Duration (min)",
                     color_continuous_scale=["#238636","#d29922","#f85149"],
                     text="Avg Duration (min)")
        fig.update_traces(marker_line_width=0,
                          texttemplate="%{text:.1f}", textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig_layout(fig, title="Process Stage Duration Analysis",
                   yaxis_range=[0, means.max()*1.28])
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("TOTAL INSPECTION TIME DISTRIBUTION")
        fig = px.histogram(fdf, x="total_time", nbins=35,
                           color_discrete_sequence=["#1f6feb"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Total Process Time per Vehicle",
                   xaxis_title="Total Time (min)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    # ── Bottleneck detection ──────────────────────────────────────────────────
    st.markdown("---")
    slbl("BOTTLENECK DETECTION — STAGE CONTRIBUTION TO TOTAL TIME")
    contrib = (fdf[stage_cols].mean() / fdf[stage_cols].mean().sum() * 100).round(1)
    contrib_df = pd.DataFrame({"Stage":STAGES, "Share (%)":contrib.values})
    fig = px.bar(contrib_df, x="Share (%)", y="Stage", orientation="h",
                 color="Share (%)",
                 color_continuous_scale=["#238636","#d29922","#f85149"],
                 text="Share (%)")
    fig.update_traces(marker_line_width=0,
                      texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig_layout(fig, title="Stage Share of Total Process Time — Bottleneck View",
               xaxis_title="Share (%)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # ── Process flow by outcome ───────────────────────────────────────────────
    col_l2, col_r2 = st.columns(2)
    with col_l2:
        slbl("INSPECTION DURATION BY OUTCOME")
        fig = px.box(fdf, x="outcome", y="inspection_duration",
                     color="outcome",
                     color_discrete_map={"Pass":"#3fb950","Advisory":"#d29922","Fail":"#f85149"})
        fig_layout(fig, title="Inspection Duration by Outcome",
                   showlegend=False, yaxis_title="Duration (min)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        slbl("MANUAL REVIEW STAGE — TRIGGERED CASES")
        rev_df = fdf[fdf["dur_manual_review"] > 0]
        rev_by = rev_df.groupby("name")["dur_manual_review"].mean().reset_index()
        rev_by.columns = ["Station","Avg Review Duration (min)"]
        fig = px.bar(rev_by.sort_values("Avg Review Duration (min)"),
                     x="Avg Review Duration (min)", y="Station",
                     orientation="h", color_discrete_sequence=["#d29922"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Avg Manual Review Duration by Station")
        st.plotly_chart(fig, use_container_width=True)

    # ── Throughput trend ──────────────────────────────────────────────────────
    slbl("DAILY THROUGHPUT TREND (SAMPLE — FIRST 90 DAYS)")
    fdf2 = fdf.copy()
    fdf2["date"] = pd.to_datetime(fdf2["arrival_time"]).dt.date
    daily = fdf2.groupby("date").size().reset_index(name="count")
    daily = daily.head(90)
    fig = px.area(daily, x="date", y="count",
                  color_discrete_sequence=["#1f6feb"], line_shape="spline")
    fig.update_traces(fill="tozeroy", fillcolor="rgba(31,111,235,0.12)")
    fig_layout(fig, title="Daily Inspection Throughput",
               xaxis_title="Date", yaxis_title="Inspections")
    st.plotly_chart(fig, use_container_width=True)

    # ── Stage table ───────────────────────────────────────────────────────────
    slbl("PROCESS STAGE SUMMARY TABLE")
    summary = pd.DataFrame({
        "Stage": STAGES,
        "Avg (min)": fdf[stage_cols].mean().round(2).values,
        "Median (min)": fdf[stage_cols].median().round(2).values,
        "Std Dev": fdf[stage_cols].std().round(2).values,
        "Max (min)": fdf[stage_cols].max().round(1).values,
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — QUEUE OPTIMISATION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Queue Optimisation":
    st.title("Queue Optimisation")
    info("Queue analysis based on simulated station traffic. All outputs represent scenario-based estimation using synthetic operational data.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Queue Length",  f"{df['queue_length'].mean():.1f} veh.")
    c2.metric("Peak Queue (Sim.)", f"{int(df['queue_length'].max())} veh.")
    c3.metric("Avg Wait Time",     f"{df['wait_time_min'].mean():.1f} min")
    c4.metric("Peak Wait (Sim.)",  f"{df['wait_time_min'].max():.0f} min")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        slbl("QUEUE LENGTH BY HOUR — CONGESTION PROFILE")
        hq = df.groupby("hour")["queue_length"].mean().reset_index()
        fig = px.bar(hq, x="hour", y="queue_length",
                     color="queue_length",
                     color_continuous_scale=["#238636","#d29922","#f85149"])
        fig.update_traces(marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig_layout(fig, title="Avg Queue by Hour",
                   xaxis_title="Hour of Day", yaxis_title="Vehicles in Queue")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("WAIT TIME DISTRIBUTION")
        fig = px.histogram(df, x="wait_time_min", nbins=35,
                           color_discrete_sequence=["#58a6ff"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Wait Time Distribution",
                   xaxis_title="Wait Time (min)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────────────────────────
    slbl("CONGESTION HEATMAP — HOUR vs DAY OF WEEK")
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat = df.groupby(["day_of_week","hour"])["queue_length"].mean().reset_index()
    heat = heat.pivot(index="day_of_week", columns="hour", values="queue_length")
    heat = heat.reindex([d for d in dow_order if d in heat.index])
    fig = go.Figure(go.Heatmap(
        z=heat.values,
        x=list(heat.columns),
        y=list(heat.index),
        colorscale=[[0,"#161b22"],[0.4,"#1f6feb"],[0.7,"#d29922"],[1.0,"#f85149"]],
        colorbar=dict(tickfont=dict(color="#8b949e"), title=dict(text="Queue", font=dict(color="#8b949e"))),
    ))
    fig_layout(fig, title="Queue Intensity Heatmap",
               xaxis_title="Hour of Day", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # ── Per-station wait ──────────────────────────────────────────────────────
    col_l2, col_r2 = st.columns(2)
    with col_l2:
        slbl("WAIT TIME BY STATION")
        sw = df.groupby("name")["wait_time_min"].mean().reset_index().sort_values("wait_time_min")
        fig = px.bar(sw, x="wait_time_min", y="name", orientation="h",
                     color="wait_time_min",
                     color_continuous_scale=["#238636","#d29922","#f85149"])
        fig.update_traces(marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig_layout(fig, title="Avg Wait Time per Station",
                   xaxis_title="Minutes", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        slbl("QUEUE LENGTH BY VEHICLE TYPE")
        qv = df.groupby("vehicle_type")["queue_length"].mean().reset_index().sort_values("queue_length")
        fig = px.bar(qv, x="queue_length", y="vehicle_type", orientation="h",
                     color_discrete_sequence=["#1f6feb"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Avg Queue by Vehicle Type",
                   xaxis_title="Queue Length", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # ── Scenario sliders ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Operational Scenario Estimation")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sc_vol   = st.slider("Daily volume (vehicles)", 100, 700, 320, 10)
    with sc2:
        sc_lanes = st.slider("Active lanes", 1, 12, 4, 1)
    with sc3:
        sc_staff = st.slider("Staff on duty", 2, 20, 6, 1)

    base_r = simulate(320, 12, 4, 6)
    curr_r = simulate(sc_vol, 12, sc_lanes, sc_staff)

    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("Est. Avg Wait", f"{curr_r['wait']} min",
               f"{curr_r['wait']-base_r['wait']:+.1f} vs baseline", delta_color="inverse")
    mc2.metric("Utilisation", f"{curr_r['util']}%",
               f"{curr_r['util']-base_r['util']:+.1f}%", delta_color="inverse")
    mc3.metric("Est. Queue", f"{curr_r['qlen']} veh.",
               f"{curr_r['qlen']-base_r['qlen']:+d}", delta_color="inverse")
    mc4.metric("Bottleneck Risk", curr_r["risk"])

    slbl("SCENARIO COMPARISON — ESTIMATED WAIT TIME")
    scenarios = [
        {"label":"Baseline",          "v":320,"e":12,"l":4,"s":6},
        {"label":"+2 Lanes",          "v":320,"e":12,"l":6,"s":6},
        {"label":"EV Surge +30%",     "v":320,"e":42,"l":4,"s":6},
        {"label":"Peak Volume +50%",  "v":480,"e":12,"l":4,"s":6},
        {"label":"Peak + Opt. Lanes", "v":480,"e":12,"l":7,"s":8},
        {"label":"Current Settings",  "v":sc_vol,"e":12,"l":sc_lanes,"s":sc_staff},
    ]
    sc_rows = []
    for s in scenarios:
        r = simulate(s["v"],s["e"],s["l"],s["s"])
        sc_rows.append({"Scenario":s["label"],"Wait (min)":r["wait"],"Util (%)":r["util"]})
    sc_df = pd.DataFrame(sc_rows)
    colors_sc = ["#8b949e"]*5 + ["#1f6feb"]
    fig = go.Figure()
    for i, row in sc_df.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Scenario"]], y=[row["Wait (min)"]],
            marker_color=colors_sc[i],
            text=[f"{row['Wait (min)']} min"], textposition="outside",
            showlegend=False,
        ))
    fig_layout(fig, title="Estimated Avg Wait Time by Scenario",
               yaxis_title="Minutes",
               yaxis_range=[0, sc_df["Wait (min)"].max()*1.3])
    st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — EV INSPECTION OPERATIONS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "EV Inspection Operations":
    st.title("EV Inspection Operations")
    info("Electric and hybrid vehicle inspection data is simulated. Battery temperature thresholds are illustrative, based on general academic mobility research parameters.")

    ev_df = df[df["is_ev"]].copy()
    cv_df = df[~df["is_ev"]].copy()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("EV / Hybrid Inspections", f"{len(ev_df):,}")
    c2.metric("Share of Total Fleet",    f"{len(ev_df)/len(df)*100:.1f}%")
    c3.metric("Avg EV Wait Time",        f"{ev_df['wait_time_min'].mean():.1f} min")
    c4.metric("Avg Battery Temp",        f"{ev_df['battery_temp_c'].mean():.1f} C")
    c5.metric("Temp Alerts (>50 C)",     f"{int((ev_df['battery_temp_c']>50).sum())}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        slbl("EV vs CONVENTIONAL — WAIT TIME")
        comp = pd.DataFrame({
            "Group":["EV / Hybrid","Conventional"],
            "Avg Wait (min)":[ev_df["wait_time_min"].mean(), cv_df["wait_time_min"].mean()]
        })
        fig = px.bar(comp, x="Group", y="Avg Wait (min)",
                     color="Group",
                     color_discrete_map={"EV / Hybrid":"#3fb950","Conventional":"#484f58"})
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Average Wait Time Comparison", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("BATTERY TEMPERATURE DISTRIBUTION")
        fig = px.histogram(ev_df, x="battery_temp_c", nbins=30,
                           color_discrete_sequence=["#3fb950"])
        fig.add_vline(x=50, line_dash="dash", line_color="#f85149",
                      annotation_text="Alert (50 C)", annotation_font_color="#f85149")
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Battery Temperature — EV / Hybrid Fleet",
                   xaxis_title="Temperature (C)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        slbl("EV INSPECTIONS BY STATION")
        ev_st = ev_df.groupby("name").size().reset_index(name="EV Inspections")
        ev_st = ev_st.sort_values("EV Inspections", ascending=True)
        fig = px.bar(ev_st, x="EV Inspections", y="name", orientation="h",
                     color_discrete_sequence=["#3fb950"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="EV Inspections per Station", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        slbl("EV INSPECTION OUTCOMES")
        eo = ev_df["outcome"].value_counts().reset_index()
        eo.columns = ["outcome","count"]
        cmap = {"Pass":"#3fb950","Advisory":"#d29922","Fail":"#f85149"}
        fig = px.bar(eo, x="outcome", y="count",
                     color="outcome", color_discrete_map=cmap)
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="EV Inspection Outcomes", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    slbl("EV INSPECTION DURATION vs CONVENTIONAL")
    dur_comp = pd.DataFrame({
        "Type": ["EV/Hybrid"]*len(ev_df) + ["Conventional"]*len(cv_df),
        "Duration (min)": list(ev_df["inspection_duration"]) + list(cv_df["inspection_duration"])
    })
    fig = px.box(dur_comp, x="Type", y="Duration (min)",
                 color="Type",
                 color_discrete_map={"EV/Hybrid":"#3fb950","Conventional":"#484f58"})
    fig_layout(fig, title="Inspection Duration Comparison", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    slbl("EV-CAPABLE STATION OVERVIEW")
    ev_cap = sdf[["name","ev_capable","lanes","district"]].copy()
    ev_cap["EV Capable"] = ev_cap["ev_capable"].map({True:"Yes",False:"No"})
    ev_cap = ev_cap.rename(columns={"name":"Station","lanes":"Lanes","district":"District"})
    st.dataframe(ev_cap[["Station","District","Lanes","EV Capable"]],
                 use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — EMISSION MONITORING
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Emission Monitoring":
    st.title("Emission Monitoring")
    info("Conceptual anomaly-based monitoring using simulated operational data. "
         "Flags are generated statistically (z-score > 2 SD from fuel-class mean). "
         "This is not a certified emissions detection system.")

    pd_df = df[df["fuel_type"].isin(["Petrol","Diesel"])].copy()
    an_df = df[df["anomaly_flag"]].copy()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Records Monitored",   f"{len(pd_df):,}")
    c2.metric("Anomaly Flags",       f"{len(an_df)}")
    c3.metric("Flag Rate",           f"{len(an_df)/len(pd_df)*100:.1f}%")
    c4.metric("Avg Emissions Score", f"{df['emissions_score'].mean():.2f}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        slbl("EMISSIONS SCORE BY FUEL TYPE")
        ne = df[df["fuel_type"].isin(["Petrol","Diesel","LPG","Hybrid"])].copy()
        fig = px.box(ne, x="fuel_type", y="emissions_score",
                     color="fuel_type", color_discrete_sequence=PALETTE)
        fig_layout(fig, title="Emissions Distribution by Fuel Type",
                   showlegend=False, yaxis_title="Emissions Score (simulated)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("NORMAL vs FLAGGED")
        df2 = df[df["fuel_type"].isin(["Petrol","Diesel"])].copy()
        df2["Status"] = df2["anomaly_flag"].map({True:"Flagged",False:"Normal"})
        fig = px.histogram(df2, x="emissions_score", color="Status",
                           nbins=40, barmode="overlay", opacity=0.75,
                           color_discrete_map={"Normal":"#1f6feb","Flagged":"#f85149"})
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Emissions Distribution — Status View",
                   xaxis_title="Emissions Score", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        slbl("FLAGS BY STATION")
        fg = an_df.groupby("name").size().reset_index(name="flags").sort_values("flags",ascending=True)
        fig = px.bar(fg, x="flags", y="name", orientation="h",
                     color_discrete_sequence=["#d29922"])
        fig.update_traces(marker_line_width=0)
        fig_layout(fig, title="Anomaly Flags by Station",
                   xaxis_title="Flags", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_r2:
        slbl("MONTHLY FLAG TREND")
        mf = an_df.groupby("month").size().reset_index(name="flags")
        mf["Month"] = mf["month"].map(MONTH)
        fig = px.line(mf, x="Month", y="flags", markers=True,
                      color_discrete_sequence=["#f85149"])
        fig.update_traces(line_width=2, marker_size=5)
        fig_layout(fig, title="Anomaly Flags per Month",
                   yaxis_title="Flag Count")
        st.plotly_chart(fig, use_container_width=True)

    slbl("FLAGGED RECORDS — SAMPLE (SYNTHETIC)")
    ft = an_df[["plate","vehicle_type","fuel_type","emissions_score","outcome","name"]].copy()
    ft.columns = ["Plate","Vehicle Type","Fuel","Emissions Score","Outcome","Station"]
    st.dataframe(ft.head(30), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(
        "**Detection Methodology (Conceptual):** Each vehicle's emissions score is compared "
        "against the mean and standard deviation of its fuel-class group. Vehicles scoring more "
        "than **2 standard deviations above** their class mean are flagged for inspector review. "
        "No automated enforcement is modelled — all flagged cases require human confirmation."
    )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 6 — DIGITAL TWIN SIMULATION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Digital Twin Simulation":
    st.title("Digital Twin Simulation")
    info("Parameterised operational simulation — not a trained predictive model. "
         "Outputs are scenario-based estimations intended for planning discussion only.")

    st.markdown("#### Scenario Configuration")
    c1,c2,c3,c4 = st.columns(4)
    with c1: vol   = st.slider("Daily volume",         100,700,320,10)
    with c2: ev_s  = st.slider("EV / Hybrid share (%)",0,60,12,1)
    with c3: lanes = st.slider("Active lanes",         1,12,4,1)
    with c4: stf   = st.slider("Staff per station",    2,20,6,1)

    BASE = simulate(320,12,4,6)
    CURR = simulate(vol,ev_s,lanes,stf)

    st.markdown("---")
    st.markdown("#### Simulation Output")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Est. Avg Wait",  f"{CURR['wait']} min",
              f"{CURR['wait']-BASE['wait']:+.1f} vs baseline", delta_color="inverse")
    c2.metric("Utilisation",    f"{CURR['util']}%",
              f"{CURR['util']-BASE['util']:+.1f}%",         delta_color="inverse")
    c3.metric("Queue Length",   f"{CURR['qlen']} veh.",
              f"{CURR['qlen']-BASE['qlen']:+d}",             delta_color="inverse")
    c4.metric("Daily EV Volume",f"{CURR['ev_vol']} veh.")
    c5.metric("Bottleneck Risk",CURR["risk"])

    st.markdown("---")
    scenarios = [
        {"label":"Baseline",          "v":320,"e":12,"l":4,"s":6},
        {"label":"+2 Lanes",          "v":320,"e":12,"l":6,"s":6},
        {"label":"EV Surge +30%",     "v":320,"e":42,"l":4,"s":6},
        {"label":"Peak +50%",         "v":480,"e":12,"l":4,"s":6},
        {"label":"Combined Opt.",     "v":480,"e":12,"l":7,"s":8},
        {"label":"Current Settings",  "v":vol,"e":ev_s,"l":lanes,"s":stf},
    ]
    rows = []
    for s in scenarios:
        r = simulate(s["v"],s["e"],s["l"],s["s"])
        rows.append({"Scenario":s["label"],"Wait (min)":r["wait"],"Util (%)":r["util"],"Queue":r["qlen"]})
    scen_df = pd.DataFrame(rows)
    clrs = ["#484f58"]*5 + ["#1f6feb"]

    col_l, col_r = st.columns(2)
    with col_l:
        slbl("ESTIMATED WAIT TIME BY SCENARIO")
        fig = go.Figure()
        for i, row in scen_df.iterrows():
            fig.add_trace(go.Bar(x=[row["Scenario"]], y=[row["Wait (min)"]],
                                 marker_color=clrs[i],
                                 text=[f"{row['Wait (min)']} min"],
                                 textposition="outside", showlegend=False))
        fig_layout(fig, title="Avg Wait by Scenario",
                   yaxis_title="Minutes",
                   yaxis_range=[0, 10 if scen_df.empty or str(scen_df["Wait (min)"].max()) == "nan" else float(scen_df["Wait (min)"].max()) * 1.3])
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("UTILISATION BY SCENARIO")
        fig2 = go.Figure()
        for i, row in scen_df.iterrows():
            fig2.add_trace(go.Bar(x=[row["Scenario"]], y=[row["Util (%)"]],
                                  marker_color=clrs[i],
                                  text=[f"{row['Util (%)']}%"],
                                  textposition="outside", showlegend=False))
        fig2.add_hline(y=85, line_dash="dash", line_color="#f85149",
                       annotation_text="High load", annotation_font_color="#f85149")
        fig_layout(fig2, title="Utilisation by Scenario",
                   yaxis_title="Utilisation (%)", yaxis_range=[0,115])
        st.plotly_chart(fig2, use_container_width=True)

    slbl("SENSITIVITY ANALYSIS — LANE COUNT vs WAIT TIME")
    lr  = list(range(1,13))
    lw  = [simulate(vol,ev_s,ln,stf)["wait"] for ln in lr]
    sdf2 = pd.DataFrame({"Lanes":lr,"Wait (min)":lw})
    fig3 = px.line(sdf2, x="Lanes", y="Wait (min)", markers=True,
                   color_discrete_sequence=["#58a6ff"])
    fig3.add_vline(x=lanes, line_dash="dot", line_color="#3fb950",
                   annotation_text="Current", annotation_font_color="#3fb950")
    fig3.update_traces(line_width=2, marker_size=5)
    fig_layout(fig3, title="Effect of Lane Count on Estimated Wait Time")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown(
        "**Simulation assumptions:** Capacity approximated as `lanes x staff x 5.6` vehicles/day. "
        "Wait derived from a simplified queuing estimate. Results are indicative only and "
        "should not be used for real infrastructure decisions without validated input data."
    )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 7 — STATION NETWORK PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Station Network Performance":
    st.title("Station Network Performance")
    info("Station-level performance metrics aggregated from simulated inspection records.")

    sagg = (
        df.groupby(["station_id","name","district","lanes","ev_capable"])
        .agg(
            inspections=("inspection_id","count"),
            avg_wait=("wait_time_min","mean"),
            avg_queue=("queue_length","mean"),
            avg_util=("utilisation","mean"),
            pass_rate=("outcome", lambda x: (x=="Pass").mean()*100),
            ev_count=("is_ev","sum"),
            flags=("anomaly_flag","sum"),
            avg_total_time=("total_time","mean"),
        )
        .reset_index()
        .round(1)
    )

    slbl("STATION SUMMARY")
    tbl = sagg[["name","district","lanes","ev_capable","inspections",
                "avg_wait","avg_queue","avg_util","pass_rate","flags"]].copy()
    tbl.columns = ["Station","District","Lanes","EV Capable","Inspections",
                   "Avg Wait (min)","Avg Queue","Utilisation (%)","Pass Rate (%)","Flags"]
    tbl["EV Capable"] = tbl["EV Capable"].map({True:"Yes",False:"No"})
    st.dataframe(tbl, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        slbl("AVG WAIT TIME BY STATION")
        s1 = sagg.sort_values("avg_wait",ascending=True)
        fig = px.bar(s1, x="avg_wait", y="name", orientation="h",
                     color="avg_wait",
                     color_continuous_scale=["#238636","#d29922","#f85149"])
        fig.update_traces(marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig_layout(fig, title="Avg Wait Time per Station",
                   xaxis_title="Minutes", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        slbl("UTILISATION BY STATION")
        s2 = sagg.sort_values("avg_util",ascending=True)
        fig2 = px.bar(s2, x="avg_util", y="name", orientation="h",
                      color="avg_util",
                      color_continuous_scale=["#238636","#d29922","#f85149"])
        fig2.update_traces(marker_line_width=0)
        fig2.update_coloraxes(showscale=False)
        fig2.add_vline(x=80, line_dash="dash", line_color="#f85149")
        fig_layout(fig2, title="Avg Utilisation per Station",
                   xaxis_title="Utilisation (%)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        slbl("PASS RATE BY STATION")
        s3 = sagg.sort_values("pass_rate",ascending=True)
        fig3 = px.bar(s3, x="pass_rate", y="name", orientation="h",
                      color_discrete_sequence=["#3fb950"])
        fig3.update_traces(marker_line_width=0)
        fig_layout(fig3, title="Pass Rate per Station (%)",
                   xaxis_title="Pass Rate (%)", yaxis_title="",
                   xaxis_range=[0,100])
        st.plotly_chart(fig3, use_container_width=True)

    with col_r2:
        slbl("VOLUME BY DISTRICT")
        dd = df.groupby("district").size().reset_index(name="count")
        fig4 = px.pie(dd, names="district", values="count",
                      color_discrete_sequence=["#1f6feb","#3fb950"], hole=0.42)
        fig4.update_traces(textinfo="percent+label")
        fig_layout(fig4, title="Inspections by District", showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    slbl("HOURLY QUEUE PROFILE BY STATION")
    hst = df.groupby(["name","hour"])["queue_length"].mean().reset_index()
    fig5 = px.line(hst, x="hour", y="queue_length", color="name",
                   color_discrete_sequence=PALETTE)
    fig5.update_traces(line_width=1.5)
    fig_layout(fig5, title="Avg Queue Length by Hour — All Stations",
               xaxis_title="Hour of Day", yaxis_title="Queue Length")
    st.plotly_chart(fig5, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 8 — VEHICLE INSPECTION SEARCH
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Vehicle Inspection Search":
    st.title("Vehicle Inspection Search")
    info("All plate numbers and vehicle records are synthetically generated. No real vehicle data is used or stored.")

    with st.expander("Search & Filter", expanded=True):
        fc1,fc2,fc3,fc4 = st.columns([2,2,2,2])
        with fc1:
            plate_q = st.text_input("Plate (partial match)", placeholder="e.g. 34 AB")
        with fc2:
            out_f   = st.multiselect("Outcome", ["Pass","Advisory","Fail"],
                                     default=["Pass","Advisory","Fail"])
        with fc3:
            fuel_f  = st.multiselect("Fuel Type", sorted(df["fuel_type"].unique()),
                                     default=list(df["fuel_type"].unique()))
        with fc4:
            st_f    = st.multiselect("Station", sorted(df["name"].unique()),
                                     default=list(df["name"].unique()))

    filt = df.copy()
    if plate_q.strip():
        filt = filt[filt["plate"].str.contains(plate_q.strip(), case=False, na=False)]
    if out_f:   filt = filt[filt["outcome"].isin(out_f)]
    if fuel_f:  filt = filt[filt["fuel_type"].isin(fuel_f)]
    if st_f:    filt = filt[filt["name"].isin(st_f)]

    st.markdown(f"**{len(filt):,}** records match current filter.")

    c1,c2,c3,c4 = st.columns(4)
    if len(filt):
        c1.metric("Records",       f"{len(filt):,}")
        c2.metric("Avg Wait",      f"{filt['wait_time_min'].mean():.1f} min")
        c3.metric("Pass Rate",     f"{(filt['outcome']=='Pass').mean()*100:.1f}%")
        c4.metric("Anomaly Flags", f"{int(filt['anomaly_flag'].sum())}")
    else:
        c1.metric("Records","0")
        c2.metric("Avg Wait","—")
        c3.metric("Pass Rate","—")
        c4.metric("Anomaly Flags","—")

    st.markdown("---")
    slbl("INSPECTION RECORDS")
    cols = ["plate","vehicle_type","fuel_type","name",
            "wait_time_min","inspection_duration","queue_length",
            "emissions_score","outcome","anomaly_flag"]
    disp = filt[cols].copy()
    disp.columns = ["Plate","Vehicle Type","Fuel","Station",
                    "Wait (min)","Duration (min)","Queue",
                    "Emissions Score","Outcome","Anomaly Flag"]
    disp["Anomaly Flag"] = disp["Anomaly Flag"].map({True:"Yes",False:"No"})

    st.dataframe(
        disp.head(200), use_container_width=True, hide_index=True,
        column_config={
            "Wait (min)":      st.column_config.NumberColumn(format="%.1f"),
            "Duration (min)":  st.column_config.NumberColumn(format="%.1f"),
            "Emissions Score": st.column_config.NumberColumn(format="%.3f"),
        }
    )
    if len(filt)>200:
        st.caption(f"Showing first 200 of {len(filt):,} records.")

    if len(filt)>0:
        st.markdown("---")
        col_l,col_r = st.columns(2)
        with col_l:
            slbl("OUTCOME BREAKDOWN")
            oc = filt["outcome"].value_counts().reset_index()
            oc.columns = ["outcome","count"]
            cmap = {"Pass":"#3fb950","Advisory":"#d29922","Fail":"#f85149"}
            fig = px.pie(oc, names="outcome", values="count",
                         color="outcome", color_discrete_map=cmap, hole=0.42)
            fig.update_traces(textinfo="percent+label")
            fig_layout(fig, title="Outcome Distribution", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            slbl("WAIT TIME DISTRIBUTION")
            fig2 = px.histogram(filt, x="wait_time_min", nbins=25,
                                color_discrete_sequence=["#1f6feb"])
            fig2.update_traces(marker_line_width=0)
            fig_layout(fig2, title="Wait Time Distribution",
                       xaxis_title="Wait Time (min)", yaxis_title="Count")
            st.plotly_chart(fig2, use_container_width=True)