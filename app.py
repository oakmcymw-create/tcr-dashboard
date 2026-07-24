import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Metal45 | TCR 효과 대시보드",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# STYLE (다크 네이비 사이드바 + 화이트 메인, 레퍼런스 톤 매칭)
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: -apple-system, 'Segoe UI', 'Malgun Gothic', sans-serif;
    }
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #12224a;
        min-width: 300px;
    }
    section[data-testid="stSidebar"] * { color: #e6ebf5 !important; }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] input {
        background-color: #1b2f5e !important;
        color: #ffffff !important;
        border: 1px solid #2c4172 !important;
    }
    section[data-testid="stSidebar"] hr { border-color: #26386a; }

    .logo-title {font-size: 22px; font-weight: 800; color: #ffffff !important; margin-bottom: 0;}
    .logo-sub {font-size: 12.5px; color: #8ea0c9 !important; margin-top: -6px;}

    .side-h {font-size: 13.5px; font-weight: 700; color: #cfd9ef !important;
             margin-top: 18px; margin-bottom: 6px; letter-spacing: .2px;}

    .nav-btn {
        display:block; padding: 9px 12px; border-radius: 8px; margin-bottom: 4px;
        font-size: 14px; color: #c7d1ea !important;
    }
    .nav-btn.active {background-color: #2352d9; color: #ffffff !important; font-weight: 600;}

    .info-box {
        background-color: #1b2f5e; border-radius: 10px; padding: 12px 14px;
        font-size: 12px; line-height: 1.9; color: #b9c5e6 !important; margin-top: 10px;
    }

    /* Main title */
    .main-title {font-size: 28px; font-weight: 800; color: #14213d; margin-bottom: 0px;}
    .main-sub {font-size: 13px; color: #6b7794; margin-top: 2px; margin-bottom: 18px;}

    /* KPI cards */
    .kpi-card {
        border-radius: 14px; padding: 18px 20px; height: 168px;
        box-shadow: 0 1px 4px rgba(20,33,61,0.08); border: 1px solid #eef0f6;
    }
    .kpi-title {font-size: 14px; font-weight: 700; text-align:center; color:#2a3455; margin-bottom: 10px;}
    .kpi-icon {font-size: 26px;}
    .kpi-row {display:flex; justify-content:space-around; align-items:center; margin-top:6px;}
    .kpi-label {font-size: 11.5px; color:#8891a8; text-align:center;}
    .kpi-value {font-size: 24px; font-weight: 800; color:#1c2745; text-align:center;}
    .kpi-arrow {font-size:20px; color:#9aa4bf;}
    .kpi-foot {text-align:center; font-size:13px; font-weight:700; margin-top:10px;}
    .kpi-big {font-size:34px; font-weight:800; text-align:center;}
    .kpi-footnote {font-size:10.5px; color:#a3adc4; text-align:center; margin-top:6px;}

    .card-blue {background: linear-gradient(180deg,#eaf1ff 0%, #ffffff 55%);}
    .card-green {background: linear-gradient(180deg,#eafaf1 0%, #ffffff 55%);}
    .card-orange {background: linear-gradient(180deg,#fff6e6 0%, #ffffff 55%);}
    .card-purple {background: linear-gradient(180deg,#f3ecfb 0%, #ffffff 55%);}

    .chart-card {
        background:#ffffff; border-radius:14px; padding: 14px 18px 6px 18px;
        border: 1px solid #eef0f6; box-shadow: 0 1px 4px rgba(20,33,61,0.06); margin-bottom: 18px;
    }
    .chart-title {font-size:15px; font-weight:800; color:#1c2745; margin-bottom:0px;}
    .chart-sub {font-size:11.5px; color:#8891a8; margin-bottom:6px;}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="logo-title">◆ Metal45</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">TCR 효과 대시보드</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="side-h">1. 설비 및 교체일 INPUT ⓘ</div>', unsafe_allow_html=True)
    st.caption("설비 선택")
    equipment = st.selectbox("설비 선택", ["M45-01", "M45-02", "M45-03", "M45-04", "M45-05"],
                              label_visibility="collapsed")
    st.caption("TCR A급 교체일")
    swap_date = st.date_input("TCR A급 교체일", value=date(2026, 6, 18), label_visibility="collapsed")
    st.button("저장", use_container_width=True)

    st.markdown('<div class="side-h">전체 설비 교체일 관리</div>', unsafe_allow_html=True)
    equip_table = pd.DataFrame({
        "설비": ["M45-01", "M45-02", "M45-03", "M45-04", "M45-05"],
        "교체일": ["2026-06-18", "2026-06-25", "2026-07-02", "-  (미교체)", "2026-06-30"],
    })
    st.dataframe(equip_table, hide_index=True, use_container_width=True, height=210)

    st.markdown("<hr>", unsafe_allow_html=True)
    nav_items = ["📊 대시보드", "🔍 설비별 상세분석", "📈 전체 설비 비교",
                 "🕒 이벤트 히스토리", "🔔 알람 리스트", "🗂 데이터 테이블", "⚙️ 설정"]
    for i, item in enumerate(nav_items):
        cls = "nav-btn active" if i == 0 else "nav-btn"
        st.markdown(f'<div class="{cls}">{item}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <b>분석 기준</b><br>
        • 교체 전/후 : 전후 14일 기준<br>
        • 지표 : 1일 평균 기준<br>
        • WPD 0인 날은 평균 계산에서 제외<br>
        • 시간 단위 : 분 (min)
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
h_left, h_right = st.columns([3, 1.3])
with h_left:
    st.markdown('<div class="main-title">TCR 교체 효과 대시보드 ⓘ</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">※ 각 설비별 TCR A급 교체일을 기준으로 전후 효과를 분석합니다.</div>',
                unsafe_allow_html=True)
with h_right:
    st.date_input("기간", value=(date(2026, 5, 18), date(2026, 7, 3)), label_visibility="collapsed")

# ----------------------------------------------------------------------------
# SYNTHETIC DATA (레퍼런스 수치에 맞춘 더미 데이터)
# ----------------------------------------------------------------------------
days = np.arange(-14, 15)

rng = np.random.default_rng(42)
delay_before = 104 + rng.normal(0, 12, size=15).cumsum() * 0 + rng.normal(100, 15, 15)
delay_before = np.clip(90 + rng.normal(0, 15, 15), 60, 140)
delay_after = np.clip(8 + rng.normal(0, 3, 15), 0, 20)
delay_series = np.concatenate([delay_before, delay_after])

alarm_before = np.clip(rng.normal(28, 6, 15), 15, 45)
alarm_after = np.clip(rng.normal(2, 1.2, 15), 0, 6)
alarm_series = np.concatenate([alarm_before, alarm_after])

# 전체 설비 평균 효과 (교체일 기준 정렬)
avg_before = np.clip(np.linspace(140, 90, 15) + rng.normal(0, 6, 15), 60, 150)
avg_after = np.clip(np.linspace(70, 8, 15) + rng.normal(0, 4, 15), 0, 80)
avg_series = np.concatenate([avg_before, avg_after])

df_trend = pd.DataFrame({"day": days, "delay": delay_series, "alarm": alarm_series, "avg": avg_series})

compare_df = pd.DataFrame({
    "설비": ["M45-02", "M45-01", "M45-03", "M45-05", "M45-04"],
    "교체일": ["2026-06-25", "2026-06-18", "2026-07-02", "2026-06-30", "-  (미교체)"],
    "교체 전 (min/day)": [110, 120, 98, 65, 75],
    "교체 후 (min/day)": [5, 8, 14, 12, 68],
})
compare_df["감소율"] = ((compare_df["교체 전 (min/day)"] - compare_df["교체 후 (min/day)"])
                       / compare_df["교체 전 (min/day)"] * 100).round(0).astype(int)

# ----------------------------------------------------------------------------
# KPI CARDS (4개)
# ----------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card card-blue">
        <div class="kpi-title">🔔 Upper Chamber Temp Alarm (건수/일)</div>
        <div class="kpi-row">
            <div><div class="kpi-label">교체 전<br>(-14 ~ -1일)</div><div class="kpi-value">37건/일</div></div>
            <div class="kpi-arrow">➜</div>
            <div><div class="kpi-label">교체 후<br>(+1 ~ +14일)</div><div class="kpi-value">1건/일</div></div>
        </div>
        <div class="kpi-foot" style="color:#2563eb;">▼ 97% 감소</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card card-green">
        <div class="kpi-title">🕒 생산 Loss (Swap Delay Time, min/day)</div>
        <div class="kpi-row">
            <div><div class="kpi-label">교체 전<br>(-14 ~ -1일)</div><div class="kpi-value">120<br><span style="font-size:11px;font-weight:400;">min/day</span></div></div>
            <div class="kpi-arrow">➜</div>
            <div><div class="kpi-label">교체 후<br>(+1 ~ +14일)</div><div class="kpi-value">8<br><span style="font-size:11px;font-weight:400;">min/day</span></div></div>
        </div>
        <div class="kpi-foot" style="color:#16a34a;">▼ 112 min/day (▼93%)</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card card-orange">
        <div class="kpi-title">🌐 예상 생산성 증가</div>
        <div class="kpi-big" style="color:#f59e0b;">+95</div>
        <div class="kpi-label" style="font-size:13px;">wafers/day</div>
        <div class="kpi-footnote">* 평균 Wafer Time 1.26 min/ea 기준</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card card-purple">
        <div class="kpi-title">💰 재무성과 (예상)</div>
        <div class="kpi-big" style="color:#7c3aed;">+2,470</div>
        <div class="kpi-label" style="font-size:13px;">만원/일</div>
        <div class="kpi-footnote">* Wafer Margin 26만원/장 기준</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# HELPER: 교체 기준선 있는 라인 차트
# ----------------------------------------------------------------------------
def line_chart(x, y, name, color, unit=""):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers", name=name,
        line=dict(color=color, width=2), marker=dict(size=4),
        fill="tozeroy", fillcolor=color.replace("rgb", "rgba").replace(")", ",0.08)") if "rgb" in color else None,
    ))
    fig.add_vline(x=0, line_width=1.6, line_dash="dash", line_color="#e11d48")
    fig.add_annotation(x=0, y=1.08, yref="paper", showarrow=False,
                        text="TCR A급 교체", font=dict(color="#e11d48", size=12, family="Arial Black"))
    fig.update_layout(
        height=260, margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(title="(Day)", showgrid=False, zeroline=False),
        yaxis=dict(title=f"({unit})", showgrid=True, gridcolor="#f0f1f5", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1, font=dict(size=11)),
        font=dict(size=11, color="#41476b"),
    )
    return fig

# ----------------------------------------------------------------------------
# CHART ROW 1 : 2. Swap Delay Time Trend / 3. Temp Alarm Count Trend
# ----------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">2. Swap Delay Time Trend (min/day) ⓘ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-sub">선택 설비 : {equipment} &nbsp;&nbsp; 교체일 : {swap_date}</div>',
                unsafe_allow_html=True)
    fig = line_chart(df_trend["day"], df_trend["delay"], "Delay Time (min/day)", "#3b82f6", unit="min")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">3. Temp Alarm Count Trend (건/일) ⓘ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-sub">선택 설비 : {equipment} &nbsp;&nbsp; 교체일 : {swap_date}</div>',
                unsafe_allow_html=True)
    fig = line_chart(df_trend["day"], df_trend["alarm"], "Alarm Count (건/일)", "#8b5cf6", unit="건")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# CHART ROW 2 : 5. 전체 설비 평균 효과 / 6. 설비별 개선 효과 비교
# ----------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">5. 전체 설비 평균 효과 (교체일 기준 정렬)</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">모든 설비의 교체일을 기준으로 정렬 후 평균</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_trend["day"], y=df_trend["avg"], mode="lines+markers", name="Avg Delay Time",
        line=dict(color="#3b82f6", width=2), marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
    ))
    fig.add_vline(x=0, line_width=1.6, line_dash="dash", line_color="#e11d48")
    fig.add_annotation(x=0, y=1.08, yref="paper", showarrow=False,
                        text="TCR A급 교체 (평균)", font=dict(color="#e11d48", size=12, family="Arial Black"))
    fig.update_layout(
        height=260, margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(title="(Day)", showgrid=False, zeroline=False),
        yaxis=dict(title="(min)", showgrid=True, gridcolor="#f0f1f5", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1, font=dict(size=11)),
        font=dict(size=11, color="#41476b"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">6. 설비별 개선 효과 비교 (Delay Time 감소율) ⓘ</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">&nbsp;</div>', unsafe_allow_html=True)

    def render_bar(pct):
        pct = max(pct, 0)
        color = "#22c55e" if pct >= 50 else "#ef4444"
        width = min(pct, 100)
        return f"""<div style="background:#eef0f6;border-radius:6px;height:14px;width:100%;">
        <div style="background:{color};height:14px;border-radius:6px;width:{width}%;"></div></div>"""

    header_cols = st.columns([1, 1, 1, 1, 1, 1.4])
    headers = ["설비", "교체일", "교체 전\n(min/day)", "교체 후\n(min/day)", "감소율", "개선 효과"]
    for hcol, htxt in zip(header_cols, headers):
        hcol.markdown(f"<div style='font-size:11.5px;color:#8891a8;font-weight:700;'>{htxt}</div>",
                      unsafe_allow_html=True)

    for _, row in compare_df.iterrows():
        rc = st.columns([1, 1, 1, 1, 1, 1.4])
        rc[0].markdown(f"<div style='font-size:12.5px;font-weight:700;'>{row['설비']}</div>", unsafe_allow_html=True)
        rc[1].markdown(f"<div style='font-size:12.5px;'>{row['교체일']}</div>", unsafe_allow_html=True)
        rc[2].markdown(f"<div style='font-size:12.5px;'>{row['교체 전 (min/day)']}</div>", unsafe_allow_html=True)
        rc[3].markdown(f"<div style='font-size:12.5px;'>{row['교체 후 (min/day)']}</div>", unsafe_allow_html=True)
        color = "#16a34a" if row["감소율"] >= 50 else "#ef4444"
        rc[4].markdown(f"<div style='font-size:12.5px;color:{color};font-weight:700;'>▼{row['감소율']}%</div>",
                       unsafe_allow_html=True)
        rc[5].markdown(render_bar(row["감소율"]), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
