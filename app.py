"""
Metal45 TCR 교체 효과 대시보드
Streamlit + Plotly 구현
실행: streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import date, datetime

# ────────────────────────────────────────────────────────────────────────────
# 0. 기본 설정 & 스타일
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Metal45 TCR 효과 대시보드",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY_BLUE = "#2F5CFF"
PRIMARY_RED = "#E23D3D"
PRIMARY_GREEN = "#1F9D55"
PRIMARY_PURPLE = "#7B4FE0"
PRIMARY_ORANGE = "#F5A623"
CARD_BG = "#FFFFFF"
PAGE_BG = "#F3F5F9"
SIDEBAR_BG = "#161B29"
TEXT_DARK = "#1B1F2A"
TEXT_GRAY = "#8A93A6"

st.markdown(f"""
<style>
    .stApp {{ background-color: {PAGE_BG}; }}
    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
    }}
    section[data-testid="stSidebar"] * {{
        color: #E7E9EE !important;
    }}
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] .stDateInput input {{
        color: #1B1F2A !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: #232838 !important;
    }}
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}
    .kpi-card {{
        background-color: {CARD_BG};
        border-radius: 14px;
        padding: 18px 20px 14px 20px;
        box-shadow: 0 1px 3px rgba(20,20,43,0.08);
        height: 168px;
    }}
    .kpi-title {{
        font-size: 14px;
        font-weight: 700;
        color: {TEXT_DARK};
        margin-bottom: 10px;
    }}
    .kpi-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .kpi-before-after {{
        text-align: center;
    }}
    .kpi-label {{
        font-size: 11px;
        color: {TEXT_GRAY};
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 800;
        color: {TEXT_DARK};
    }}
    .kpi-unit {{
        font-size: 11px;
        color: {TEXT_GRAY};
    }}
    .kpi-delta {{
        margin-top: 8px;
        font-size: 13px;
        font-weight: 700;
        color: {PRIMARY_BLUE};
        text-align: center;
    }}
    .kpi-big {{
        font-size: 30px;
        font-weight: 800;
        text-align: center;
    }}
    .kpi-sub {{
        font-size: 11px;
        color: {TEXT_GRAY};
        text-align: center;
        margin-top: 6px;
    }}
    .panel-card {{
        background-color: {CARD_BG};
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(20,20,43,0.08);
        margin-bottom: 18px;
    }}
    .panel-title {{
        font-size: 15px;
        font-weight: 700;
        color: {TEXT_DARK};
        margin-bottom: 2px;
    }}
    .panel-sub {{
        font-size: 11.5px;
        color: {TEXT_GRAY};
        margin-bottom: 6px;
    }}
    .footnote {{
        font-size: 11px;
        color: {TEXT_GRAY};
        margin-top: 4px;
    }}
    thead tr th {{
        background-color: #F5F6FA !important;
    }}
    div[data-testid="stMetricValue"] {{ font-size: 22px; }}
</style>
""", unsafe_allow_html=True)

DAY_RANGE = list(range(-14, 15))

def switch_marker_layout(fig, x0=0, label="TCR A급 교체", y_top=1.0):
    fig.add_vline(x=x0, line_width=1.6, line_dash="dash", line_color=PRIMARY_RED)
    fig.add_annotation(
        x=x0, y=1.06, xref="x", yref="paper", text=label,
        showarrow=False, font=dict(color=PRIMARY_RED, size=12, family="Arial Black"),
    )
    return fig

def base_layout(fig, y_title="", height=300):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=36, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="left", x=0,
                    font=dict(size=11)),
        font=dict(size=11, color=TEXT_DARK),
        xaxis=dict(title="(Day)", showgrid=False, zeroline=False,
                   tickmode="array", tickvals=list(range(-14, 15, 2))),
        yaxis=dict(title=y_title, showgrid=True, gridcolor="#EEF0F5", zeroline=False),
    )
    return fig

# ────────────────────────────────────────────────────────────────────────────
# 1. 합성 데이터 생성 (교체일 기준 전후 트렌드)
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data
def make_trend(before_level, after_level, noise, seed, before_len=15, after_len=15):
    rng = np.random.default_rng(seed)
    before = before_level + rng.normal(0, noise, before_len)
    before = np.clip(before, a_min=0, a_max=None)
    after = after_level + rng.normal(0, noise * 0.35, after_len)
    after = np.clip(after, a_min=0, a_max=None)
    # 자연스러운 하락 곡선 (전환 구간)
    before_trend = np.linspace(before_level * 1.05, before_level * 0.9, before_len) + before - before_level
    after_trend = np.linspace(after_level * 1.6, after_level * 0.85, after_len) + after - after_level
    return np.concatenate([before_trend, after_trend])

EQUIP_LIST = pd.DataFrame([
    {"설비": "M45-01", "교체일": "2026-06-18"},
    {"설비": "M45-02", "교체일": "2026-06-25"},
    {"설비": "M45-03", "교체일": "2026-07-02"},
    {"설비": "M45-04", "교체일": "-"},
    {"설비": "M45-05", "교체일": "2026-06-30"},
])

IMPROVE_TABLE = pd.DataFrame([
    {"설비": "M45-02", "교체일": "2026-06-25", "교체 전(min/day)": 110, "교체 후(min/day)": 5,  "감소율": -95},
    {"설비": "M45-01", "교체일": "2026-06-18", "교체 전(min/day)": 120, "교체 후(min/day)": 8,  "감소율": -93},
    {"설비": "M45-03", "교체일": "2026-07-02", "교체 전(min/day)": 98,  "교체 후(min/day)": 14, "감소율": -86},
    {"설비": "M45-05", "교체일": "2026-06-30", "교체 전(min/day)": 65,  "교체 후(min/day)": 12, "감소율": -82},
    {"설비": "M45-04", "교체일": "-",          "교체 전(min/day)": 75,  "교체 후(min/day)": 68, "감소율": -9},
])

KPI_SUMMARY = pd.DataFrame([
    {"항목": "Swap Delay Time (min/day)",    "교체 전 평균(-14~-1일)": 104.6, "교체 후 평균(+1~+14일)": 9.8, "변화율": -90.6},
    {"항목": "Upper Temp Alarm (건/day)",     "교체 전 평균(-14~-1일)": 28.4,  "교체 후 평균(+1~+14일)": 2.1, "변화율": -92.6},
    {"항목": "평균 Recovery Time (min)",       "교체 전 평균(-14~-1일)": 11.3,  "교체 후 평균(+1~+14일)": 2.4, "변화율": -78.8},
    {"항목": "1000 Wafer 당 Delay (min)",      "교체 전 평균(-14~-1일)": 22.7,  "교체 후 평균(+1~+14일)": 2.3, "변화율": -89.9},
])

EVENT_TIMELINE = [
    {"date": "05.18", "label": "PM 완료",            "color": "#8A93A6"},
    {"date": "06.05", "label": "PCW 라인\n기포 이슈 발생", "color": "#8A93A6"},
    {"date": "06.12", "label": "Bias Housing\n분리 작업 적용", "color": "#8A93A6"},
    {"date": "06.18", "label": "M45-01\nTCR A급 교체",  "color": PRIMARY_RED},
    {"date": "06.25", "label": "M45-02\nTCR A급 교체",  "color": PRIMARY_PURPLE},
    {"date": "06.30", "label": "M45-05\nTCR A급 교체",  "color": PRIMARY_ORANGE},
    {"date": "07.02", "label": "M45-03\nTCR A급 교체",  "color": "#2AA9A0"},
    {"date": "07.03", "label": "데이터 기준일",         "color": PRIMARY_BLUE},
]

# ────────────────────────────────────────────────────────────────────────────
# 2. 사이드바
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💎 Metal45")
    st.markdown("<div style='margin-top:-14px; color:#8A93A6; font-size:13px;'>TCR 효과 대시보드</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 1. 설비 및 교체일 INPUT")
    selected_equip = st.selectbox("설비 선택", EQUIP_LIST["설비"].tolist(), index=0)
    default_date = EQUIP_LIST.loc[EQUIP_LIST["설비"] == selected_equip, "교체일"].values[0]
    default_date = date(2026, 6, 18) if default_date == "-" else datetime.strptime(default_date, "%Y-%m-%d").date()

    tcr_date = st.date_input("TCR A급 교체일", value=default_date, format="YYYY-MM-DD")
    st.button("저장", use_container_width=True)

    st.markdown("#### 전체 설비 교체일 관리")
    st.dataframe(EQUIP_LIST, hide_index=True, use_container_width=True, height=210)

    st.markdown("---")
    nav = st.radio(
        "메뉴",
        ["📊 대시보드", "🧩 설비별 상세 분석", "📶 전체 설비 비교",
         "🗓️ 이벤트 히스토리", "🔔 알람 리스트", "📋 데이터 테이블", "⚙️ 설정"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:12px; line-height:1.7; color:#B9C0D0;'>
    <b>분석 기준</b><br>
    • 교체 전/후 : 전후 14일 기준<br>
    • 지표 : 1일 평균 기준<br>
    • WPD 0인 날은 평균 계산에서 제외<br>
    • 시간 단위 : 분 (min)
    </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 3. 헤더
# ────────────────────────────────────────────────────────────────────────────
h1, h2, h3, h4 = st.columns([5, 2.1, 1.1, 1.6])
with h1:
    st.markdown(f"### TCR 교체 효과 대시보드 ℹ️")
    st.markdown(
        f"<div style='color:{TEXT_GRAY}; font-size:12.5px; margin-top:-10px;'>"
        "※ 각 설비별 TCR A급 교체일을 기준으로 전후 효과를 분석합니다.</div>",
        unsafe_allow_html=True,
    )
with h2:
    date_range = st.date_input(
        "기간", value=(date(2026, 5, 18), date(2026, 7, 3)),
        label_visibility="collapsed", format="YYYY-MM-DD"
    )
with h3:
    st.button("기간 선택", type="primary", use_container_width=True)
with h4:
    st.markdown(
        f"<div style='text-align:right; font-size:12px; color:{TEXT_GRAY}; padding-top:6px;'>"
        "최종 업데이트 : 2026.07.03 08:30</div>", unsafe_allow_html=True
    )

st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 4. KPI 카드 4개
# ────────────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Upper Chamber Temp Alarm (건수/일)</div>
        <div class="kpi-row">
            <div class="kpi-before-after">
                <div class="kpi-label">교체 전<br>(-14 ~ -1일)</div>
                <div class="kpi-value">37<span class="kpi-unit">건/일</span></div>
            </div>
            <div style="font-size:22px; color:{PRIMARY_BLUE};">➔</div>
            <div class="kpi-before-after">
                <div class="kpi-label">교체 후<br>(+1 ~ +14일)</div>
                <div class="kpi-value">1<span class="kpi-unit">건/일</span></div>
            </div>
        </div>
        <div class="kpi-delta">▼ 97% 감소</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">생산 Loss (Swap Delay Time, min/day)</div>
        <div class="kpi-row">
            <div class="kpi-before-after">
                <div class="kpi-label">교체 전<br>(-14 ~ -1일)</div>
                <div class="kpi-value">120<span class="kpi-unit"> min/day</span></div>
            </div>
            <div style="font-size:22px; color:{PRIMARY_GREEN};">➔</div>
            <div class="kpi-before-after">
                <div class="kpi-label">교체 후<br>(+1 ~ +14일)</div>
                <div class="kpi-value">8<span class="kpi-unit"> min/day</span></div>
            </div>
        </div>
        <div class="kpi-delta" style="color:{PRIMARY_GREEN};">▼ 112 min/day (▼93%)</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(180deg,#FFF7E8,#FFFDF9);">
        <div class="kpi-title">예상 생산성 증가</div>
        <div class="kpi-big" style="color:{PRIMARY_ORANGE};">+95</div>
        <div class="kpi-sub">wafers/day</div>
        <div class="footnote" style="text-align:center;">* 평균 Wafer Time 1.26 min/ea 기준</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">재무성과 (예상)</div>
        <div class="kpi-big" style="color:{PRIMARY_PURPLE};">+2,470</div>
        <div class="kpi-sub">만원/일</div>
        <div class="footnote" style="text-align:center;">* Wafer Margin 26만원/장 기준</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 5. 트렌드 차트 3개 (Swap Delay / Temp Alarm / Upper Chamber Temp)
# ────────────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">2. Swap Delay Time Trend (min/day) ℹ️</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="panel-sub">선택 설비 : {selected_equip} | 교체일 : {tcr_date.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

        y = make_trend(120, 8, noise=8, seed=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=DAY_RANGE, y=y, mode="lines+markers",
                                  name="Delay Time (min/day)",
                                  line=dict(color=PRIMARY_BLUE, width=2),
                                  marker=dict(size=4)))
        fig = switch_marker_layout(fig)
        fig = base_layout(fig, y_title="(min)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">3. Temp Alarm Count Trend (건/일) ℹ️</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="panel-sub">선택 설비 : {selected_equip} | 교체일 : {tcr_date.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

        y = make_trend(37, 1, noise=2.2, seed=2)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=DAY_RANGE, y=y, mode="lines+markers",
                                  name="Alarm Count (건/일)",
                                  line=dict(color=PRIMARY_PURPLE, width=2),
                                  marker=dict(size=4)))
        fig = switch_marker_layout(fig)
        fig = base_layout(fig, y_title="(건)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

with c3:
    with st.container():
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">4. Upper Chamber Temp (℃) ℹ️</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="panel-sub">선택 설비 : {selected_equip} | 교체일 : {tcr_date.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

        rng = np.random.default_rng(3)
        max_t = 72 + rng.normal(0, 1.4, len(DAY_RANGE))
        avg_t = 62 + rng.normal(0, 1.1, len(DAY_RANGE))
        min_t = 58 + rng.normal(0, 1.0, len(DAY_RANGE))
        # 교체 후 살짝 안정화(변동폭 감소)
        for arr, base in [(max_t, 68), (avg_t, 61), (min_t, 59)]:
            arr[15:] = base + rng.normal(0, 0.5, len(arr[15:]))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=DAY_RANGE, y=max_t, mode="lines+markers", name="Max Temp (℃)",
                                  line=dict(color=PRIMARY_RED, width=2), marker=dict(size=3)))
        fig.add_trace(go.Scatter(x=DAY_RANGE, y=avg_t, mode="lines+markers", name="Avg Temp (℃)",
                                  line=dict(color=PRIMARY_BLUE, width=2), marker=dict(size=3)))
        fig.add_trace(go.Scatter(x=DAY_RANGE, y=min_t, mode="lines+markers", name="Min Temp (℃)",
                                  line=dict(color=PRIMARY_GREEN, width=2), marker=dict(size=3)))
        fig = switch_marker_layout(fig, y_top=1.12)
        fig = base_layout(fig, y_title="(℃)")
        fig.update_yaxes(range=[55, 75])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 6. 전체 평균 효과 / 설비별 비교 테이블 / 개선 효과 분포
# ────────────────────────────────────────────────────────────────────────────
d1, d2, d3 = st.columns([1.1, 1.4, 1])

with d1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">5. 전체 설비 평균 효과 (교체일 기준 정렬)</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">모든 설비의 교체일을 기준으로 정렬 후 평균</div>', unsafe_allow_html=True)

    y_avg = make_trend(120, 10, noise=6, seed=42)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=DAY_RANGE, y=y_avg, mode="lines", name="Avg Delay Time (min/day)",
                              line=dict(color=PRIMARY_BLUE, width=2),
                              fill="tozeroy", fillcolor="rgba(47,92,255,0.12)"))
    fig = switch_marker_layout(fig, label="TCR A급 교체 (평균)")
    fig = base_layout(fig, y_title="(min)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with d2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">6. 설비별 개선 효과 비교 (Delay Time 감소) ℹ️</div>', unsafe_allow_html=True)

    disp = IMPROVE_TABLE.copy()
    disp["개선율"] = disp["감소율"].apply(lambda v: f"▼{abs(v)}%")

    def bar_html(pct):
        pct = abs(pct)
        color = PRIMARY_GREEN if pct >= 50 else PRIMARY_RED
        width = max(pct, 4)
        return f"""<div style="background:#EEF0F5; border-radius:4px; width:100%; height:14px;">
        <div style="background:{color}; width:{width}%; height:14px; border-radius:4px;"></div>
        </div>"""

    rows_html = ""
    for _, row in IMPROVE_TABLE.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding:6px 4px; font-weight:600;">{row['설비']}</td>
            <td style="padding:6px 4px; color:{TEXT_GRAY};">{row['교체일']}</td>
            <td style="padding:6px 4px; text-align:right;">{row['교체 전(min/day)']}</td>
            <td style="padding:6px 4px; text-align:right;">{row['교체 후(min/day)']}</td>
            <td style="padding:6px 4px; text-align:right; color:{PRIMARY_BLUE if abs(row['감소율'])>=50 else PRIMARY_RED}; font-weight:700;">▼{abs(row['감소율'])}%</td>
            <td style="padding:6px 4px; width:110px;">{bar_html(row['감소율'])}</td>
        </tr>"""

    table_html = f"""
    <table style="width:100%; border-collapse:collapse; font-size:12.5px;">
    <thead>
        <tr style="color:{TEXT_GRAY}; text-align:left; border-bottom:1px solid #EEF0F5;">
            <th style="padding:6px 4px;">설비</th>
            <th style="padding:6px 4px;">교체일</th>
            <th style="padding:6px 4px; text-align:right;">교체 전(min/day)</th>
            <th style="padding:6px 4px; text-align:right;">교체 후(min/day)</th>
            <th style="padding:6px 4px; text-align:right;">감소율</th>
            <th style="padding:6px 4px;">개선 효과</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with d3:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">7. 개선 효과 분포 (Delay Time 변화율) ℹ️</div>', unsafe_allow_html=True)

    buckets = ["80% 이상", "60~80%", "40~60%", "20~40%", "20% 미만", "악화"]
    counts = [3, 2, 1, 0, 0, 0]
    colors = [PRIMARY_BLUE, PRIMARY_BLUE, PRIMARY_BLUE, "#C7CCDA", "#C7CCDA", PRIMARY_RED]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=buckets, y=counts, marker_color=colors,
                          text=[str(c) if c > 0 else "" for c in counts],
                          textposition="outside"))
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(title="(설비 수)", range=[0, 6], gridcolor="#EEF0F5"),
        xaxis=dict(tickfont=dict(size=10)),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# 7. 이벤트 타임라인 & KPI 요약 테이블
# ────────────────────────────────────────────────────────────────────────────
e1, e2 = st.columns([1.6, 1])

with e1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">8. 이벤트 타임라인 (전체 설비)</div>', unsafe_allow_html=True)

    n = len(EVENT_TIMELINE)
    fig = go.Figure()
    xs = list(range(n))
    fig.add_trace(go.Scatter(x=xs, y=[0]*n, mode="lines", line=dict(color="#DADFEA", width=2), showlegend=False))
    for i, ev in enumerate(EVENT_TIMELINE):
        fig.add_trace(go.Scatter(
            x=[i], y=[0], mode="markers", marker=dict(size=14, color=ev["color"]),
            showlegend=False,
        ))
        fig.add_annotation(x=i, y=0.28, text=f"<b>{ev['date']}</b>", showarrow=False, font=dict(size=11, color=TEXT_DARK))
        fig.add_annotation(x=i, y=-0.30, text=ev["label"].replace("\n", "<br>"), showarrow=False,
                           font=dict(size=10, color=ev["color"] if ev["color"] != "#8A93A6" else TEXT_GRAY))
    fig.update_layout(
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(visible=False, range=[-0.5, n-0.5]),
        yaxis=dict(visible=False, range=[-0.7, 0.55]),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with e2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">9. KPI 요약 테이블 (평균, 교체 전 vs 교체 후)</div>', unsafe_allow_html=True)

    rows_html = ""
    for _, row in KPI_SUMMARY.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding:7px 4px; font-weight:600;">{row['항목']}</td>
            <td style="padding:7px 4px; text-align:right;">{row['교체 전 평균(-14~-1일)']}</td>
            <td style="padding:7px 4px; text-align:right;">{row['교체 후 평균(+1~+14일)']}</td>
            <td style="padding:7px 4px; text-align:right; color:{PRIMARY_BLUE}; font-weight:700;">▼{abs(row['변화율'])}%</td>
        </tr>"""

    table_html = f"""
    <table style="width:100%; border-collapse:collapse; font-size:12.5px;">
    <thead>
        <tr style="color:{TEXT_GRAY}; text-align:left; border-bottom:1px solid #EEF0F5;">
            <th style="padding:7px 4px;">항목</th>
            <th style="padding:7px 4px; text-align:right;">교체 전<br>평균(-14~-1일)</th>
            <th style="padding:7px 4px; text-align:right;">교체 후<br>평균(+1~+14일)</th>
            <th style="padding:7px 4px; text-align:right;">변화율</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    f"<div class='footnote'>※ WPD 0 또는 Wafer 0 인 날짜는 평균 계산에서 제외되었습니다.</div>",
    unsafe_allow_html=True
)
