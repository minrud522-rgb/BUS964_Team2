"""
HealthOn CTR 예측 시연용 Streamlit 앱
Business Analytics Programming I - Team 2
윤민경, 전윤희, 고은주

[실행 방법]
pip install streamlit plotly
streamlit run BUS964_FinalDemo_Team2.py

[앱 설명]
데이터 수집 체계 개선 전후로 CTR 예측이 어떻게 달라지는지
가상의 광고 대상자를 설정하여 직관적으로 시연하는 앱.
- 왼쪽: 현재 보유 7개 변수 기반 예측 (나이만 유의미)
- 오른쪽: 개선 후 12개 변수 기반 예측 (다양한 변수 반영)
"""

import streamlit as st
import plotly.graph_objects as go

PRIMARY = "#3D7A5A"
PRIMARY_DARK = "#2F6149"
DANGER = "#C0392B"
WHITE = "#FFFFFF"
PAGE_BG = "#F1F4F3"
GRAY_MUTED = "#8B95A1"
GAUGE_GRAY = "#9CA3AF"
BORDER = "#D8E0DC"
# 게이지 배경: 단일 톤 초록 3단계 (낮음 → 높음)
GAUGE_STEP_LOW = "#EDF7F1"
GAUGE_STEP_MID = "#CFE8D9"
GAUGE_STEP_HIGH = "#A6D4B8"

# 양쪽 게이지 동일 픽셀 스케일: domain·margin·height 를 완전히 동일하게 유지
GAUGE_INDICATOR_DOMAIN = {"x": [0.06, 0.90], "y": [0.26, 0.84]}


st.set_page_config(
    page_title="HealthOn CTR 예측 시스템",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

    html, body, [class*="css"]  {{
        font-family: "Noto Sans KR", -apple-system, BlinkMacSystemFont,
            "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }}

    .stApp {{
        background-color: {PAGE_BG};
    }}

    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    .block-container {{
        padding-top: 0.85rem !important;
        padding-bottom: 1.25rem !important;
        max-width: min(1480px, 100%);
    }}

    footer {{ visibility: hidden; height: 0; }}

    div[data-testid="stHorizontalBlock"] {{
        gap: 1.1rem !important;
        align-items: flex-start !important;
    }}
    div[data-testid="column"] {{
        background: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 1.1rem 1.2rem 1.2rem !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}

    div[data-testid="column"] .stMarkdown h3 {{
        margin: 0 0 0.12rem 0;
        font-size: 0.98rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.02em;
    }}

    .healthon-header {{
        background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
        color: {WHITE};
        padding: 0.75rem 1.25rem;
        border-radius: 14px;
        margin-bottom: 0.6rem;
        box-shadow: 0 3px 14px rgba(61, 122, 90, 0.18);
        text-align: center;
    }}
    .healthon-header h1 {{
        margin: 0;
        font-size: 1.22rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.35;
    }}

    .compare-label {{
        color: {GRAY_MUTED};
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 0.5rem 0.1rem;
    }}

    .badge-pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.26rem 0.72rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 0.35rem;
        background-color: {PRIMARY};
        color: {WHITE};
        box-shadow: 0 1px 4px rgba(61, 122, 90, 0.2);
    }}

    .panel-lead {{
        color: {PRIMARY};
        font-size: 0.82rem;
        font-weight: 600;
        line-height: 1.45;
        margin: 0 0 0.65rem 0;
    }}

    .status-strip {{
        min-height: 2.35rem;
        display: flex;
        align-items: center;
        padding: 0.4rem 0.65rem;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 500;
        line-height: 1.35;
        margin-bottom: 0.65rem;
    }}
    .status-strip-ok {{
        background: #E8F3ED;
        color: #1E4D36;
        border: 1px solid rgba(61, 122, 90, 0.28);
    }}

    /* 광고 클릭률 예측: 테두리 카드 — 세로·가로 중앙 (내부 블록이 남는 높이를 채우고 가운데 정렬) */
    div[class*="ho_gauge_panel"],
    div[id*="ho_gauge_panel"] {{
        border: 1.5px solid #A8C9B6 !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
        padding: 0.5rem 0.55rem 0.5rem !important;
        margin: 0.25rem 0 0.4rem !important;
        box-shadow: 0 1px 2px rgba(61, 122, 90, 0.05);
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        justify-content: center !important;
        min-height: 268px;
        box-sizing: border-box;
    }}
    div[class*="ho_gauge_panel"] > div,
    div[id*="ho_gauge_panel"] > div {{
        width: 100% !important;
        flex: 1 1 auto !important;
        min-height: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    div[class*="ho_gauge_panel"] [data-testid="stMarkdownContainer"],
    div[id*="ho_gauge_panel"] [data-testid="stMarkdownContainer"] {{
        text-align: center;
    }}
    div[class*="ho_gauge_panel"] [data-testid="stPlotlyChart"],
    div[id*="ho_gauge_panel"] [data-testid="stPlotlyChart"] {{
        width: 100% !important;
        max-width: 100%;
        margin-left: auto !important;
        margin-right: auto !important;
        overflow: visible !important;
    }}

    .gauge-block {{
        margin: 0 auto;
        padding: 0.1rem 0 0.15rem;
        text-align: center;
        max-width: 100%;
    }}
    .gauge-heading {{
        font-size: 0.95rem;
        font-weight: 700;
        color: #111827;
        margin: 0 0 0.15rem 0;
        padding-top: 0;
        line-height: 1.35;
        letter-spacing: -0.02em;
    }}
    .gauge-sub {{
        font-size: 0.72rem;
        color: {GRAY_MUTED};
        margin: 0 0 0.2rem 0;
        line-height: 1.35;
    }}

    div[data-testid="stPlotlyChart"] {{
        overflow: visible !important;
    }}
    [data-testid="stPlotlyChart"] iframe {{
        min-height: 172px;
        max-width: 100%;
    }}
    div[class*="ho_gauge_panel"] [data-testid="stPlotlyChart"] iframe,
    div[id*="ho_gauge_panel"] [data-testid="stPlotlyChart"] iframe {{
        width: 100% !important;
        min-height: 188px;
        height: 188px !important;
    }}

    .explain-box {{
        background: #EAF4EE;
        color: #234536;
        border: 1px solid rgba(61, 122, 90, 0.2);
        border-left: 4px solid {PRIMARY};
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        font-size: 0.8rem;
        line-height: 1.5;
        white-space: pre-line;
        margin-top: 0.35rem;
    }}

    /*
     * 슬라이더: Streamlit 1.39+ 는 primaryColor(→ .streamlit/config.toml)로 트랙·썸·숫자 색을 씁니다.
     * 숫자 라벨 testid 는 stSliderThumbValue 입니다(stThumbValue 아님).
     */
    div[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {{
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }}
    div[data-testid="stSlider"] label p {{
        color: #374151 !important;
    }}
    div[data-testid="stSlider"] input[type="range"] {{
        accent-color: #111827;
    }}
    div[data-testid="stSlider"] input[type="range"]::-webkit-slider-thumb {{
        background: #111827 !important;
        border: 2px solid #111827 !important;
    }}
    div[data-testid="stSlider"] input[type="range"]::-moz-range-thumb {{
        background: #111827 !important;
        border: 2px solid #111827 !important;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


def base_ctr_from_age(age: int) -> int:
    if 18 <= age <= 29:
        return 55
    if 30 <= age <= 39:
        return 50
    if 40 <= age <= 49:
        return 45
    return 40


def improved_ctr_delta(
    stay: str,
    impressions: str,
    health_goal: str,
    payment: str,
    ad_clicks: str,
) -> int:
    d = 0
    if stay == "10분 미만":
        d -= 10
    elif stay == "10~30분":
        d += 0
    else:
        d += 15

    if impressions == "1회":
        d -= 5
    elif impressions == "2~3회":
        d += 15
    else:
        d -= 5

    if health_goal == "다이어트":
        d += 15
    elif health_goal == "근력 향상":
        d += 10
    elif health_goal == "질환 관리":
        d += 5

    if payment == "1회":
        d += 10
    elif payment == "2회 이상":
        d += 20

    if ad_clicks == "1~2회":
        d += 10
    elif ad_clicks == "3회 이상":
        d += 20

    return d


def _gauge_axis() -> dict:
    return {
        "range": [0, 100],
        "tickwidth": 1,
        "tickcolor": "#9CA3AF",
        "tickfont": {"size": 12, "color": "#374151"},
        "dtick": 20,
    }


def _gauge_figure_layout() -> dict:
    # 좌·우 차트에 동일 적용 → 컨테이너 너비가 같을 때 막대 실제 길이 동일
    return dict(
        height=184,
        margin=dict(l=18, r=64, t=6, b=74),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Noto Sans KR, sans-serif",
            color="#374151",
            size=12,
        ),
    )


def bullet_current(value: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge",
            value=value,
            domain=GAUGE_INDICATOR_DOMAIN,
            title={"text": ""},
            number={
                "suffix": "%",
                "font": {"size": 21, "color": "#111827"},
            },
            gauge={
                "shape": "bullet",
                "axis": _gauge_axis(),
                "bar": {"color": GAUGE_GRAY},
                "bgcolor": "#E5E7EB",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 33], "color": GAUGE_STEP_LOW},
                    {"range": [33, 66], "color": GAUGE_STEP_MID},
                    {"range": [66, 100], "color": GAUGE_STEP_HIGH},
                ],
                "threshold": {
                    "line": {"color": PRIMARY_DARK, "width": 2},
                    "thickness": 0.88,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(**_gauge_figure_layout())
    return fig


def bullet_improved(value: float, reference: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge+delta",
            value=value,
            delta={
                "reference": reference,
                "increasing": {"color": PRIMARY},
                "decreasing": {"color": DANGER},
                "font": {"size": 11},
                "position": "bottom",
                "valueformat": "+.0f",
            },
            domain=GAUGE_INDICATOR_DOMAIN,
            title={"text": ""},
            number={
                "suffix": "%",
                "font": {"size": 21, "color": PRIMARY_DARK},
            },
            gauge={
                "shape": "bullet",
                "axis": _gauge_axis(),
                "bar": {"color": PRIMARY},
                "bgcolor": "#E5E7EB",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 33], "color": GAUGE_STEP_LOW},
                    {"range": [33, 66], "color": GAUGE_STEP_MID},
                    {"range": [66, 100], "color": GAUGE_STEP_HIGH},
                ],
                "threshold": {
                    "line": {"color": PRIMARY_DARK, "width": 2},
                    "thickness": 0.88,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(**_gauge_figure_layout())
    return fig


PLOT_CONFIG = {"displayModeBar": False}


def render_gauge_block(fig: go.Figure, *, panel_key: str) -> None:
    with st.container(border=True, key=panel_key, gap=None):
        st.markdown(
            """
            <div class="gauge-block">
            <div class="gauge-heading">광고 클릭률 예측</div>
            <div class="gauge-sub">0~100% 스케일 · 동일 조건 비교</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)


# ----- 헤더 -----
st.markdown(
    """
    <div class="healthon-header">
        <h1>HealthOn CTR 예측 시스템</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="compare-label">예측 비교</p>', unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="medium")

# ----- 왼쪽: 현재 -----
with col_left:
    st.markdown(
        '<div class="badge-pill">현재 상황 · 보유 변수 7개</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="panel-lead">나이 외 정보 부족으로 정교한 예측 불가</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### 현재 수집 중인 데이터")
    st.caption("현재 보유 정보")
    st.markdown(
        '<div class="status-strip status-strip-ok">'
        "현재 예측 모델에는 <strong>나이</strong>만 클릭률에 유의미한 영향"
        "</div>",
        unsafe_allow_html=True,
    )

    age = st.slider("나이", 18, 64, 35, key="age_main")
    g1, g2, g3 = st.columns(3)
    with g1:
        gender = st.selectbox("성별", ["남성", "여성", "기타"], key="gender_main")
    with g2:
        device = st.selectbox(
            "접속 기기", ["모바일", "PC", "태블릿"], key="device_main"
        )
    with g3:
        interest = st.selectbox(
            "관심 콘텐츠",
            ["엔터테인먼트", "뉴스", "쇼핑", "교육", "소셜미디어"],
            key="interest_main",
        )
    g4, g5, _ = st.columns([1, 1, 1])
    with g4:
        ad_pos = st.selectbox("광고 위치", ["상단", "측면", "하단"], key="adpos_main")
    with g5:
        ad_time = st.selectbox(
            "광고 노출 시간대",
            ["아침", "오후", "저녁", "밤"],
            key="adtime_main",
        )

    render_gauge_block(
        bullet_current(float(base_ctr_from_age(age))),
        panel_key="ho_gauge_panel_left",
    )

    st.markdown(
        """
        <div class="explain-box">유의미한 변수는 <strong>나이</strong> 1개
나머지 5개 변수는 예측에 기여하지 못함</div>
        """,
        unsafe_allow_html=True,
    )

# ----- 오른쪽: 개선 후 (항상 표시) -----
current_prob = float(base_ctr_from_age(age))

with col_right:
    st.markdown(
        '<div class="badge-pill">데이터 개선 후 · 보유 변수 12개</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="panel-lead">12개 변수로 정교한 예측 가능</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### 데이터 개선 후 추가 정보")
    st.caption("수집 체계 개선 시 함께 활용되는 정보")
    st.markdown(
        '<div class="status-strip status-strip-ok">'
        "추가 데이터 확보 — 정교한 예측 가능"
        "</div>",
        unsafe_allow_html=True,
    )

    h1, h2 = st.columns(2)
    with h1:
        stay = st.selectbox(
            "앱 체류 시간",
            ["10분 미만", "10~30분", "30분 이상"],
            key="stay_main",
        )
        health_goal = st.selectbox(
            "건강 목표",
            ["다이어트", "근력 향상", "질환 관리", "건강 유지"],
            key="health_main",
        )
        ad_clicks = st.selectbox(
            "광고 클릭 이력",
            ["없음", "1~2회", "3회 이상"],
            key="adclk_main",
        )
    with h2:
        impressions = st.selectbox(
            "광고 노출 횟수",
            ["1회", "2~3회", "4회 이상"],
            key="imp_main",
        )
        payment = st.selectbox(
            "구독/결제 이력",
            ["없음", "1회", "2회 이상"],
            key="pay_main",
        )

    delta_pts = improved_ctr_delta(
        stay, impressions, health_goal, payment, ad_clicks
    )
    improved_prob = float(max(5, min(95, base_ctr_from_age(age) + delta_pts)))

    render_gauge_block(
        bullet_improved(improved_prob, current_prob),
        panel_key="ho_gauge_panel_right",
    )

    diff = improved_prob - current_prob
    st.markdown(
        f"""
        <div class="explain-box">예측에 사용된 변수: 12개
현재 대비 클릭 확률 변화: {diff:+.0f}%p
→ 다양한 변수로 고객의 행동 패턴 파악 가능</div>
        """,
        unsafe_allow_html=True,
    )

_ = (gender, device, interest, ad_pos, ad_time)
