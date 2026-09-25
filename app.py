import streamlit as st
import plotly.graph_objects as go

from data import APPLIANCE_WATTAGE, AC_HP_TO_WATT
from calculations import calculate_kwh, calculate_tnb_cost, calculate_co2
from ui_components import (
    APPLIANCE_META, APPLIANCE_ORDER, TIPS,
    sorted_appliance_breakdown, top_driver_impact, generate_recommendations,
    efficiency_score, build_csv_report,
)
from ai_recommendations import get_ai_recommendations

st.set_page_config(page_title="EnergiSmart | Energy Advisor", page_icon="⚡", layout="wide")

# =================================================================
# SESSION STATE
# =================================================================
if "page" not in st.session_state:
    st.session_state.page = "landing"  # landing -> household -> appliances -> results

def go_to(page):
    st.session_state.page = page

# =================================================================
# DESIGN SYSTEM (CSS)
# =================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.stApp { background-color: #fbfdfc; }

.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1040px; }

/* ---------- NAV ---------- */
.navbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.6rem 0 1.2rem 0; border-bottom: 1px solid #e6efe9; margin-bottom: 1.6rem;
    flex-wrap: wrap; gap: 0.6rem;
}
.navbar .brand { font-size: 1.25rem; font-weight: 800; color: #1b4332; }
.navbar .brand span { color: #40916c; }
.navbar .links { display: flex; gap: 1.2rem; align-items: center; flex-wrap: wrap; }
.navbar .links a {
    font-size: 0.82rem; font-weight: 500; color: #52796f; text-decoration: none;
}
.navbar .flag {
    background: #f1f8f4; border: 1px solid #d8ecdf; color: #2d6a4f;
    font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.65rem; border-radius: 999px;
}

/* ---------- HERO ---------- */
.hero-wrap { text-align: center; padding: 2.4rem 1rem 1.6rem 1rem; }
.hero-wrap h1 {
    font-size: 2.4rem; font-weight: 800; color: #1b4332; margin: 0 0 0.8rem 0; line-height: 1.15;
}
.hero-wrap p.sub {
    font-size: 1.02rem; color: #52796f; max-width: 560px; margin: 0 auto 1.6rem auto; line-height: 1.55;
}
.hero-note { font-size: 0.82rem; color: #74a892; margin-top: 0.9rem; font-weight: 500; }

/* ---------- PROGRESS STEPS ---------- */
.steps-row { display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin: 0.4rem 0 2rem 0; }
.step-pill {
    display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 999px;
    font-size: 0.82rem; font-weight: 600; background: #f1f8f4; color: #95a89c; border: 1px solid #e6efe9;
}
.step-pill.active { background: #1b4332; color: white; border-color: #1b4332; }
.step-pill.done { background: #e9f5ee; color: #2d6a4f; border-color: #b7e4c7; }
.step-line { width: 28px; height: 2px; background: #d8ecdf; }

/* ---------- CARDS ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    box-shadow: 0 1px 5px rgba(27,67,50,0.05);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 16px rgba(27,67,50,0.10);
}

.app-card-icon { font-size: 1.6rem; margin-bottom: 0.15rem; }
.app-card-name { font-weight: 700; color: #1b4332; font-size: 0.98rem; }
.app-card-desc { font-size: 0.78rem; color: #8aa89a; margin-bottom: 0.4rem; }

/* ---------- BUTTONS ---------- */
.stButton>button {
    border-radius: 12px; font-weight: 600; padding: 0.65rem 1.1rem;
    border: none; letter-spacing: 0.2px; transition: transform 0.1s ease;
}
.stButton>button[kind="primary"] {
    background: #1b4332; color: white; box-shadow: 0 4px 12px rgba(27,67,50,0.22);
}
.stButton>button[kind="primary"]:hover { background: #143024; color: white; }
.stButton>button[kind="secondary"] {
    background: white; color: #2d6a4f; border: 1.5px solid #cfe6d8;
}

/* ---------- SUMMARY BAR ---------- */
.summary-bar {
    background: linear-gradient(120deg, #1b4332, #2d6a4f);
    border-radius: 16px; padding: 1.2rem 1.6rem; color: white;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;
    margin: 1.4rem 0 1.6rem 0; box-shadow: 0 6px 18px rgba(27,67,50,0.18);
}
.summary-bar .sb-label { font-size: 0.72rem; opacity: 0.75; text-transform: uppercase; letter-spacing: 0.6px; }
.summary-bar .sb-value { font-size: 1.35rem; font-weight: 700; }

/* ---------- KPI CARDS ---------- */
.kpi-row { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.2rem 0 1.6rem 0; }
.kpi-card {
    flex: 1; min-width: 210px; background: white; border-radius: 16px; padding: 1.3rem 1.3rem;
    box-shadow: 0 3px 14px rgba(27,67,50,0.07); border-top: 4px solid #2d6a4f;
}
.kpi-card.amber { border-top-color: #e8a33d; }
.kpi-card.blue { border-top-color: #457b9d; }
.kpi-icon { font-size: 1.4rem; }
.kpi-label { font-size: 0.74rem; font-weight: 700; color: #8aa89a; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.3rem; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #1b4332; margin-top: 0.15rem; }
.kpi-value span { font-size: 0.95rem; font-weight: 500; color: #74a892; }
.kpi-explain { font-size: 0.76rem; color: #95a89c; margin-top: 0.35rem; }

/* ---------- INSIGHT / REC CARDS ---------- */
.insight-card {
    background: white; border-radius: 16px; padding: 1.3rem 1.4rem; border-left: 4px solid #e8a33d;
    box-shadow: 0 2px 10px rgba(27,67,50,0.06); margin-bottom: 1rem;
}
.rec-card {
    background: white; border-radius: 16px; padding: 1.1rem 1.3rem; border: 1px solid #eaf2ee;
    box-shadow: 0 2px 8px rgba(27,67,50,0.05); margin-bottom: 0.8rem;
    display: flex; gap: 0.9rem; align-items: flex-start;
}
.rec-num {
    font-size: 0.72rem; font-weight: 800; color: #b7e4c7; min-width: 22px;
}
.rec-title { font-weight: 700; color: #1b4332; font-size: 0.95rem; margin-bottom: 0.15rem; }
.rec-body { font-size: 0.84rem; color: #52796f; line-height: 1.5; }

/* ---------- BILL TABLE ---------- */
.bill-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.bill-table td { padding: 0.5rem 0.2rem; border-bottom: 1px solid #eef4f0; color: #40534a; }
.bill-table td.amt { text-align: right; font-weight: 600; }
.bill-table tr.total td { font-weight: 800; color: #1b4332; font-size: 1rem; border-top: 2px solid #1b4332; border-bottom: none; padding-top: 0.7rem; }
.bill-note { font-size: 0.75rem; color: #95a89c; margin-top: 0.6rem; }

/* ---------- GLANCE CARD ---------- */
.glance-card {
    background: #f1f8f4; border: 1px solid #d8ecdf; border-radius: 16px; padding: 1.4rem 1.5rem;
}
.glance-row { display: flex; justify-content: space-between; padding: 0.4rem 0; font-size: 0.92rem; color: #1b4332; }
.glance-row .l { color: #52796f; }
.glance-row .v { font-weight: 700; }

.empty-state {
    text-align: center; padding: 2.2rem 1.4rem; background: #f1f8f4; border: 1px dashed #b7e4c7;
    border-radius: 16px; color: #2d6a4f;
}

.app-footer { text-align: center; color: #a9bdb2; font-size: 0.76rem; margin-top: 3rem; padding-top: 1.1rem; border-top: 1px solid #eef4f0; }
</style>
""", unsafe_allow_html=True)

# =================================================================
# NAV (always shown)
# =================================================================
st.markdown("""
<div class="navbar">
    <div class="brand">⚡ Energi<span>Smart</span></div>
    <div class="links">
        <a href="#">Energy Advisor</a>
        <a href="#">How It Works</a>
        <a href="#">About</a>
        <span class="flag">🇲🇾 Malaysia</span>
    </div>
</div>
""", unsafe_allow_html=True)


def progress_steps(current):
    """current: 1, 2, or 3"""
    labels = ["01 Household", "02 Appliances", "03 Analysis"]
    html = '<div class="steps-row">'
    for i, label in enumerate(labels, start=1):
        cls = "active" if i == current else ("done" if i < current else "")
        html += f'<div class="step-pill {cls}">{label}</div>'
        if i < 3:
            html += '<div class="step-line"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# =================================================================
# PAGE: LANDING
# =================================================================
if st.session_state.page == "landing":
    st.markdown("""
    <div class="hero-wrap">
        <h1>Understand Your Home's Energy.</h1>
        <p class="sub">Estimate your electricity usage, monthly TNB cost, and carbon footprint —
        and discover where you can save.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Start Energy Assessment →", type="primary", use_container_width=True):
            go_to("household")
            st.rerun()
    st.markdown('<p style="text-align:center;" class="hero-note">🔒 No smart meter required · Based on official TNB rates · Takes about 2 minutes</p>', unsafe_allow_html=True)

# =================================================================
# PAGE: HOUSEHOLD (step 1)
# =================================================================
elif st.session_state.page == "household":
    progress_steps(1)
    st.markdown("### Let's build your energy profile.")
    st.caption("A few basics about your home — this helps us calculate your estimate accurately.")

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**👨‍👩‍👧‍👦 Household Size**")
            st.number_input("Number of occupants", min_value=1, max_value=20, value=4, key="occupants", label_visibility="collapsed")
        with c2:
            st.markdown("**🏠 Home Type**")
            st.selectbox("Home type", ["Terrace House", "Apartment/Condo", "Semi-Detached", "Bungalow"],
                         key="home_type", label_visibility="collapsed")

        st.markdown("**💳 Current Monthly Bill (RM)**")
        st.caption("Approximate — this is for comparison only and does not affect the calculation.")
        st.number_input("Average monthly TNB bill (RM)", min_value=0.0, value=180.0, step=10.0,
                         key="avg_bill", label_visibility="collapsed")

    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Back", type="secondary", use_container_width=True):
            go_to("landing")
            st.rerun()
    with c2:
        if st.button("Continue to Appliances →", type="primary", use_container_width=True):
            st.session_state.occupants_saved = st.session_state.get("occupants", 4)
            go_to("appliances")
            st.rerun()

# =================================================================
# HELPERS shared by appliances + results pages
# =================================================================

def get_appliance_inputs():
    """Reads current selections straight from session_state (widget keys)."""
    inputs = {}
    for name in APPLIANCE_ORDER:
        if st.session_state.get(f"sel_{name}", False):
            if name == "Air Conditioner":
                hp = st.session_state.get("ac_hp", 1.0)
                hours = st.session_state.get("ac_hours", 8)
                watts = AC_HP_TO_WATT[hp]
            elif name == "Lighting":
                bulbs = st.session_state.get("light_bulbs", 6)
                hours = st.session_state.get("light_hours", 6)
                watts = APPLIANCE_WATTAGE["Lighting"] * bulbs
            elif name == "Refrigerator":
                hours = 24
                watts = APPLIANCE_WATTAGE["Refrigerator"]
            else:
                hours = st.session_state.get(f"{name}_hours", 2)
                watts = APPLIANCE_WATTAGE[name]
            inputs[name] = (watts, hours)
    return inputs


def render_appliance_card(name):
    meta = APPLIANCE_META[name]
    with st.container(border=True):
        st.markdown(f'<div class="app-card-icon">{meta["icon"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="app-card-name">{name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="app-card-desc">{meta["desc"]}</div>', unsafe_allow_html=True)

        selected = st.toggle("Selected", key=f"sel_{name}")

        if selected:
            if name == "Air Conditioner":
                c1, c2 = st.columns(2)
                with c1:
                    st.selectbox("Capacity", list(AC_HP_TO_WATT.keys()), key="ac_hp",
                                 format_func=lambda x: f"{x} HP")
                with c2:
                    st.slider("Daily usage (hrs)", 0, 24, 8, key="ac_hours")
            elif name == "Lighting":
                c1, c2 = st.columns(2)
                with c1:
                    st.number_input("Number of bulbs", min_value=1, max_value=50, value=6, key="light_bulbs")
                with c2:
                    st.slider("Daily usage (hrs)", 0, 24, 6, key="light_hours")
            elif name == "Refrigerator":
                st.caption("Runs continuously: 24 hrs/day (fixed)")
            else:
                default_hours = 2
                st.slider("Daily usage (hrs)", 0, 24, default_hours, key=f"{name}_hours")


# =================================================================
# PAGE: APPLIANCES (step 2)
# =================================================================
if st.session_state.page == "appliances":
    progress_steps(2)
    st.markdown("### Tell us what's running in your home.")
    st.caption("Select the appliances you use and tell us how often they run.")

    for i in range(0, len(APPLIANCE_ORDER), 2):
        pair = APPLIANCE_ORDER[i:i + 2]
        cols = st.columns(2)
        for col, name in zip(cols, pair):
            with col:
                render_appliance_card(name)

    # ---- live summary panel ----
    inputs_now = get_appliance_inputs()
    n_selected = len(inputs_now)
    daily_kwh = sum((w / 1000) * h for w, h in inputs_now.values())
    monthly_kwh = daily_kwh * 30

    st.markdown(f"""
    <div class="summary-bar">
        <div><div class="sb-label">Your Home</div><div class="sb-value">{n_selected} appliance{"s" if n_selected != 1 else ""} selected</div></div>
        <div><div class="sb-label">Estimated daily usage</div><div class="sb-value">{daily_kwh:.1f} kWh</div></div>
        <div><div class="sb-label">Estimated monthly usage</div><div class="sb-value">{monthly_kwh:.1f} kWh</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Back", type="secondary", use_container_width=True):
            go_to("household")
            st.rerun()
    with c2:
        generate = st.button("Generate My Energy Report →", type="primary", use_container_width=True)

    if generate:
        if not inputs_now:
            st.markdown("""
            <div class="empty-state">
                <b>Your energy profile is waiting</b><br/>
                Select at least one appliance to generate your personalised energy report.
            </div>
            """, unsafe_allow_html=True)
        else:
            go_to("results")
            st.rerun()

# =================================================================
# PAGE: RESULTS (step 3)
# =================================================================
elif st.session_state.page == "results":
    progress_steps(3)

    appliance_inputs = get_appliance_inputs()
    occupants = st.session_state.get("occupants_saved", st.session_state.get("occupants", 4))

    if not appliance_inputs:
        st.markdown("""
        <div class="empty-state">
            <b>Your energy profile is waiting</b><br/>
            Select at least one appliance to generate your personalised energy report.
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Back to Appliances", type="primary"):
            go_to("appliances")
            st.rerun()
        st.stop()

    breakdown = sorted_appliance_breakdown(appliance_inputs, calculate_kwh)
    total_kwh = sum(row["kwh"] for row in breakdown)
    cost = calculate_tnb_cost(total_kwh)
    co2 = calculate_co2(total_kwh)
    score = efficiency_score(total_kwh, occupants)

    # ---------- 1. Header ----------
    st.markdown("### Your Energy Report")
    st.caption("Here's how your household is using energy.")

    # ---------- 2. KPI row ----------
    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card amber">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-label">Monthly Usage</div>
            <div class="kpi-value">{total_kwh:.1f} <span>kWh</span></div>
            <div class="kpi-explain">Estimated household usage</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">RM</div>
            <div class="kpi-label">Estimated Monthly Bill</div>
            <div class="kpi-value">RM {cost['total_cost_rm']:.2f}</div>
            <div class="kpi-explain">Based on TNB's tiered tariff</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-icon">🌍</div>
            <div class="kpi-label">Carbon Footprint</div>
            <div class="kpi-value">{co2:.1f} <span>kg CO2</span></div>
            <div class="kpi-explain">Based on Malaysia's 2024 grid factor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------- 3. Charts ----------
    st.markdown("#### Energy Consumption by Appliance")
    chart_c1, chart_c2 = st.columns([1.3, 1])

    with chart_c1:
        names = [f'{APPLIANCE_META[r["name"]]["icon"]} {r["name"]}' for r in breakdown]
        kwhs = [r["kwh"] for r in breakdown]
        fig_bar = go.Figure(go.Bar(
            x=kwhs, y=names, orientation="h",
            marker_color="#2d6a4f",
            text=[f"{v:.0f} kWh" for v in kwhs], textposition="outside",
        ))
        fig_bar.update_layout(
            height=max(260, 46 * len(names)),
            margin=dict(l=10, r=30, t=10, b=10),
            xaxis_title="kWh / month", yaxis=dict(autorange="reversed"),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Poppins, sans-serif", size=12, color="#1b4332"),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with chart_c2:
        palette = ["#2d6a4f", "#40916c", "#74c69d", "#95d5b2", "#b7e4c7", "#e8a33d", "#457b9d", "#a8dadc", "#cfe6d8", "#d8ecdf"]
        fig_donut = go.Figure(go.Pie(
            labels=[r["name"] for r in breakdown], values=[r["kwh"] for r in breakdown],
            hole=0.55, marker=dict(colors=palette[:len(breakdown)]),
            textinfo="percent", textfont=dict(size=11),
        ))
        fig_donut.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True, legend=dict(font=dict(size=10)),
            font=dict(family="Poppins, sans-serif", color="#1b4332"),
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    # ---------- 4. Biggest energy drivers ----------
    st.markdown("#### Your Biggest Energy Drivers")
    top = breakdown[0]
    share = round((top["kwh"] / total_kwh) * 100, 1) if total_kwh > 0 else 0
    impact = top_driver_impact(breakdown, total_kwh, calculate_tnb_cost)

    impact_text = ""
    if impact:
        impact_text = (f'<br/><br/><b>Potential impact:</b> Reducing usage by {impact["reduce_hours"]} '
                        f'hrs/day could save approximately {impact["kwh_saved"]:.1f} kWh and '
                        f'RM {impact["rm_saved"]:.2f} per month.')

    st.markdown(f"""
    <div class="insight-card">
        <div style="font-size:1.3rem;">{APPLIANCE_META[top["name"]]["icon"]} <b>{top["name"]}</b></div>
        <div style="color:#95a89c; font-size:0.8rem; margin-bottom:0.4rem;">Your biggest energy consumer</div>
        Your {top["name"].lower()} accounts for approximately <b>{share}%</b> of your estimated monthly electricity usage.{impact_text}
    </div>
    """, unsafe_allow_html=True)

        # ---------- 5. Smart recommendations ----------
    st.markdown("#### Smart Energy Recommendations")

    with st.spinner("Generating personalised recommendations..."):
        recs, rec_source = get_ai_recommendations(
            breakdown, total_kwh, cost, co2, occupants, calculate_tnb_cost
        )

    if rec_source == "ai":
        st.caption("✨ AI-personalised recommendations, generated from your calculated usage data.")
    else:
        st.caption("Rule-based tips generated from your calculated usage. "
                   "(AI recommendations were unavailable for this request, so these "
                   "reliable fallback tips are shown instead.)")

    for i, rec in enumerate(recs, start=1):
        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-num">{i:02d}</div>
            <div>
                <div class="rec-title">{rec["icon"]} {rec["title"]}</div>
                <div class="rec-body">{rec["body"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------- 6. Efficiency score ----------
    st.markdown("#### Energy Efficiency Score")
    score_c1, score_c2 = st.columns([1, 1.4])
    with score_c1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score["score"],
            number={"suffix": " / 100", "font": {"size": 30, "color": "#1b4332"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0.5},
                "bar": {"color": "#2d6a4f"},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, 40], "color": "#fbe4d5"},
                    {"range": [40, 60], "color": "#fdf0d0"},
                    {"range": [60, 80], "color": "#e6f4ea"},
                    {"range": [80, 100], "color": "#d8ecdf"},
                ],
            },
        ))
        fig_gauge.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=10),
                                 font=dict(family="Poppins, sans-serif"))
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
    with score_c2:
        st.markdown(f"**{score['band']}** — {score['message']}")
        with st.expander("How is this score calculated?"):
            st.write(
                f"This is an **estimated, transparency-first score** - not a scientific or "
                f"official rating. It compares your usage per occupant "
                f"({score['usage_per_person']} kWh/person/month) against a reference "
                f"benchmark of {score['benchmark']} kWh/person/month. Usage at or below "
                f"the benchmark scores 100; usage at double the benchmark scores 0."
            )

    # ---------- 7. TNB bill breakdown ----------
    st.markdown("#### Estimated TNB Bill")
    st.markdown(f"""
    <table class="bill-table">
        <tr><td>Energy Charge</td><td class="amt">RM {cost['energy_charge']:.2f}</td></tr>
        <tr><td>Capacity Charge</td><td class="amt">RM {cost['capacity_charge']:.2f}</td></tr>
        <tr><td>Network Charge</td><td class="amt">RM {cost['network_charge']:.2f}</td></tr>
        <tr><td>Retail Charge</td><td class="amt">RM {cost['retail_charge']:.2f}</td></tr>
        <tr><td>Rebate</td><td class="amt">-RM {cost['rebate_amount']:.2f}</td></tr>
        <tr class="total"><td>Estimated Total</td><td class="amt">RM {cost['total_cost_rm']:.2f}</td></tr>
    </table>
    <div class="bill-note">Estimated based on the tariff assumptions used by this application
    (TNB Domestic Tariff, effective 1 July 2025). Actual TNB bills may vary. This is not an
    official TNB document.</div>
    """, unsafe_allow_html=True)

    # ---------- 8 & 9. Report summary / glance ----------
    st.markdown("#### At a Glance")
    st.markdown(f"""
    <div class="glance-card">
        <div class="glance-row"><span class="l">Monthly usage</span><span class="v">{total_kwh:.1f} kWh</span></div>
        <div class="glance-row"><span class="l">Estimated electricity cost</span><span class="v">RM {cost['total_cost_rm']:.2f}</span></div>
        <div class="glance-row"><span class="l">Carbon footprint</span><span class="v">{co2:.1f} kg CO2</span></div>
        <div class="glance-row"><span class="l">Largest energy consumer</span><span class="v">{APPLIANCE_META[top["name"]]["icon"]} {top["name"]}</span></div>
    </div>
    <p style="font-size:0.85rem; color:#52796f; margin-top:0.8rem;">
        <b>What should you focus on?</b> Start with your highest-consuming appliances.
        Small reductions in high-usage devices have a larger impact than the same effort
        applied to low-consumption devices.
    </p>
    """, unsafe_allow_html=True)

    # ---------- 10. Download ----------
    household = {
        "Occupants": occupants,
        "Home Type": st.session_state.get("home_type", ""),
        "Reported Avg. Monthly Bill (RM)": st.session_state.get("avg_bill", 0),
    }
    csv_bytes = build_csv_report(household, breakdown, cost, co2, score)
    st.download_button(
        "⬇ Download Energy Report (CSV)", data=csv_bytes,
        file_name="energismart_energy_report.csv", mime="text/csv",
        use_container_width=True,
    )

    st.write("")
    if st.button("← Back to Appliances", type="secondary"):
        go_to("appliances")
        st.rerun()

# =================================================================
# FOOTER
# =================================================================
st.markdown("""
<div class="app-footer">EnergiSmart · Built for Malaysian households</div>
""", unsafe_allow_html=True)
