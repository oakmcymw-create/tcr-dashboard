"""
챔버(설비) x 날짜 히트맵 - TCR 예지보전 모니터링용
16개 챔버 전체를 한 화면에서 스캔하며 "최근 온도가 나빠지고 있는 챔버"를
색으로 바로 짚어내기 위한 차트입니다.

사용법:
    from heatmap_chart import render_chamber_heatmap
    render_chamber_heatmap(df)   # Streamlit 안에서 호출

df 형식 (long format, 컬럼명 자유롭게 바꿔도 됨):
    설비      | 날짜        | max_temp
    M45-01    | 2026-07-01  | 61.2
    M45-01    | 2026-07-02  | 62.0
    ...
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

SETPOINT = 60      # TCR 설정 온도
ALARM_TEMP = 70     # Warning 알람 기준 온도


def _pivot_wide(df: pd.DataFrame, col_equip: str, col_date: str, col_temp: str) -> pd.DataFrame:
    """long format -> 챔버 x 날짜 wide format 피벗."""
    wide = df.pivot_table(index=col_equip, columns=col_date, values=col_temp, aggfunc="mean")
    wide = wide.sort_index(axis=1)  # 날짜 오름차순 정렬
    return wide


def build_heatmap_figure(df: pd.DataFrame,
                          col_equip: str = "설비",
                          col_date: str = "날짜",
                          col_temp: str = "max_temp",
                          sort_by_latest: bool = True) -> go.Figure:
    """df를 받아 최근 값이 높은(위험한) 챔버가 위로 오도록 정렬한 히트맵 Figure 반환."""

    wide = _pivot_wide(df, col_equip, col_date, col_temp)

    if sort_by_latest:
        latest_col = wide.columns[-1]
        wide = wide.loc[wide[latest_col].sort_values(ascending=True).index]
        # Plotly heatmap은 y축 아래->위 순서이므로, 위험한 챔버가 맨 위에
        # 보이도록 오름차순으로 정렬해 리스트에 넣음 (마지막 항목이 위쪽)

    fig = go.Figure(data=go.Heatmap(
        z=wide.values,
        x=[str(c) for c in wide.columns],
        y=wide.index.tolist(),
        colorscale=[
            [0.0, "#0F6E56"],   # 여유 있음 (teal, 낮은 온도)
            [0.45, "#5DCAA5"],
            [0.6, "#FAC775"],   # 관심 (amber)
            [0.78, "#EF9F27"],
            [0.9, "#E24B4A"],   # 위험 (red, 알람 근접)
            [1.0, "#791F1F"],
        ],
        zmin=SETPOINT - 3,
        zmax=ALARM_TEMP + 2,
        colorbar=dict(title="Max Temp(℃)", thickness=14),
        hovertemplate="%{y}<br>%{x}<br>Max Temp: %{z:.1f}℃<extra></extra>",
        xgap=2,
        ygap=2,
    ))

    # 알람 기준선(70℃) 도달 여부를 컬러바 옆에 텍스트로 안내
    fig.update_layout(
        height=max(360, 26 * len(wide.index) + 100),
        margin=dict(l=10, r=10, t=30, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(title="날짜", side="bottom", tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(title="", tickfont=dict(size=12)),
        font=dict(size=12, color="#1B1F2A"),
    )
    return fig


def render_chamber_heatmap(df: pd.DataFrame,
                            col_equip: str = "설비",
                            col_date: str = "날짜",
                            col_temp: str = "max_temp",
                            title: str = "챔버별 Max Temp 히트맵 (예지보전 모니터링)"):
    """Streamlit 안에서 바로 호출하는 렌더 함수."""
    st.markdown(f"#### {title}")
    st.caption(f"설정온도 {SETPOINT}℃ / 알람기준 {ALARM_TEMP}℃ · 붉은 셀이 많은 챔버일수록 교체 우선순위 높음")
    fig = build_heatmap_figure(df, col_equip, col_date, col_temp)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── 단독 실행 테스트 (streamlit run heatmap_chart.py) ────────────────────────
if __name__ == "__main__":
    st.set_page_config(layout="wide")

    # 16개 챔버 x 21일 샘플 데이터 생성
    rng = np.random.default_rng(7)
    n_chambers = 16
    n_days = 21
    dates = pd.date_range("2026-06-20", periods=n_days, freq="D").strftime("%m-%d")
    chambers = [f"M45-{i:02d}" for i in range(1, n_chambers + 1)]

    # 챔버마다 서로 다른 열화 속도를 부여 (일부는 상승 추세, 대부분은 안정)
    degrade_rate = rng.choice(
        [0.0, 0.0, 0.0, 0.05, 0.1, 0.15, 0.35, 0.5],
        size=n_chambers, replace=True
    )
    base_temp = rng.uniform(60, 63, size=n_chambers)

    rows = []
    for i, ch in enumerate(chambers):
        for d in range(n_days):
            val = base_temp[i] + degrade_rate[i] * d + rng.normal(0, 0.8)
            rows.append({"설비": ch, "날짜": dates[d], "max_temp": round(val, 1)})

    sample_df = pd.DataFrame(rows)

    render_chamber_heatmap(sample_df)
