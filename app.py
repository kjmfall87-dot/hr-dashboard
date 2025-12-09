import streamlit as st
import pandas as pd
import numpy as np

# =========================================
# 0. 기본 설정
# =========================================
st.set_page_config(
    page_title="HR 인사이트 대시보드",
    layout="wide"
)

st.title("👥 HR 인사이트 대시보드")

# =========================================
# 1. 데이터 로딩 함수
# =========================================
@st.cache_data
def load_data():
    # 같은 폴더의 company_hr_data.xlsx 읽기
    xls = pd.ExcelFile("company_hr_data.xlsx")
    df_change = pd.read_excel(xls, "인원변동")
    df_turnover = pd.read_excel(xls, "퇴사율")
    df_retention = pd.read_excel(xls, "잔존율")
    df_tenure = pd.read_excel(xls, "근속")
    return df_change, df_turnover, df_retention, df_tenure

# =========================================
# 2. 유틸리티 함수들
# =========================================
def to_month_period(series):
    """월 컬럼을 연-월 형태로 통일"""
    return pd.to_datetime(series).dt.to_period("M").astype(str)

# =========================================
# 3. 인사이트 코멘트 생성 함수들
# =========================================

# 3-1. 인원 변동 / 입·퇴사 인사이트
def analyze_headcount(df_change):
    text_blocks = []

    df = df_change.copy()
    df["월"] = to_month_period(df["월"])
    df = df.sort_values("월")

    if len(df) < 3:
        return "📌 인원변동 데이터가 3개월 미만이라, 추세 분석은 어렵습니다. (모르겠습니다)"

    recent_df = df.tail(6).copy()
    recent_df_reset = recent_df.reset_index(drop=True)

    last3 = recent_df_reset.tail(3)
    prev3 = recent_df_reset.head(len(recent_df_reset) - 3)

    if len(prev3) == 0:
        prev3 = last3  # 비교 불가 시 동일 기간으로 처리 (추측입니다)

    hire_last3 = last3["입사자"].sum()
    hire_prev3 = prev3["입사자"].sum()
    sep_last3 = last3["퇴사자"].sum()
    sep_prev3 = prev3["퇴사자"].sum()

    total_last = df["총원"].iloc[-1]
    total_first = df["총원"].iloc[0]
    total_change = total_last - total_first

    def pct_change(new, old):
        if old == 0:
            return np.nan
        return (new - old) / old * 100

    hire_chg = pct_change(hire_last3, hire_prev3)
    sep_chg = pct_change(sep_last3, sep_prev3)

    # 1) 입사자 추세 (표현 다양화)
    hire_comment = f"최근 3개월 입사자는 총 **{hire_last3}명**이며, 직전 3개월 대비 "
    if pd.isna(hire_chg):
        hire_comment += "비교 가능한 과거 데이터가 부족합니다. (확실하지 않음)"
    elif hire_chg > 40:
        hire_comment += (
            f"**{hire_chg:.1f}% 급증**했습니다. 공격적으로 인력을 확장하는 국면으로 볼 수 있습니다. (추측입니다)"
        )
    elif hire_chg > 20:
        hire_comment += (
            f"**{hire_chg:.1f}% 증가**했습니다. 채용 강도가 이전보다 확실히 높아진 상태입니다."
        )
    elif hire_chg > 5:
        hire_comment += (
            f"**{hire_chg:.1f}% 소폭 증가**했습니다. 완만하게 인력을 확충하는 흐름입니다."
        )
    elif hire_chg < -40:
        hire_comment += (
            f"**{abs(hire_chg):.1f}% 급감**했습니다. 채용 축소 또는 채용 전략 변화가 있었을 가능성이 큽니다. (추측입니다)"
        )
    elif hire_chg < -20:
        hire_comment += (
            f"**{abs(hire_chg):.1f}% 감소**했습니다. 신규 충원이 눈에 띄게 줄어든 상태입니다."
        )
    elif hire_chg < -5:
        hire_comment += (
            f"**{abs(hire_chg):.1f}% 소폭 감소**했습니다. 당장은 큰 리스크는 아니지만, "
            "채용 파이프라인을 점검해 보는 것이 좋습니다. (추측입니다)"
        )
    else:
        hire_comment += (
            f"{hire_chg:.1f}% 변동으로, 큰 변화 없이 **안정적인 채용 수준**이 유지되고 있습니다."
        )
    text_blocks.append("🔹 **입사자 추세 인사이트**\n" + hire_comment)

    # 2) 퇴사자 추세 (표현 다양화)
    sep_comment = f"최근 3개월 퇴사자는 총 **{sep_last3}명**이며, 직전 3개월 대비 "
    if pd.isna(sep_chg):
        sep_comment += "비교 가능한 과거 데이터가 부족합니다. (확실하지 않음)"
    elif sep_chg > 40:
        sep_comment += (
            f"**{sep_chg:.1f}% 급증**했습니다. 단기간에 이탈이 몰리면서, "
            "조직 안정성 측면에서 강한 경고 신호로 해석될 수 있습니다. (추측입니다)"
        )
    elif sep_chg > 20:
        sep_comment += (
            f"**{sep_chg:.1f}% 증가**했습니다. 이탈이 눈에 띄게 많아진 구간으로, "
            "원인 분석과 조기 대응이 필요한 상태입니다. (추측입니다)"
        )
    elif sep_chg > 5:
        sep_comment += (
            f"**{sep_chg:.1f}% 소폭 증가**했습니다. 당장 심각한 수준은 아니지만, "
            "특정 부서·직무에 편중되어 있는지 확인하는 것이 좋습니다. (추측입니다)"
        )
    elif sep_chg < -20:
        sep_comment += (
            f"**{abs(sep_chg):.1f}% 감소**했습니다. 이탈이 뚜렷하게 줄어든 안정 구간입니다."
        )
    elif sep_chg < -5:
        sep_comment += (
            f"**{abs(sep_chg):.1f}% 소폭 감소**했습니다. 이탈 관리가 비교적 잘 이뤄지고 있는 흐름입니다. (추측입니다)"
        )
    else:
        sep_comment += (
            f"{sep_chg:.1f}% 변동으로, 이탈 수준은 **크게 흔들림 없이 유지**되고 있습니다."
        )
    text_blocks.append("🔹 **퇴사자 추세 인사이트**\n" + sep_comment)

    # 3) 총원 추세 (장기)
    if total_change > 0:
        total_comment = (
            f"분석 기간 전체로 보면 총원은 **+{total_change}명** 증가했습니다. "
            "장기적으로 조직을 키워가는 성장 전략이 유지되고 있는 모습입니다."
        )
    elif total_change < 0:
        total_comment = (
            f"분석 기간 전체로 보면 총원은 **{total_change}명** 감소했습니다. "
            "채용 축소, 자연 이탈, 선택적 구조조정 등이 함께 영향을 준 결과일 수 있습니다. (추측입니다)"
        )
    else:
        total_comment = (
            "분석 기간 동안 총원은 거의 변동이 없었습니다. "
            "채용과 퇴사가 거의 균형을 이루는, 안정적인 인력 유지 구간으로 볼 수 있습니다."
        )
    text_blocks.append("🔹 **총원 장기 추세 인사이트**\n" + total_comment)

    # 4) 종합 평가
    net_last3 = hire_last3 - sep_last3
    if net_last3 > 0 and (not pd.isna(sep_chg) and sep_chg < 20):
        overall = (
            "최근 3개월은 **순증가(입사 > 퇴사)** 구간으로, "
            "단기 리스크는 낮고 성장을 지향하는 국면으로 해석할 수 있습니다. (추측입니다)"
        )
    elif net_last3 < 0 and (not pd.isna(sep_chg) and sep_chg > 20):
        overall = (
            "최근 3개월은 **순감소(퇴사 > 입사)** 구간이며, "
            "퇴사 증가까지 겹쳐 **조직 안정성 측면에서 주의 깊은 모니터링이 필요한 시기**입니다. (추측입니다)"
        )
    else:
        overall = (
            "입·퇴사와 총원 모두 큰 폭의 변화는 아니지만, "
            "세부 부서·직무 단위에서의 변동 패턴을 함께 살펴보는 것이 좋습니다. (추측입니다)"
        )
    text_blocks.append("🔹 **종합 인사이트**\n" + overall)

    return "\n\n".join(text_blocks)

# 3-2. 부서별 퇴사 리스크 분석 (옵션 A: 전년 대비 + 절대 규모 혼합 스코어)
def analyze_department_turnover(df_turnover, show_table=True):
    text_blocks = []

    df = df_turnover.copy()
    df = df.sort_values("연도")

    years = sorted(df["연도"].unique())
    if len(years) < 2:
        return "📌 전년 대비 분석을 할 수 있을 만큼 연도 데이터가 충분하지 않습니다. (모르겠습니다)", None

    last_year = years[-1]   # 최신 연도
    prev_year = years[-2]   # 직전 연도

    recent_df = df[df["연도"] == last_year]
    prev_df = df[df["연도"] == prev_year]

    dept_cols = [c for c in df.columns if c != "연도"]

    # 올해 전체 부서 퇴사자수 평균 (절대 규모 기준)
    total_this_year = []
    for col in dept_cols:
        total_this_year.append(recent_df[col].sum())
    overall_avg_this_year = np.mean(total_this_year) if len(total_this_year) > 0 else np.nan

    risk_rows = []
    for col in dept_cols:
        this_year_val = recent_df[col].sum()
        prev_year_val = prev_df[col].sum()

        # 1) 전년 대비 스코어
        if prev_year_val == 0:
            yoy_score = np.nan
        else:
            yoy_score = this_year_val / prev_year_val

        # 2) 절대 규모 스코어 (올해 전체 평균 대비)
        if overall_avg_this_year == 0 or np.isnan(overall_avg_this_year):
            abs_score = np.nan
        else:
            abs_score = this_year_val / overall_avg_this_year

        # 3) 최종 리스크 스코어 (혼합)
        if np.isnan(yoy_score) and not np.isnan(abs_score):
            final_score = abs_score
        elif np.isnan(abs_score) and not np.isnan(yoy_score):
            final_score = yoy_score
        elif np.isnan(yoy_score) and np.isnan(abs_score):
            final_score = np.nan
        else:
            final_score = 0.5 * yoy_score + 0.5 * abs_score

        risk_rows.append((col, this_year_val, prev_year_val, yoy_score, abs_score, final_score))

    risk_df = pd.DataFrame(
        risk_rows,
        columns=[
            "부서",
            f"{last_year}년_퇴사자수",
            f"{prev_year}년_퇴사자수",
            "전년대비스코어",
            "절대규모스코어",
            "최종리스크스코어"
        ]
    ).sort_values("최종리스크스코어", ascending=False)

    # 기본 등급은 Low
    risk_df["리스크등급"] = "Low"

    # 최종 리스크 스코어가 1.2 이상인 부서들 중 상위 2개를 High로 설정
    candidates = risk_df[risk_df["최종리스크스코어"] >= 1.2].copy()
    top_high = candidates.head(2).index
    risk_df.loc[top_high, "리스크등급"] = "High"

    # 나머지 중에서 1.0 이상 1.2 미만은 Medium
    medium_mask = (risk_df["리스크등급"] == "Low") & (risk_df["최종리스크스코어"] >= 1.0)
    risk_df.loc[medium_mask, "리스크등급"] = "Medium"

    # 표 표시 여부
    if show_table:
        st.dataframe(
            risk_df.style.format(
                {
                    f"{last_year}년_퇴사자수": "{:.0f}",
                    f"{prev_year}년_퇴사자수": "{:.0f}",
                    "전년대비스코어": "{:.2f}",
                    "절대규모스코어": "{:.2f}",
                    "최종리스크스코어": "{:.2f}",
                }
            ),
            use_container_width=True
        )

    # 인사이트 코멘트
    high_risk = risk_df[risk_df["리스크등급"] == "High"]
    medium_risk = risk_df[risk_df["리스크등급"] == "Medium"]

    if not high_risk.empty:
        dept_list = ", ".join(
            f"{row.부서}팀("
            f"{last_year}년 {row[f'{last_year}년_퇴사자수']:.0f}명, "
            f"{prev_year}년 대비 {row['전년대비스코어']:.2f}배, "
            f"절대규모스코어 {row['절대규모스코어']:.2f}, "
            f"최종 {row['최종리스크스코어']:.2f})"
            for _, row in high_risk.iterrows()
        )
        text_blocks.append(
            f"🔴 **High Risk 부서 인사이트 (전년 대비 + 절대 규모)**\n"
            f"{dept_list} 에서 전년 대비 증가 폭과 절대 퇴사 규모가 모두 높은 편입니다. "
            f"조직문화, 리더십, 역할적합성, 보상 등 원인 진단이 필요합니다. (추측입니다)"
        )
    else:
        text_blocks.append(
            "🔴 **High Risk 부서 인사이트 (전년 대비 + 절대 규모)**\n"
            "현재 기준으로 전년 대비 증가 폭과 절대 규모를 함께 보았을 때, "
            "강하게 경고가 필요한 부서는 없습니다."
        )

    if not medium_risk.empty:
        dept_list = ", ".join(
            f"{row.부서}팀("
            f"{last_year}년 {row[f'{last_year}년_퇴사자수']:.0f}명, "
            f"{prev_year}년 대비 {row['전년대비스코어']:.2f}배, "
            f"절대규모스코어 {row['절대규모스코어']:.2f}, "
            f"최종 {row['최종리스크스코어']:.2f})"
            for _, row in medium_risk.iterrows()
        )
        text_blocks.append(
            f"🟠 **Medium Risk 부서 인사이트 (전년 대비 + 절대 규모)**\n"
            f"{dept_list} 수준으로, 앞으로의 추이를 모니터링하면서 "
            f"퇴사 사유와 패턴을 주기적으로 확인하는 것이 좋습니다. (추측입니다)"
        )
    else:
        text_blocks.append(
            "🟠 **Medium Risk 부서 인사이트 (전년 대비 + 절대 규모)**\n"
            "전년 대비 증가 폭과 절대 규모를 함께 보았을 때, "
            "중간 수준의 주의가 필요한 부서는 아직 뚜렷하지 않습니다."
        )

    low_count = (risk_df["리스크등급"] == "Low").sum()
    text_blocks.append(
        f"🟢 **Low Risk 부서 인사이트**\n"
        f"전년과 유사하거나 더 낮은 수준(또는 규모가 상대적으로 작은 수준)의 부서는 총 **{low_count}개**입니다."
    )

    return "\n\n".join(text_blocks), risk_df

# 3-3. 잔존율 분석 (입사연도별 그룹 관점, 표 표시 옵션)
def analyze_retention(df_retention, show_table=True):
    text_blocks = []

    df = df_retention.copy()

    pivot_12 = df[df["경과개월"] == 12].copy()
    if pivot_12.empty:
        text_blocks.append("📌 12개월 잔존율 데이터가 없어 입사연도별 그룹 비교는 어렵습니다. (모르겠습니다)")
    else:
        worst = pivot_12.sort_values("잔존율").iloc[0]
        best = pivot_12.sort_values("잔존율", ascending=False).iloc[0]
        text_blocks.append(
            "🔹 **12개월 잔존율 기준 입사연도별 그룹 비교 인사이트**\n"
            f"- 최저 잔존율: **{int(worst['입사연도'])}년 입사 그룹** ({worst['잔존율']:.1f}%)\n"
            f"- 최고 잔존율: **{int(best['입사연도'])}년 입사 그룹** ({best['잔존율']:.1f}%)\n"
            "→ 특정 입사연도 그룹에서 온보딩, 배치, 조직적합성 등 경험의 질이 달랐을 가능성이 있습니다. (추측입니다)"
        )

    drops = []
    for year, g in df.groupby("입사연도"):
        g = g.sort_values("경과개월")
        g["change"] = g["잔존율"].diff()
        big_drop = g[g["change"] <= -10]
        for _, row in big_drop.iterrows():
            drops.append(
                (
                    year,
                    int(row["경과개월"]),
                    row["change"]
                )
            )

    if drops:
        drops_df = pd.DataFrame(drops, columns=["입사연도", "경과개월", "변화량"])
        drops_df = drops_df.sort_values("변화량")

        if show_table:
            st.dataframe(
    drops_df.reset_index(drop=True),
    use_container_width=True
)


        example = drops_df.iloc[0]
        text_blocks.append(
            "🔹 **입사연도별 그룹의 잔존율 급락 구간 인사이트**\n"
            f"- 예: {int(example['입사연도'])}년 입사 그룹의 "
            f"{int(example['경과개월'])}개월 시점에서 잔존율이 **{example['변화량']:.1f}p** 급락했습니다.\n"
            "→ 해당 시점 전후의 평가, 조직개편, 리더 변경, 보상 이벤트 등을 함께 검토하는 것이 좋습니다. (추측입니다)"
        )
    else:
        text_blocks.append(
            "🔹 **입사연도별 그룹의 잔존율 급락 구간 인사이트**\n"
            "연속 구간에서 -10%p 이상 급락한 패턴은 뚜렷하게 나타나지 않습니다."
        )

    return "\n\n".join(text_blocks)

# 3-4. 입사연도별 잔존율 라인 그래프용 데이터
def make_retention_line_data(df_retention):
    df = df_retention.copy()
    line_df = df.pivot_table(
        index="경과개월",
        columns="입사연도",
        values="잔존율",
        aggfunc="mean"
    ).sort_index()
    return line_df

# 3-5. 액션 포인트 생성
def generate_action_points(headcount_comment, risk_df, retention_comment):
    points = []

    if risk_df is not None:
        high_risk = risk_df[risk_df["리스크등급"] == "High"]
        if not high_risk.empty:
            dept_names = ", ".join(high_risk["부서"].tolist())
            points.append(
                f"1) **High Risk 부서 집중 진단 제안 (전년 대비 + 절대 규모)**\n"
                f"- 대상: {dept_names}\n"
                f"- 액션: 퇴사자 인터뷰, 조직문화/리더십 진단, 역할·성과 기대치 명확화 워크숍 등을 우선 검토합니다. (추측입니다)"
            )
        else:
            points.append(
                "1) **High Risk 부서 집중 진단 제안 (전년 대비 + 절대 규모)**\n"
                "- 현재 기준으로 High Risk에 해당하는 부서는 없지만, "
                "퇴사 증가 신호가 나타날 경우 신속히 집중 진단을 진행할 수 있도록 준비하는 것이 좋습니다. (추측입니다)"
            )

    points.append(
        "2) **입사연도별 그룹 잔존율 격차 관리 제안**\n"
        "- 잔존율이 낮은 입사연도 그룹을 중심으로, 초기 온보딩/배치/피드백 구조를 점검하고 "
        "동일 시기에 입사한 구성원들의 공통 경험을 인터뷰로 수집하는 것을 권장합니다. (추측입니다)"
    )

    points.append(
        "3) **잔존율 급락 시점 재점검 제안**\n"
        "- 잔존율이 특정 시점 이후 크게 떨어지는 경우, 그 전후로 있었던 평가, 조직개편, 리더 변경, "
        "보상/성과 제도 변경 등 조직 이벤트를 함께 확인하고, 커뮤니케이션 및 제도 보완 방안을 마련하는 것이 좋습니다. (추측입니다)"
    )

    points.append(
        "4) **입·퇴사 및 총원 추세 기반 채용/운영 전략 조정 제안**\n"
        "- 퇴사 증가가 감지되는 시점에는 단기적인 충원 계획뿐 아니라, "
        "이탈 사유를 체계적으로 수집·분석하여 중장기적인 구조 개선 방향까지 함께 검토하는 것이 중요합니다. (추측입니다)"
    )

    return "\n\n".join(points)

# =========================================
# 4. 메인 화면 구성
# =========================================
try:
    df_change, df_turnover, df_retention, df_tenure = load_data()
    data_loaded = True
except FileNotFoundError:
    st.error("`company_hr_data.xlsx` 파일을 찾을 수 없습니다. app.py와 같은 폴더에 있는지 확인해주세요.")
    data_loaded = False
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    data_loaded = False

if not data_loaded:
    st.stop()

# 👉 사이드바는 페이지 선택만 간결하게
menu = st.sidebar.radio(
    "페이지 선택",
    ["1. 조직 현황 스냅샷", "2. 리텐션 분석", "3. 액션 포인트"]
)

# -------------------------------------
# 페이지 1: 조직 현황 스냅샷
# -------------------------------------
if menu.startswith("1"):
    st.subheader("📍 페이지 1 — 조직 현황 스냅샷")

    df_change_view = df_change.copy()
    df_change_view["월"] = to_month_period(df_change_view["월"])
    df_change_view = df_change_view.sort_values("월")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**월별 입·퇴사 추이**")
        st.line_chart(
            df_change_view.set_index("월")[["입사자", "퇴사자"]]
        )

    with col2:
        st.markdown("**월별 총원 추세**")
        st.line_chart(
            df_change_view.set_index("월")[["총원"]]
        )

    st.markdown("---")
    st.markdown("### 🧠 인사이트 코멘트")

    headcount_comment = analyze_headcount(df_change)
    st.markdown(headcount_comment)

# -------------------------------------
# 페이지 2: 리텐션 분석
# -------------------------------------
elif menu.startswith("2"):
    st.subheader("📍 페이지 2 — 리텐션 분석")

    st.markdown("#### 🔥 부서별 퇴사자 수 (연도×부서)")
    turnover_melt = df_turnover.melt(id_vars=["연도"], var_name="부서", value_name="퇴사자수")
    turnover_pivot = turnover_melt.pivot(index="연도", columns="부서", values="퇴사자수")
    st.dataframe(turnover_pivot, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🧠 부서별 인사이트 코멘트 (전년 대비 + 절대 규모)")
    dept_comment, risk_df = analyze_department_turnover(df_turnover, show_table=True)
    st.markdown(dept_comment)

    st.markdown("---")
    st.markdown("### 📈 입사연도별 잔존율 추이 (그룹별 라인 그래프)")
    retention_line_df = make_retention_line_data(df_retention)
    st.line_chart(retention_line_df)

    st.markdown("---")
    st.markdown("### 🧠 잔존율 인사이트 코멘트 (입사연도별 그룹 관점)")
    retention_comment = analyze_retention(df_retention, show_table=True)
    st.markdown(retention_comment)

# -------------------------------------
# 페이지 3: 액션 포인트
# -------------------------------------
elif menu.startswith("3"):
    st.subheader("📍 페이지 3 — 액션 포인트")

    headcount_comment = analyze_headcount(df_change)
    dept_comment, risk_df = analyze_department_turnover(df_turnover, show_table=False)
    retention_comment = analyze_retention(df_retention, show_table=False)

    st.markdown("### 🧠 요약 인사이트")
    if "🔹 **종합 인사이트**" in headcount_comment:
        summary_part = headcount_comment.split("🔹 **종합 인사이트**")[-1]
        st.markdown("**조직 현황 종합 인사이트**" + summary_part)
    else:
        st.markdown(headcount_comment)

    st.markdown("---")
    st.markdown("### ✅ HR 액션 포인트 제안")

    action_points = generate_action_points(
        headcount_comment, risk_df, retention_comment
    )
    st.markdown(action_points)



