import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="AstroGuard IQ | Quantum-Optimized Space Traffic Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "alert_triggered" not in st.session_state:
    st.session_state.alert_triggered = False
if "copilot_messages" not in st.session_state:
    st.session_state.copilot_messages = []

COPILOT_ALERT_REPLY = (
    "Scanning orbital coordinates... Collision vector detected between "
    "Cartosat-2E and Debris-X9. Awaiting deployment commands for the "
    "Qiskit QAOA Optimization engine on IBM Quantum hardware."
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Source+Sans+3:wght@400;600;700&display=swap');

        .stApp {
            background: radial-gradient(ellipse at top, #141b33 0%, #07090f 55%, #05060a 100%);
            color: #e8edf7;
            font-family: "Source Sans 3", sans-serif;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0c1224 0%, #080a12 100%);
            border-right: 1px solid #1e2a4a;
        }

        [data-testid="stSidebar"] * {
            color: #d7def0 !important;
        }

        h1, h2, h3 {
            font-family: "Orbitron", sans-serif !important;
            letter-spacing: 0.04em;
        }

        .hero-kicker {
            color: #7ee0ff;
            font-size: 0.78rem;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .hero-title {
            font-family: "Orbitron", sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
            color: #f4f7ff;
            margin-bottom: 0.35rem;
        }

        .hero-sub {
            color: #9aa8c7;
            margin-bottom: 1.4rem;
        }

        .panel {
            background: rgba(16, 24, 48, 0.72);
            border: 1px solid #243056;
            border-radius: 14px;
            padding: 1rem 1.15rem;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28);
        }

        div.stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #ff2d4a 0%, #c1121f 100%);
            color: #ffffff;
            border: 1px solid #ff6b81;
            border-radius: 10px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 0.85rem 1.2rem;
            box-shadow: 0 0 22px rgba(255, 45, 74, 0.35);
        }

        div.stButton > button:hover {
            background: linear-gradient(90deg, #ff4d67 0%, #e11d2e 100%);
            border-color: #ff8a9b;
            color: #ffffff;
        }

        [data-testid="stMetric"] {
            background: rgba(12, 18, 36, 0.85);
            border: 1px solid #2a3a66;
            border-radius: 12px;
            padding: 0.85rem 1rem;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #243056;
            border-radius: 10px;
        }

        [data-testid="stSidebar"] [data-testid="stChatMessage"] {
            background: rgba(12, 18, 36, 0.9);
            border: 1px solid #243056;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

EARTH_RADIUS_KM = 6371.0

SATELLITES = pd.DataFrame(
    [
        {
            "asset": "Starlink-5412",
            "type": "Constellation",
            "altitude_km": 550,
            "x_km": 4120.4,
            "y_km": -4810.8,
            "z_km": 2288.1,
            "velocity_kms": 7.59,
        },
        {
            "asset": "Cartosat-2E",
            "type": "Earth Observation",
            "altitude_km": 630,
            "x_km": -2188.6,
            "y_km": 6244.2,
            "z_km": 1840.5,
            "velocity_kms": 7.54,
        },
        {
            "asset": "ISS",
            "type": "Station",
            "altitude_km": 420,
            "x_km": 5112.7,
            "y_km": 3120.4,
            "z_km": -3011.9,
            "velocity_kms": 7.66,
        },
        {
            "asset": "Debris-X9",
            "type": "Untracked Debris",
            "altitude_km": 628,
            "x_km": -2144.1,
            "y_km": 6210.8,
            "z_km": 1866.3,
            "velocity_kms": 7.55,
        },
    ]
)


def orbital_ring(radius: float, samples: int = 180, tilt_deg: float = 0.0) -> pd.DataFrame:
    theta = np.linspace(0, 2 * np.pi, samples)
    tilt = np.radians(tilt_deg)
    return pd.DataFrame(
        {
            "x_km": radius * np.cos(theta),
            "y_km": radius * np.sin(theta) * np.cos(tilt),
            "z_km": radius * np.sin(theta) * np.sin(tilt),
        }
    )


def build_orbit_figure(assets: pd.DataFrame, alert: bool) -> go.Figure:
    fig = px.scatter_3d(
        assets,
        x="x_km",
        y="y_km",
        z="z_km",
        color="asset",
        hover_name="asset",
        hover_data={"type": True, "altitude_km": True, "velocity_kms": True, "x_km": ":.1f", "y_km": ":.1f", "z_km": ":.1f"},
        color_discrete_map={
            "Starlink-5412": "#4cc9f0",
            "Cartosat-2E": "#80ed99",
            "ISS": "#ffd166",
            "Debris-X9": "#ff4d6d",
        },
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="#ffffff")))

    earth = go.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        mode="markers",
        name="Earth",
        marker=dict(size=28, color="#3a86ff", opacity=0.92, line=dict(width=2, color="#90e0ef")),
        hovertemplate="Earth (origin)<extra></extra>",
    )
    fig.add_trace(earth)

    for radius, tilt, color in (
        (EARTH_RADIUS_KM + 420, 51.6, "rgba(255, 209, 102, 0.28)"),
        (EARTH_RADIUS_KM + 550, 53.0, "rgba(76, 201, 240, 0.22)"),
        (EARTH_RADIUS_KM + 630, 97.5, "rgba(128, 237, 153, 0.22)"),
    ):
        ring = orbital_ring(radius, tilt_deg=tilt)
        fig.add_trace(
            go.Scatter3d(
                x=ring["x_km"],
                y=ring["y_km"],
                z=ring["z_km"],
                mode="lines",
                line=dict(color=color, width=2),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    if alert:
        cartosat = assets[assets["asset"] == "Cartosat-2E"].iloc[0]
        debris = assets[assets["asset"] == "Debris-X9"].iloc[0]
        fig.add_trace(
            go.Scatter3d(
                x=[cartosat["x_km"], debris["x_km"]],
                y=[cartosat["y_km"], debris["y_km"]],
                z=[cartosat["z_km"], debris["z_km"]],
                mode="lines",
                line=dict(color="#ff2d4a", width=6),
                name="Collision Vector",
                hovertemplate="Proximity corridor<extra></extra>",
            )
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(bgcolor="rgba(8,12,24,0.75)", bordercolor="#2a3a66", borderwidth=1),
        scene=dict(
            bgcolor="#070b16",
            xaxis=dict(title="X (km)", gridcolor="#1c2744", backgroundcolor="#070b16", zerolinecolor="#33415f"),
            yaxis=dict(title="Y (km)", gridcolor="#1c2744", backgroundcolor="#070b16", zerolinecolor="#33415f"),
            zaxis=dict(title="Z (km)", gridcolor="#1c2744", backgroundcolor="#070b16", zerolinecolor="#33415f"),
            camera=dict(eye=dict(x=1.55, y=1.35, z=0.95)),
            aspectmode="cube",
        ),
        title=dict(text="Live ECEF Positions · Earth at Origin", font=dict(size=16, color="#dce6ff")),
    )
    return fig


with st.sidebar:
    st.markdown("### 🛰️ AstroGuard IQ")
    st.caption("Quantum-Optimized Space Traffic Control")
    st.divider()
    section = st.radio(
        "Mission Console",
        ["1. Live Orbital Operations", "2. Quantum Resolution Matrix"],
        index=0,
    )

    st.markdown("### 💬 AI Space Traffic Copilot")
    st.caption("Issue orbital commands. Try “clear the path” or “resolve collision”.")

    copilot_log = st.container(height=280)
    with copilot_log:
        if not st.session_state.copilot_messages:
            with st.chat_message("assistant"):
                st.markdown("Copilot online. Standing by for traffic directives.")
        for message in st.session_state.copilot_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Command the copilot…")
    if prompt:
        st.session_state.copilot_messages.append({"role": "user", "content": prompt})
        lowered = prompt.strip().lower()
        if "clear the path" in lowered or "resolve collision" in lowered:
            reply = COPILOT_ALERT_REPLY
        else:
            reply = (
                "Directive acknowledged. Say **clear the path** or **resolve collision** "
                "to scan conjunction geometry."
            )
        st.session_state.copilot_messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.divider()
    st.markdown("**Watchlist**")
    st.caption("4 catalogued objects in LEO theater")
    st.caption("Conjunction screening: Cartosat-2E × Debris-X9")

st.markdown(
    """
    <div class="hero-kicker">Mission Control · Low Earth Orbit</div>
    <div class="hero-title">AstroGuard IQ: Quantum-Optimized Space Traffic Control</div>
    <div class="hero-sub">Real-time conjunction awareness fused with quantum-assisted conflict resolution.</div>
    """,
    unsafe_allow_html=True,
)

if section == "1. Live Orbital Operations":
    status_col, count_col, miss_col = st.columns(3)
    if st.session_state.alert_triggered:
        status_col.metric("System Status", "Collision Inbound", delta="CRITICAL", delta_color="inverse")
        miss_col.metric("Predicted Miss Distance", "0.41 km", delta="-18.7 km", delta_color="inverse")
    else:
        status_col.metric("System Status", "System Safe", delta="NOMINAL")
        miss_col.metric("Predicted Miss Distance", "19.1 km", delta="stable")
    count_col.metric("Active Catalog", "4 assets", delta="LEO")

    left, right = st.columns([1.15, 1.85], gap="large")

    with left:
        st.subheader("Active Satellite Catalog")
        st.dataframe(
            SATELLITES.rename(
                columns={
                    "asset": "Asset",
                    "type": "Class",
                    "altitude_km": "Altitude (km)",
                    "x_km": "X (km)",
                    "y_km": "Y (km)",
                    "z_km": "Z (km)",
                    "velocity_kms": "Velocity (km/s)",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.caption("Coordinates are Earth-Centered Earth-Fixed (ECEF) kilometers from Earth's geometric center.")

        if st.button("Trigger Proximity Alert"):
            st.session_state.alert_triggered = True
            st.rerun()

        if st.session_state.alert_triggered:
            st.error("CRITICAL ALERT: Debris-X9 is on a collision course with Cartosat-2E!")

    with right:
        st.plotly_chart(
            build_orbit_figure(SATELLITES, st.session_state.alert_triggered),
            use_container_width=True,
        )

else:
    st.subheader("Quantum Resolution Matrix")
    st.caption("QUBO-style conflict graph for LEO conjunction pairs. Dummy scores for demonstration.")

    assets = SATELLITES["asset"].tolist()
    n = len(assets)
    rng = np.random.default_rng(42)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            risk = float(rng.uniform(0.05, 0.35))
            if {assets[i], assets[j]} == {"Cartosat-2E", "Debris-X9"}:
                risk = 0.97 if st.session_state.alert_triggered else 0.62
            matrix[i, j] = matrix[j, i] = risk

    heat = px.imshow(
        matrix,
        x=assets,
        y=assets,
        color_continuous_scale="Turbo",
        labels=dict(color="Collision Risk"),
        text_auto=".2f",
    )
    heat.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        title="Pairwise Conjunction Risk Matrix",
        coloraxis_colorbar=dict(title="Risk"),
    )

    c1, c2 = st.columns([1.4, 1])
    with c1:
        st.plotly_chart(heat, use_container_width=True)
    with c2:
        st.markdown("#### Solver posture")
        if st.session_state.alert_triggered:
            st.warning("Quantum annealer queued: minimize Δv for Cartosat-2E vs Debris-X9.")
            st.metric("Priority Pair", "Cartosat-2E × Debris-X9")
            st.metric("Recommended Maneuver", "Radial +0.12 m/s")
        else:
            st.info("No critical QUBO constraints. Traffic remains separable.")
            st.metric("Priority Pair", "None")
            st.metric("Recommended Maneuver", "Hold")
        st.caption("Switch to Live Orbital Operations and trigger the proximity alert to escalate this matrix.")
