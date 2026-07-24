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
# SESSION STATE (16개 챔버 교체일 및 클릭/선택 상태 관리)
# ----------------------------------------------------------------------------
equip_list = [f"M45-{i:02d}" for i in range(1, 17)]

if "swap_dates" not in st.session_state:
    # 16개 설비 기본 세팅 (변경점 여러 개 테스트용 히스토리 포함)
    default_dates = {
        "M45-01": [date(2026, 5, 20), date(2026, 6, 18)],  # 교체 2회 이력
        "M45-02": [date(2026, 6, 25)],
        "M45-03": [date(2026, 7, 2)],
        "M45-04": [],  # 미교체
        "M45-05": [date(2026, 6, 30)],
    }
    for eq in equip_list:
        if eq not in default_dates:
            default_dates[eq] = [date(2026, 6, 20)]
    st.session_state.swap_dates = default_dates

if "selected_equipment" not in st.session_state:
    st.session_state.selected_equipment = "전체"

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="logo-title">◆ Metal45</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">TCR 효과 대시보드</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="side-h">1. 설비 및 교체일 INPUT ⓘ</div>', unsafe_allow_html=True)
    st.caption("설비 선택")
    
    # 드롭다운 선택 (session_state 연동)
    options = ["전체"] + equip_list
    current_idx = options.index(st.session_state.selected_equipment) if st.session_state.selected_equipment in options else 0
    equipment = st.selectbox("설비 선택", options, index=current_idx, key="sb_equipment", label_visibility="collapsed")
    st.session_state.selected_equipment = equipment

    st.caption("TCR A급 교체일 추가/변경")
    cur_history = st.session_state.swap_dates.get(equipment, [date(2026, 6, 18)]) if equipment != "전체" else [date(2026, 6, 18)]
    latest_val = cur_history[-1] if len(cur_history) > 0 else date(2026, 6, 18)
    
    swap_date = st.date_input("TCR A급 교체일", value=latest_val, label_visibility="collapsed")
    
    if st.button("저장", use_container_width=True):
        if equipment != "전체":
            if swap_date not in st.session_state.swap_dates[equipment]:
                st.session_state.swap_dates[equipment].append(swap_date)
                st.session_state.swap_dates[equipment].sort()
            st.success(f"{equipment} 교체일 업데이트 완료!")
            st.rerun()
        else:
            st.warning("특정 설비를 선택한 후 저장해주세요.")

    st.markdown('<div class="side-h">전체 설비 교체일 관리</div>', unsafe_allow_html=True)
    
    equip_table_data = []
    for eq in equip_list:
        dts = st.session_state.swap_dates[eq]
        dt_str = ", ".join([d.strftime("%Y-%m-%d") for d in dts]) if dts else "- (미교체)"
        equip_table_data.append({"설비": eq, "교체일 이력": dt_str})
    equip_table = pd.DataFrame(equip_table_data)
    st.dataframe(equip_table, hide_index=True, use_container_width=True, height=200)

    st.markdown("<hr>", unsafe_allow_html=True)
    nav_items = ["📊 대시보드", "🔍 설비별 상세분석", "📈 전체 설비 비교",
                 "🕒 이벤트 히스토리", "🔔 알람 리스트", "🗂 데이터 테이블", "⚙️ 설정"]
    for i, item in enumerate(nav_items):
        cls = "nav-btn active" if i == 0 else "nav-btn"
        st.markdown(f'<div class="{cls}">{item}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# HEADER & DATE RANGE FILTER
# ----------------------------------------------------------------------------
h_left, h_right = st.columns([3, 1.4])
with h_left:
    st.markdown('<div class="main-title">TCR 교체 효과 대시보드 ⓘ</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-sub">※ 각 설비별 TCR A급 교체일을 기준으로 전후 효과를 분석합니다.</div>',
                unsafe_allow_html=True)
with h_right:
    # 3번 기능 지원용 날짜 범위 지정
    date_range = st.date_input("조회 기간 설정", value=(date(2026, 5, 15), date(2026, 7, 10)), label_visibility="visible")
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = date(2026, 5, 15), date(2026, 7, 10)

# ----------------------------------------------------------------------------
# SYNTHETIC DATA GENERATION
# ----------------------------------------------------------------------------
days = np.arange(-14, 15)  # Relative Day (-14 ~ +14)
rng = np.random.default_rng(42)

# 1) Relative Day 기준 데이터
data_dict = {}
for eq in equip_list:
    delay_before = np.clip(90 + rng.normal(0, 15, 14), 60, 140)
    delay_after = np.clip(8 + rng.normal(0, 3, 15), 0, 20)
    delay_series = np.concatenate([delay_before, delay_after])
    wpd_series = rng.integers(150, 290, size=29)
    wpd_series[rng.choice(29, 2)] = 0
    
    data_dict[eq] = pd.DataFrame({"day": days, "delay": delay_series, "wpd": wpd_series})

# 전체 평균 (Relative Day)
avg_delay = np.mean([df["delay"].values for df in data_dict.values()], axis=0)
avg_wpd = np.mean([df["wpd"].values for df in data_dict.values()], axis=0)
df_all_rel = pd.DataFrame({"day": days, "delay": avg_delay, "wpd": avg_wpd})

# 2) 실제 날짜(Absolute Date Range) 기준 데이터 생성 (3번 기능용)
full_dates = pd.date_range(start_date, end_date, freq="D").date
date_data_dict = {}

for eq in equip_list:
    n_days = len(full_dates)
    dts_list = st.session_state.swap_dates[eq]
    
    # 기본 baseline 생성
    base_delay = np.clip(100 + rng.normal(0, 12, n_days), 50, 150)
    
    # 교체일 이후 구간 시계열 효과 반영
    for dt in dts_list:
        after_mask = np.array([d >= dt for d in full_dates])
        base_delay[after_mask] = np.clip(8 + rng.normal(0, 3, np.sum(after_mask)), 0, 25)
        
    wpd_vals = rng.integers(160, 295, size=n_days)
    date_data_dict[eq] = pd.DataFrame({"date": full_dates, "delay": base_delay, "wpd": wpd_vals})

# 전체 평균 (Absolute Date)
avg_date_delay = np.mean([df["delay"].values for df in date_data_dict.values()], axis=0)
avg_date_wpd = np.mean([df["wpd"].values for df in date_data_dict.values()], axis=0)
df_all_date = pd.DataFrame({"date": full_dates, "delay": avg_date_delay, "wpd": avg_date_wpd})

# 현재 선택 설비 참조
equipment = st.session_state.selected_equipment
if equipment == "전체":
    df_current_rel = df_all_rel
    df_current_date = df_all_date
    current_swap_str = "전체 설비 평균"
    cur_swap_dates = []
else:
    df_current_rel = data_dict[equipment]
    df_current_date = date_data_dict[equipment]
    cur_swap_dates = st.session_state.swap_dates[equipment]
    current_swap_str = ", ".join([d.strftime("%Y-%m-%d") for d in cur_swap_dates]) if cur_swap_dates else "미교체"

# ----------------------------------------------------------------------------
# 1번 기능: 설비별 개선 효과 비교 (전체 항목 포함) DataFrame 생성
# ----------------------------------------------------------------------------
compare_list = []

# '전체' 행 우선 추가
all_before = df_all_rel[df_all_rel["day"] < 0]["delay"].mean()
all_after = df_all_rel[df_all_rel["day"] >= 0]["delay"].mean()
all_diff_pct = round(((all_before - all_after) / all_before) * 100) if all_before > 0 else 0

compare_list.append({
    "설비": "전체",
    "교체일": "전체 평균",
    "교체 전 (min/day)": int(round(all_before)),
    "교체 후 (min/day)": int(round(all_after)),
    "감소율 (%)": all_diff_pct
})

# 각 설비별 행 추가
for eq in equip_list:
    d = data_dict[eq]
    before_val = d[d["day"] < 0]["delay"].mean()
    after_val = d[d["day"] >= 0]["delay"].mean()
    dts = st.session_state.swap_dates[eq]
    dt_str = ", ".join([d.strftime("%m-%d") for d in dts]) if dts else "미교체"
    
    diff_pct = round(((before_val - after_val) / before_val) * 100) if before_val > 0 else 0
    compare_list.append({
        "설비": eq,
        "교체일": dt_str,
        "교체 전 (min/day)": int(round(before_val)),
        "교체 후 (min/day)": int(round(after_val)),
        "감소율 (%)": diff_pct
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
# CHART ROW 1 (2번 차트 & 2번 기능: 행 클릭 시 차트 반응)
# ----------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">2. Swap Delay Trend & WPD (교체일 기준 정렬) ⓘ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-sub">선택 설비 : <b style="color:#2352d9;">{equipment}</b> &nbsp;&nbsp; 교체일 이력 : <b>{current_swap_str}</b></div>',
                unsafe_allow_html=True)
    
    ref_dt = cur_swap_dates[-1] if len(cur_swap_dates) > 0 else date(2026, 6, 18)
    date_labels = [(ref_dt + timedelta(days=int(d))).strftime("%m-%d") for d in df_current_rel["day"]]

    fig2 = go.Figure()

    # WPD 막대 (0~300)
    fig2.add_trace(go.Bar(
        x=df_current_rel["day"], y=df_current_rel["wpd"],
        name="WPD (0~300)", marker_color="rgba(148, 163, 184, 0.4)", xaxis="x"
    ))

    # Swap Delay 라인
    fig2.add_trace(go.Scatter(
        x=date_labels, y=df_current_rel["delay"],
        mode="lines+markers", name="Delay Time (min/day)",
        line=dict(color="#3b82f6", width=2.5), marker=dict(size=5), xaxis="x2"
    ))

    # 기준선 (교체일)
    fig2.add_vline(x=0, line_width=1.6, line_dash="dash", line_color="#e11d48")
    fig2.add_annotation(x=0, y=1.05, yref="paper", showarrow=False,
                        text="TCR A급 교체", font=dict(color="#e11d48", size=11, family="Arial Black"))

    fig2.update_layout(
        height=360, margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(title="수치 (min / WPD)", showgrid=True, gridcolor="#f0f1f5", zeroline=False),
        xaxis=dict(title="Relative Day (Day)", side="bottom", showgrid=False, zeroline=False),
        xaxis2=dict(title="Date (MM-DD)", side="top", overlaying="x", showgrid=False, zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.18, xanchor="right", x=1, font=dict(size=11)),
        font=dict(size=11, color="#41476b"), barmode="overlay"
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# 2번 기능 반영: st.dataframe 클릭 이벤트로 설비 변경
with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">설비별 개선 효과 비교 (클릭 시 해당 설비로 차트 변경) ⓘ</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">※ 아래 표에서 원하는 설비 행을 클릭해 보세요.</div>', unsafe_allow_html=True)

    # 클릭 가능 인터랙티브 데이터프레임
    selection = st.dataframe(
        compare_df,
        hide_index=True,
        use_container_width=True,
        height=335,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "감소율 (%)": st.column_config.ProgressColumn(
                "감소율 (%)",
                format="%d%%",
                min_value=0,
                max_value=100,
            )
        }
    )

    # 행 클릭 감지 및 반영
    if len(selection.selection["rows"]) > 0:
        selected_row_idx = selection.selection["rows"][0]
        clicked_equipment = compare_df.iloc[selected_row_idx]["설비"]
        
        if clicked_equipment != st.session_state.selected_equipment:
            st.session_state.selected_equipment = clicked_equipment
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# CHART ROW 2 (3번 기능: 날짜 지정 시계열 차트 & 다중 교체일 변경점 세로선)
# ----------------------------------------------------------------------------
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown(f'<div class="chart-title">3. 날짜 지정 시계열 Swap Delay Trend & WPD (기간: {start_date} ~ {end_date}) ⓘ</div>', unsafe_allow_html=True)
st.markdown(f'<div class="chart-sub">선택 설비 : <b style="color:#2352d9;">{equipment}</b> &nbsp;&nbsp;| &nbsp;&nbsp; 변경점(교체일) 세로선 표시 적용</div>', unsafe_allow_html=True)

fig3 = go.Figure()

# 1) WPD 막대 (0~300)
fig3.add_trace(go.Bar(
    x=df_current_date["date"],
    y=df_current_date["wpd"],
    name="WPD (0~300)",
    marker_color="rgba(148, 163, 184, 0.35)",
    yaxis="y"
))

# 2) Swap Delay 라인
fig3.add_trace(go.Scatter(
    x=df_current_date["date"],
    y=df_current_date["delay"],
    mode="lines+markers",
    name="Delay Time (min/day)",
    line=dict(color="#2563eb", width=2),
    marker=dict(size=4),
    yaxis="y"
))

# 3) 다중 교체일 세로선(Vertical Lines) 추가 (변경점 날짜가 여러 개일 때 대응)
if equipment == "전체":
    # 전체 선택 시 모든 설비의 교체일 표시
    all_dates = set()
    for d_list in st.session_state.swap_dates.values():
        all_dates.update(d_list)
    target_vline_dates = sorted(list(all_dates))
else:
    target_vline_dates = cur_swap_dates

for idx, v_date in enumerate(target_vline_dates):
    if start_date <= v_date <= end_date:
        fig3.add_vline(
            x=v_date,
            line_width=1.8,
            line_dash="dash",
            line_color="#e11d48"
        )
        fig3.add_annotation(
            x=v_date,
            y=1.05,
            yref="paper",
            showarrow=False,
            text=f"교체일 ({v_date.strftime('%m-%d')})",
            font=dict(color="#e11d48", size=10, family="Arial Black")
        )

fig3.update_layout(
    height=360,
    margin=dict(l=10, r=10, t=40, b=10),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        title="Date (YYYY-MM-DD)",
        showgrid=True,
        gridcolor="#f0f1f5",
        type="date"
    ),
    yaxis=dict(
        title="수치 (min / WPD)",
        showgrid=True,
        gridcolor="#f0f1f5",
        zeroline=False
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.12, xanchor="right", x=1, font=dict(size=11)),
    font=dict(size=11, color="#41476b"),
    barmode="overlay"
)

st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)
