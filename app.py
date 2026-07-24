import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

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
# STYLE
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
        background:#ffffff; border-radius:14px; padding: 14px 18px 14px 18px;
        border: 1px solid #eef0f6; box-shadow: 0 1px 4px rgba(20,33,61,0.06); margin-bottom: 18px;
    }
    .chart-title {font-size:15px; font-weight:800; color:#1c2745; margin-bottom:0px;}
    .chart-sub {font-size:11.5px; color:#8891a8; margin-bottom:6px;}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SESSION STATE (1. 16개 챔버 기본 교체일 및 교체일 업데이트 저장)
# ----------------------------------------------------------------------------
equip_list = [f"M45-{i:02d}" for i in range(1, 17)]

if "swap_dates" not in st.session_state:
    # 16개 설비 기본 세팅
    default_dates = {
        "M45-01": date(2026, 6, 18),
        "M45-02": date(2026, 6, 25),
        "M45-03": date(2026, 7, 2),
        "M45-04": None, # 미교체
        "M45-05": date(2026, 6, 30),
    }
    for eq in equip_list:
        if eq not in default_dates:
            default_dates[eq] = date(2026, 6, 20)
    st.session_state.swap_dates = default_dates

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="logo-title">◆ Metal45</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">TCR 효과 대시보드</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="side-h">1. 설비 및 교체일 INPUT ⓘ</div>', unsafe_allow_html=True)
    st.caption("설비 선택")
    
    # "전체" 옵션 포함
    equipment = st.selectbox("설비 선택", ["전체"] + equip_list, label_visibility="collapsed")
    
    st.caption("TCR A급 교체일")
    selected_swap_val = st.session_state.swap_dates.get(equipment, date(2026, 6, 18)) if equipment != "전체" else date(2026, 6, 18)
    if selected_swap_val is None:
        selected_swap_val = date(2026, 6, 18)
        
    swap_date = st.date_input("TCR A급 교체일", value=selected_swap_val, label_visibility="collapsed")
    
    # 5. 저장 버튼 누를 시 session_state 교체일 및 Table 반영
    if st.button("저장", use_container_width=True):
        if equipment != "전체":
            st.session_state.swap_dates[equipment] = swap_date
            st.success(f"{equipment} 교체일 변경 완료!")
        else:
            st.warning("특정 설비를 선택한 후 저장해주세요.")

    st.markdown('<div class="side-h">전체 설비 교체일 관리</div>', unsafe_allow_html=True)
    
    # 동적 테이블 생성
    equip_table_data = []
    for eq in equip_list:
        dt = st.session_state.swap_dates[eq]
        equip_table_data.append({
            "설비": eq,
            "교체일": dt.strftime("%Y-%m-%d") if dt else "- (미교체)"
        })
    equip_table = pd.DataFrame(equip_table_data)
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
# SYNTHETIC DATA GENERATION (2. WPD 및 설비별 데이터)
# ----------------------------------------------------------------------------
days = np.arange(-14, 15)  # -14 ~ +14 (29일)
rng = np.random.default_rng(42)

# 설비별 일자별 데이터 생성
data_dict = {}
for eq in equip_list:
    delay_before = np.clip(90 + rng.normal(0, 15, 14), 60, 140)
    delay_after = np.clip(8 + rng.normal(0, 3, 15), 0, 20)
    delay_series = np.concatenate([delay_before, delay_after])
    
    # 2. WPD 값 추가 (0 ~ 300)
    wpd_series = rng.integers(150, 290, size=29)
    # 가끔 WPD가 낮은 날 또는 0인 날
    wpd_series[rng.choice(29, 2)] = 0
    
    data_dict[eq] = pd.DataFrame({
        "day": days,
        "delay": delay_series,
        "wpd": wpd_series
    })

# 6. "전체" 선택 시 평균 데이터 생성
avg_delay = np.mean([df["delay"].values for df in data_dict.values()], axis=0)
avg_wpd = np.mean([df["wpd"].values for df in data_dict.values()], axis=0)
df_all = pd.DataFrame({"day": days, "delay": avg_delay, "wpd": avg_wpd})

# 현재 선택된 설비 데이터
if equipment == "전체":
    df_current = df_all
    current_swap_str = "전체 설비 평균 기준"
else:
    df_current = data_dict[equipment]
    cur_dt = st.session_state.swap_dates[equipment]
    current_swap_str = cur_dt.strftime("%Y-%m-%d") if cur_dt else "미교체"

# 설비별 비교 요약 데이터
compare_list = []
for eq in equip_list:
    d = data_dict[eq]
    before_val = d[d["day"] < 0]["delay"].mean()
    after_val = d[d["day"] >= 0]["delay"].mean()
    dt = st.session_state.swap_dates[eq]
    dt_str = dt.strftime("%Y-%m-%d") if dt else "- (미교체)"
    
    diff_pct = round(((before_val - after_val) / before_val) * 100) if before_val > 0 else 0
    compare_list.append({
        "설비": eq,
        "교체일": dt_str,
        "교체 전 (min/day)": int(round(before_val)),
        "교체 후 (min/day)": int(round(after_val)),
        "감소율": diff_pct
    })
compare_df = pd.DataFrame(compare_list)

# ----------------------------------------------------------------------------
# KPI CARDS
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
# MAIN CHARTS ROW (2번 / 4번 반영)
# ----------------------------------------------------------------------------
c1, c2 = st.columns(2)

# 2번 개발: 같은 y축을 공유하는 2개 x축 (아래: WPD 막대, 위: Relative Day 라인)
with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">2. Swap Delay Trend & WPD ⓘ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-sub">선택 설비 : <b>{equipment}</b> &nbsp;&nbsp; 교체일 : <b>{current_swap_str}</b></div>',
                unsafe_allow_html=True)
    
    # X축 상단용 Date 생성 (기준일로부터 상대 일자 계산)
    ref_date = swap_date if (equipment != "전체" and st.session_state.swap_dates[equipment] is not None) else date(2026, 6, 18)
    date_labels = [(ref_date + timedelta(days=int(d))).strftime("%m-%d") for d in df_current["day"]]

    fig = go.Figure()

    # 1) 아래 X축: WPD 막대 그래프 (0~300)
    fig.add_trace(go.Bar(
        x=df_current["day"],
        y=df_current["wpd"],
        name="WPD (0~300)",
        marker_color="rgba(148, 163, 184, 0.4)",
        xaxis="x",
    ))

    # 2) 위 X축: Swap Delay 라인 그래프
    fig.add_trace(go.Scatter(
        x=date_labels,
        y=df_current["delay"],
        mode="lines+markers",
        name="Delay Time (min/day)",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=5),
        xaxis="x2"
    ))

    # 기준선 (교체일)
    fig.add_vline(x=0, line_width=1.6, line_dash="dash", line_color="#e11d48")
    fig.add_annotation(x=0, y=1.05, yref="paper", showarrow=False,
                       text="TCR A급 교체", font=dict(color="#e11d48", size=11, family="Arial Black"))

    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(title="수치 (min / WPD)", showgrid=True, gridcolor="#f0f1f5", zeroline=False),
        
        # X축 1 (아래축: Relative Day)
        xaxis=dict(
            title="Relative Day (Day)",
            side="bottom",
            showgrid=False,
            zeroline=False
        ),
        # X축 2 (위축: 일자 날짜)
        xaxis2=dict(
            title="Date (MM-DD)",
            side="top",
            overlaying="x",
            showgrid=False,
            zeroline=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.18, xanchor="right", x=1, font=dict(size=11)),
        font=dict(size=11, color="#41476b"),
        barmode="overlay"
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# 4번 반영: 3번 차트 위치에 6번 감소율 표 이동
with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">설비별 개선 효과 비교 (Delay Time 감소율) ⓘ</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">전체 챔버(16개) 교체 전/후 개선 현황</div>', unsafe_allow_html=True)

    def render_bar(pct):
        pct = max(pct, 0)
        color = "#22c55e" if pct >= 50 else "#ef4444"
        width = min(pct, 100)
        return f"""<div style="background:#eef0f6;border-radius:6px;height:12px;width:100%;">
        <div style="background:{color};height:12px;border-radius:6px;width:{width}%;"></div></div>"""

    # 테이블 헤더
    header_cols = st.columns([1, 1.2, 1, 1, 1, 1.4])
    headers = ["설비", "교체일", "교체 전\n(min)", "교체 후\n(min)", "감소율", "개선 효과"]
    for hcol, htxt in zip(header_cols, headers):
        hcol.markdown(f"<div style='font-size:11.5px;color:#8891a8;font-weight:700;'>{htxt}</div>", unsafe_allow_html=True)

    # Scroll 영역
    with st.container(height=320):
        for _, row in compare_df.iterrows():
            rc = st.columns([1, 1.2, 1, 1, 1, 1.4])
            rc[0].markdown(f"<div style='font-size:12px;font-weight:700;'>{row['설비']}</div>", unsafe_allow_html=True)
            rc[1].markdown(f"<div style='font-size:12px;'>{row['교체일']}</div>", unsafe_allow_html=True)
            rc[2].markdown(f"<div style='font-size:12px;'>{row['교체 전 (min/day)']}</div>", unsafe_allow_html=True)
            rc[3].markdown(f"<div style='font-size:12px;'>{row['교체 후 (min/day)']}</div>", unsafe_allow_html=True)
            color = "#16a34a" if row["감소율"] >= 50 else "#ef4444"
            rc[4].markdown(f"<div style='font-size:12px;color:{color};font-weight:700;'>▼{row['감소율']}%</div>", unsafe_allow_html=True)
            rc[5].markdown(render_bar(row["감소율"]), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
