"""
설비별 TCR 교체 전후 7일 평균 Swap Time 개선 효과 - 덤벨(Dumbbell) 차트
앞서 보여드린 SVG 위젯과 동일한 디자인을 Plotly로 재현한 코드입니다.

사용법:
    from dumbbell_chart import render_dumbbell_chart
    render_dumbbell_chart(df)   # Streamlit 안에서 호출

df 형식 (컬럼명 자유롭게 바꿔도 됨):
    설비      | 교체전_평균 | 교체후_평균
    M45-02    | 110         | 5
    ...
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

GRAY = "#9AA0AC"        # 교체 전 (before)
BLUE = "#2F5CFF"        # 교체 후 (after)
LINE_COLOR = "#C7CCDA"  # 연결선
GREEN = "#1F9D55"       # 개선율 좋음
RED = "#E23D3D"         # 개선율 저조 (기준 임의 지정, 아래 THRESHOLD 참고)
TEXT_DARK = "#1B1F2A"
TEXT_GRAY = "#8A93A6"

THRESHOLD_GOOD = 50   # 이 % 이상 감소하면 green, 미만이면 red


def _pct_change(before, after):
    if before == 0:
        return 0
    return round((after - before) / before * 100, 1)


def build_dumbbell_figure(df: pd.DataFrame,
                           col_equip: str = "설비",
                           col_before: str = "교체전_평균",
                           col_after: str = "교체후_평균") -> go.Figure:
    """df를 받아 개선율 내림차순으로 정렬한 뒤 덤벨 차트 Figure를 반환."""

    data = df.copy()
    data["변화율"] = data.apply(
        lambda r: _pct_change(r[col_before], r[col_after]), axis=1
    )
    # 개선율이 큰(더 많이 감소한) 순서로 정렬 → 위쪽에 배치되도록 역순
    data = data.sort_values("변화율", ascending=False).reset_index(drop=True)
    n = len(data)

    fig = go.Figure()

    # 설비별로 연결선 + 두 개의 점
    for i, row in data.iterrows():
        y = n - i  # 위에서부터 개선율 큰 순서로 표시
        before, after = row[col_before], row[col_after]

        # 연결선
        fig.add_trace(go.Scatter(
            x=[before, after], y=[y, y],
            mode="lines",
            line=dict(color=LINE_COLOR, width=2.5),
            showlegend=False,
            hoverinfo="skip",
        ))

        # 값 라벨 (선 위쪽)
        fig.add_annotation(x=before, y=y, text=f"{before:g}", yshift=14,
                            showarrow=False, font=dict(size=11, color=TEXT_GRAY))
        fig.add_annotation(x=after, y=y, text=f"{after:g}", yshift=14,
                            showarrow=False, font=dict(size=11, color=TEXT_GRAY))

        # 변화율 뱃지 (오른쪽 끝)
        color = GREEN if abs(row["변화율"]) >= THRESHOLD_GOOD else RED
        fig.add_annotation(
            x=1.02, xref="paper", y=y, text=f"<b>{row['변화율']:.0f}%</b>",
            showarrow=False, font=dict(size=13, color=color),
            xanchor="left",
        )

    # 교체 전 점 (회색)
    fig.add_trace(go.Scatter(
        x=data[col_before], y=list(range(n, 0, -1)),
        mode="markers", name="교체 전 (7일 평균)",
        marker=dict(size=11, color=GRAY, line=dict(color="white", width=1)),
    ))

    # 교체 후 점 (파란색)
    fig.add_trace(go.Scatter(
        x=data[col_after], y=list(range(n, 0, -1)),
        mode="markers", name="교체 후 (7일 평균)",
        marker=dict(size=11, color=BLUE, line=dict(color="white", width=1)),
    ))

    fig.update_layout(
        height=70 * n + 90,
        margin=dict(l=10, r=70, t=40, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12)),
        xaxis=dict(title="Swap Time (min)", showgrid=True, gridcolor="#EEF0F5",
                   zeroline=False),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(n, 0, -1)),
            ticktext=data[col_equip].tolist(),
            showgrid=False, zeroline=False,
            range=[0.4, n + 0.8],
        ),
        font=dict(size=12, color=TEXT_DARK),
    )
    return fig


def render_dumbbell_chart(df: pd.DataFrame,
                           col_equip: str = "설비",
                           col_before: str = "교체전_평균",
                           col_after: str = "교체후_평균",
                           title: str = "설비별 TCR 교체 전후 평균 Swap Time"):
    """Streamlit 안에서 바로 호출하는 렌더 함수."""
    st.markdown(f"#### {title}")
    fig = build_dumbbell_figure(df, col_equip, col_before, col_after)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── 단독 실행 테스트 (streamlit run dumbbell_chart.py) ──────────────────────
if __name__ == "__main__":
    st.set_page_config(layout="wide")

    sample_df = pd.DataFrame([
        {"설비": "M45-02", "교체전_평균": 110, "교체후_평균": 5},
        {"설비": "M45-01", "교체전_평균": 120, "교체후_평균": 8},
        {"설비": "M45-03", "교체전_평균": 98,  "교체후_평균": 14},
        {"설비": "M45-05", "교체전_평균": 65,  "교체후_평균": 12},
        {"설비": "M45-04", "교체전_평균": 75,  "교체후_평균": 68},
    ])

    render_dumbbell_chart(sample_df)
