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
                           col_after: str = "교체후_평균",
                           compact: bool = None) -> go.Figure:
    """df를 받아 개선율 내림차순으로 정렬한 뒤 덤벨 차트 Figure를 반환.

    compact: None이면 행 개수(n)가 10개 이상일 때 자동으로 압축 모드 적용.
             True/False로 직접 지정도 가능.
             압축 모드에서는 행 높이를 줄이고, 전/후 숫자 라벨은 항상 표시하는 대신
             hover(툴팁)로 옮겨서 16개 이상 챔버에서도 겹치지 않게 함.
    """

    data = df.copy()
    data["변화율"] = data.apply(
        lambda r: _pct_change(r[col_before], r[col_after]), axis=1
    )
    # 개선율이 큰(더 많이 감소한) 순서로 정렬 → 위쪽에 배치되도록 역순
    data = data.sort_values("변화율", ascending=False).reset_index(drop=True)
    n = len(data)

    if compact is None:
        compact = n >= 10

    row_height = 34 if compact else 70
    marker_size = 8 if compact else 11
    badge_font = 11 if compact else 13
    value_font = 10 if compact else 11

    fig = go.Figure()

    # 설비별로 연결선 + (compact 아닐 때만) 값 라벨 + 변화율 뱃지
    for i, row in data.iterrows():
        y = n - i  # 위에서부터 개선율 큰 순서로 표시
        before, after = row[col_before], row[col_after]

        # 연결선
        fig.add_trace(go.Scatter(
            x=[before, after], y=[y, y],
            mode="lines",
            line=dict(color=LINE_COLOR, width=2 if compact else 2.5),
            showlegend=False,
            hoverinfo="skip",
        ))

        if not compact:
            # 값 라벨을 선 위에 항상 표시 (챔버 수 적을 때만)
            fig.add_annotation(x=before, y=y, text=f"{before:g}", yshift=14,
                                showarrow=False, font=dict(size=value_font, color=TEXT_GRAY))
            fig.add_annotation(x=after, y=y, text=f"{after:g}", yshift=14,
                                showarrow=False, font=dict(size=value_font, color=TEXT_GRAY))

        # 변화율 뱃지 (오른쪽 끝) - compact 모드에서도 유지
        color = GREEN if abs(row["변화율"]) >= THRESHOLD_GOOD else RED
        fig.add_annotation(
            x=1.02, xref="paper", y=y, text=f"<b>{row['변화율']:.0f}%</b>",
            showarrow=False, font=dict(size=badge_font, color=color),
            xanchor="left",
        )

    # 교체 전 점 (회색) - compact 모드에서는 값이 hover로만 표시됨
    fig.add_trace(go.Scatter(
        x=data[col_before], y=list(range(n, 0, -1)),
        mode="markers", name="교체 전 (7일 평균)",
        marker=dict(size=marker_size, color=GRAY, line=dict(color="white", width=1)),
        hovertemplate="%{customdata}<br>교체 전: %{x:g}<extra></extra>" if compact else None,
        customdata=data[col_equip] if compact else None,
        hoverinfo="skip" if not compact else None,
    ))

    # 교체 후 점 (파란색)
    fig.add_trace(go.Scatter(
        x=data[col_after], y=list(range(n, 0, -1)),
        mode="markers", name="교체 후 (7일 평균)",
        marker=dict(size=marker_size, color=BLUE, line=dict(color="white", width=1)),
        hovertemplate="%{customdata}<br>교체 후: %{x:g}<extra></extra>" if compact else None,
        customdata=data[col_equip] if compact else None,
        hoverinfo="skip" if not compact else None,
    ))

    fig.update_layout(
        height=row_height * n + 90,
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
            tickfont=dict(size=11 if compact else 12),
        ),
        font=dict(size=12, color=TEXT_DARK),
    )
    return fig


def render_dumbbell_chart(df: pd.DataFrame,
                           col_equip: str = "설비",
                           col_before: str = "교체전_평균",
                           col_after: str = "교체후_평균",
                           title: str = "설비별 TCR 교체 전후 평균 Swap Time",
                           compact: bool = None):
    """Streamlit 안에서 바로 호출하는 렌더 함수.

    compact=None이면 챔버 수가 10개 이상일 때 자동으로 압축 레이아웃 적용.
    16개 챔버처럼 항목이 많을 땐 compact=True를 명시해도 됩니다.
    """
    st.markdown(f"#### {title}")
    if compact or (compact is None and len(df) >= 10):
        st.caption("항목이 많아 압축 모드로 표시 중 · 전/후 값은 점에 마우스를 올리면 확인 가능")
    fig = build_dumbbell_figure(df, col_equip, col_before, col_after, compact=compact)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── 단독 실행 테스트 (streamlit run dumbbell_chart.py) ──────────────────────
if __name__ == "__main__":
    import numpy as np

    st.set_page_config(layout="wide")

    st.markdown("### 5개 설비 - 기본 모드")
    sample_df = pd.DataFrame([
        {"설비": "M45-02", "교체전_평균": 110, "교체후_평균": 5},
        {"설비": "M45-01", "교체전_평균": 120, "교체후_평균": 8},
        {"설비": "M45-03", "교체전_평균": 98,  "교체후_평균": 14},
        {"설비": "M45-05", "교체전_평균": 65,  "교체후_평균": 12},
        {"설비": "M45-04", "교체전_평균": 75,  "교체후_평균": 68},
    ])
    render_dumbbell_chart(sample_df)

    st.markdown("---")
    st.markdown("### 16개 챔버 - 압축(compact) 모드 자동 적용")
    rng = np.random.default_rng(11)
    chambers_16 = [f"M45-{i:02d}" for i in range(1, 17)]
    before_vals = rng.uniform(60, 130, size=16).round(0)
    # 챔버마다 개선율을 다양하게 부여 (일부는 효과 미미하게)
    improve_ratio = rng.uniform(0.05, 0.95, size=16)
    after_vals = (before_vals * (1 - improve_ratio)).round(0)

    sample_df_16 = pd.DataFrame({
        "설비": chambers_16,
        "교체전_평균": before_vals,
        "교체후_평균": after_vals,
    })
    render_dumbbell_chart(sample_df_16)
