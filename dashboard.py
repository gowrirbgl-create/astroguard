import math

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
if "cam_t" not in st.session_state:
    st.session_state.cam_t = 0.0

COPILOT_ALERT_REPLY = (
    "Scanning orbital coordinates... Collision vector detected between "
    "Cartosat-2E and Debris-X9. Awaiting deployment commands for the "
    "Qiskit QAOA Optimization engine on IBM Quantum hardware."
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

        :root {
            --void: #0A0C10;
            --panel: #12161F;
            --titanium: #F4F7FB;
            --mint: #5CFFC7;
            --neon-red: #FF1F4B;
            --cyan: #4DE2FF;
            --grid: rgba(77, 226, 255, 0.07);
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #0A0C10 !important;
            color: #F4F7FB;
            font-family: "Rajdhani", sans-serif;
        }

        .stApp {
            background-image:
                radial-gradient(ellipse at 18% -8%, rgba(77, 226, 255, 0.12), transparent 42%),
                radial-gradient(ellipse at 88% 0%, rgba(92, 255, 199, 0.08), transparent 36%),
                linear-gradient(rgba(77, 226, 255, 0.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(77, 226, 255, 0.045) 1px, transparent 1px) !important;
            background-size: auto, auto, 42px 42px, 42px 42px !important;
            background-color: #0A0C10 !important;
        }

        [data-testid="stHeader"] {
            background: rgba(10, 12, 16, 0.55) !important;
            backdrop-filter: blur(16px);
        }

        .block-container {
            padding-top: 1.15rem;
            max-width: 1480px;
        }

        h1, h2, h3, h4, .hero-title {
            font-family: "Orbitron", sans-serif !important;
            color: #F4F7FB !important;
            letter-spacing: 0.06em;
            text-shadow: 0 0 18px rgba(244, 247, 251, 0.18);
        }

        p, label, span, .stMarkdown, .stCaption {
            font-family: "Rajdhani", sans-serif;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 12, 16, 0.72) 0%, rgba(18, 22, 31, 0.55) 100%) !important;
            backdrop-filter: blur(22px) saturate(140%);
            border-right: 1px solid rgba(77, 226, 255, 0.35) !important;
            box-shadow: 8px 0 40px rgba(77, 226, 255, 0.08);
        }

        [data-testid="stSidebar"] > div:first-child {
            background: transparent !important;
        }

        [data-testid="stSidebar"] * {
            color: #E8EEF8 !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(18, 22, 31, 0.55);
            border: 1px solid rgba(77, 226, 255, 0.45);
            border-radius: 16px;
            box-shadow: 0 0 24px rgba(77, 226, 255, 0.12), inset 0 0 24px rgba(92, 255, 199, 0.04);
            backdrop-filter: blur(18px);
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] details {
            background: transparent !important;
        }

        [data-testid="stSidebar"] [data-testid="stChatMessage"] {
            background: rgba(10, 12, 16, 0.72) !important;
            border: 1px solid rgba(77, 226, 255, 0.22);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        .hero-kicker {
            font-family: "Share Tech Mono", monospace;
            color: #4DE2FF;
            font-size: 0.78rem;
            letter-spacing: 0.32em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .hero-title {
            font-size: 1.72rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .hero-sub {
            color: #9AA8C0;
            font-size: 1.05rem;
            margin-bottom: 1.1rem;
        }

        .bento-row {
            display: grid;
            grid-template-columns: 1.4fr 1fr 1fr;
            gap: 0.85rem;
            margin: 0.4rem 0 1.15rem 0;
        }

        .op-card {
            background: linear-gradient(165deg, rgba(18, 22, 31, 0.96) 0%, rgba(10, 12, 16, 0.92) 100%);
            border: 1px solid rgba(77, 226, 255, 0.22);
            border-radius: 16px;
            padding: 1rem 1.15rem 1.05rem 1.15rem;
            box-shadow: 0 10px 36px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.04);
            position: relative;
            overflow: hidden;
        }

        .op-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, transparent 20%, rgba(77, 226, 255, 0.06) 50%, transparent 80%);
            pointer-events: none;
        }

        .op-label {
            font-family: "Share Tech Mono", monospace;
            font-size: 0.72rem;
            letter-spacing: 0.18em;
            color: #8FA0B8;
            text-transform: uppercase;
        }

        .op-value {
            font-family: "Orbitron", sans-serif;
            font-weight: 600;
            font-size: 1.18rem;
            color: #F4F7FB;
            margin-top: 0.35rem;
        }

        .op-meta {
            font-family: "Share Tech Mono", monospace;
            font-size: 0.78rem;
            color: #5CFFC7;
            margin-top: 0.25rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-family: "Share Tech Mono", monospace;
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            padding: 0.42rem 0.7rem;
            border-radius: 999px;
            margin-top: 0.55rem;
        }

        .status-badge .dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-badge.operational {
            color: #5CFFC7;
            border: 1px solid rgba(92, 255, 199, 0.55);
            background: rgba(92, 255, 199, 0.08);
            box-shadow: 0 0 18px rgba(92, 255, 199, 0.25);
            animation: mintPulse 2.2s ease-in-out infinite;
        }

        .status-badge.operational .dot {
            background: #5CFFC7;
            box-shadow: 0 0 10px #5CFFC7;
        }

        .status-badge.alert,
        .op-card.alert-mode .status-badge {
            color: #FFD6DE;
            border: 1px solid #FF1F4B;
            background: rgba(255, 31, 75, 0.18);
            animation: none;
        }

        .op-card.alert-mode {
            border-color: #FF1F4B;
            animation: neonAlert 0.85s ease-in-out infinite;
        }

        .op-card.alert-mode .op-value,
        .op-card.alert-mode .op-meta {
            color: #FF8A9B;
        }

        @keyframes mintPulse {
            0%, 100% { box-shadow: 0 0 10px rgba(92, 255, 199, 0.18); }
            50% { box-shadow: 0 0 26px rgba(92, 255, 199, 0.55); }
        }

        @keyframes neonAlert {
            0%, 100% {
                box-shadow: 0 0 8px rgba(255, 31, 75, 0.25);
                background: linear-gradient(165deg, rgba(40, 8, 16, 0.96) 0%, rgba(10, 12, 16, 0.92) 100%);
            }
            50% {
                box-shadow: 0 0 34px rgba(255, 31, 75, 0.85);
                background: linear-gradient(165deg, rgba(90, 8, 22, 0.98) 0%, rgba(18, 6, 10, 0.95) 100%);
            }
        }

        div.stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #FF1F4B 0%, #C1121F 100%);
            color: #ffffff !important;
            border: 1px solid #FF6B81;
            border-radius: 12px;
            font-family: "Orbitron", sans-serif;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 0.9rem 1.2rem;
            box-shadow: 0 0 22px rgba(255, 31, 75, 0.38);
        }

        div.stButton > button:hover {
            background: linear-gradient(90deg, #ff4d67 0%, #e11d2e 100%);
            border-color: #ff8a9b;
        }

        [data-testid="stMetric"] {
            background: #12161F;
            border: 1px solid rgba(77, 226, 255, 0.22);
            border-radius: 14px;
            padding: 0.85rem 1rem;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid rgba(77, 226, 255, 0.2);
            border-radius: 12px;
            background: #12161F;
        }

        [data-testid="stPlotlyChart"] {
            background: #12161F;
            border: 1px solid rgba(77, 226, 255, 0.2);
            border-radius: 16px;
            padding: 0.35rem;
            box-shadow: 0 0 28px rgba(77, 226, 255, 0.08);
        }

        .nova-panel {
            background: #12161F;
            border: 1px solid rgba(77, 226, 255, 0.2);
            border-radius: 16px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }

        @media (max-width: 1100px) {
            .bento-row { grid-template-columns: 1fr; }
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


def orbital_ring(radius: float, samples: int = 180, tilt_deg: float = 0.0, phase: float = 0.0) -> pd.DataFrame:
    theta = np.linspace(0, 2 * np.pi, samples) + phase
    tilt = np.radians(tilt_deg)
    return pd.DataFrame(
        {
            "x_km": radius * np.cos(theta),
            "y_km": radius * np.sin(theta) * np.cos(tilt),
            "z_km": radius * np.sin(theta) * np.sin(tilt),
        }
    )


def camera_trajectory(radius: float, samples: int = 220, pitch: float = 0.32, phase: float = 0.0) -> pd.DataFrame:
    t = np.linspace(0, 2 * np.pi, samples) + phase
    return pd.DataFrame(
        {
            "x_km": radius * np.cos(t),
            "y_km": radius * np.sin(t) * np.cos(pitch),
            "z_km": radius * 0.42 * np.sin(2 * t + pitch),
        }
    )


def rotate_assets(assets: pd.DataFrame, angle: float) -> pd.DataFrame:
    out = assets.copy()
    c, s = math.cos(angle), math.sin(angle)
    x = out["x_km"].to_numpy()
    y = out["y_km"].to_numpy()
    out["x_km"] = c * x - s * y
    out["y_km"] = s * x + c * y
    return out


def build_orbit_figure(assets: pd.DataFrame, alert: bool, t: float) -> go.Figure:
    palette = {
        "Starlink-5412": "#4DE2FF",
        "Cartosat-2E": "#5CFFC7",
        "ISS": "#F4F7FB",
        "Debris-X9": "#FF1F4B",
    }

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers",
            name="Earth",
            marker=dict(size=34, color="#1B4DFF", opacity=0.95, line=dict(width=3, color="#4DE2FF")),
            hovertemplate="Earth (origin)<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode="markers",
            showlegend=False,
            marker=dict(size=52, color="rgba(77, 226, 255, 0.16)"),
            hoverinfo="skip",
        )
    )

    for radius, tilt, color, phase in (
        (EARTH_RADIUS_KM + 420, 51.6, "rgba(244, 247, 251, 0.28)", t * 0.35),
        (EARTH_RADIUS_KM + 550, 53.0, "rgba(77, 226, 255, 0.32)", -t * 0.28),
        (EARTH_RADIUS_KM + 630, 97.5, "rgba(92, 255, 199, 0.28)", t * 0.22),
    ):
        ring = orbital_ring(radius, tilt_deg=tilt, phase=phase)
        fig.add_trace(
            go.Scatter3d(
                x=ring["x_km"],
                y=ring["y_km"],
                z=ring["z_km"],
                mode="lines",
                line=dict(color=color, width=3),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    for radius, pitch, color, phase in (
        (9200, 0.28, "rgba(77, 226, 255, 0.55)", t * 0.55),
        (10800, 0.51, "rgba(92, 255, 199, 0.38)", -t * 0.4),
        (12400, 0.18, "rgba(244, 247, 251, 0.22)", t * 0.18),
    ):
        path = camera_trajectory(radius, pitch=pitch, phase=phase)
        fig.add_trace(
            go.Scatter3d(
                x=path["x_km"],
                y=path["y_km"],
                z=path["z_km"],
                mode="lines",
                line=dict(color=color, width=2),
                name="Camera Vector" if radius == 9200 else None,
                showlegend=radius == 9200,
                hoverinfo="skip",
            )
        )

    for _, row in assets.iterrows():
        color = palette.get(row["asset"], "#4DE2FF")
        fig.add_trace(
            go.Scatter3d(
                x=[row["x_km"]],
                y=[row["y_km"]],
                z=[row["z_km"]],
                mode="markers",
                name=row["asset"],
                marker=dict(size=16, color=color, opacity=0.18),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[row["x_km"]],
                y=[row["y_km"]],
                z=[row["z_km"]],
                mode="markers",
                name=row["asset"],
                marker=dict(size=7, color=color, opacity=1.0, line=dict(width=2, color="#F4F7FB")),
                hovertemplate=(
                    f"{row['asset']}<br>{row['type']}<br>"
                    f"Alt {row['altitude_km']} km<br>"
                    f"V {row['velocity_kms']} km/s<extra></extra>"
                ),
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
                line=dict(color="#FF1F4B", width=7),
                name="Collision Vector",
                hovertemplate="Proximity corridor<extra></extra>",
            )
        )

    cam_r = 1.72
    eye = dict(
        x=cam_r * math.cos(t * 0.35),
        y=cam_r * math.sin(t * 0.35),
        z=0.72 + 0.28 * math.sin(t * 0.22),
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=36, b=0),
        legend=dict(bgcolor="rgba(18,22,31,0.82)", bordercolor="rgba(77,226,255,0.28)", borderwidth=1, font=dict(family="Rajdhani", color="#F4F7FB")),
        scene=dict(
            bgcolor="#0A0C10",
            xaxis=dict(title="X (km)", gridcolor="#1C2433", backgroundcolor="#0A0C10", zerolinecolor="#2A3448", color="#9AA8C0"),
            yaxis=dict(title="Y (km)", gridcolor="#1C2433", backgroundcolor="#0A0C10", zerolinecolor="#2A3448", color="#9AA8C0"),
            zaxis=dict(title="Z (km)", gridcolor="#1C2433", backgroundcolor="#0A0C10", zerolinecolor="#2A3448", color="#9AA8C0"),
            camera=dict(eye=eye, center=dict(x=0, y=0, z=0)),
            aspectmode="cube",
        ),
        title=dict(text="LIVE ECEF TELEMETRY · CAMERA VECTOR LOCK", font=dict(family="Orbitron", size=14, color="#F4F7FB")),
        uirevision="astroguard-orbit",
    )
    return fig


def render_bento_cards(alert: bool) -> None:
    if alert:
        status_html = """
        <div class="bento-row">
            <div class="op-card alert-mode">
                <div class="op-label">System Telemetry</div>
                <div class="op-value">Collision Inbound</div>
                <div class="status-badge alert"><span class="dot"></span>CRITICAL INTERCEPT DETECTED</div>
            </div>
            <div class="op-card alert-mode">
                <div class="op-label">Active Catalog</div>
                <div class="op-value">4 assets</div>
                <div class="op-meta">LEO THEATER LOCKED</div>
            </div>
            <div class="op-card alert-mode">
                <div class="op-label">Predicted Miss Distance</div>
                <div class="op-value">0.41 km</div>
                <div class="op-meta">Δ −18.7 km</div>
            </div>
        </div>
        """
    else:
        status_html = """
        <div class="bento-row">
            <div class="op-card">
                <div class="op-label">System Telemetry</div>
                <div class="op-value">System Safe</div>
                <div class="status-badge operational"><span class="dot"></span>SYSTEM STATUS: OPERATIONAL</div>
            </div>
            <div class="op-card">
                <div class="op-label">Active Catalog</div>
                <div class="op-value">4 assets</div>
                <div class="op-meta">LEO</div>
            </div>
            <div class="op-card">
                <div class="op-label">Predicted Miss Distance</div>
                <div class="op-value">19.1 km</div>
                <div class="op-meta">STABLE</div>
            </div>
        </div>
        """
    st.markdown(status_html, unsafe_allow_html=True)


@st.fragment(run_every=0.4)
def render_live_globe() -> None:
    st.session_state.cam_t += 0.12
    t = st.session_state.cam_t
    moving = rotate_assets(SATELLITES, t * 0.28)
    globe_slot = st.empty()
    globe_slot.plotly_chart(
        build_orbit_figure(moving, st.session_state.alert_triggered, t),
        use_container_width=True,
        key="orbit_live_canvas",
    )


with st.sidebar:
    st.markdown("### 🛰️ AstroGuard IQ")
    st.caption("Quantum-Optimized Space Traffic Control")
    st.divider()
    section = st.radio(
        "Mission Console",
        ["1. Live Orbital Operations", "2. Quantum Resolution Matrix"],
        index=0,
    )

    with st.expander("💬 AI Space Traffic Copilot", expanded=True):
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
    render_bento_cards(st.session_state.alert_triggered)

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
        render_live_globe()

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
        font=dict(family="Rajdhani", color="#F4F7FB"),
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
