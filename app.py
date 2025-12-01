import streamlit as st
import pandas as pd

# ------------------------------------------------
# 기본 설정
# ------------------------------------------------
st.set_page_config(
    page_title="HR 대시보드 - 조직 현황 및 인력 변동",
    layout="wide"
)

# 엑셀 파일 이름 (파일명이 다르면 여기만 변경)
EXCEL_FILE = "company_hr_data.xlsx"


# ------------------------------------------------
# 공통: 시트 로드 함수
# ------------------------------------------------
def load_sheet(sheet_name: str):
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        if df is None or df.empty:
            st.warning(f"'{sheet_name}' 시트에 데이터가 없습니다.")
            return None
        return df
    except Exception as e:
        st.error(f"'{sheet_name}' 시트를 불러오는 중 오류가 발생했습니다.")
        st.write(e)
        return None


# 1번~4번 시트 로드
flow_df   = load_sheet("인원변동")   # 1) 인원 변동
turn_df   = load_sheet("퇴사율")     # 2) 퇴사율
cohort_df = load_sheet("잔존율")     # 3) 잔존율
tenure_df = load_sheet("근속")       # 4) 근속


# ------------------------------------------------
# 화면 상단 설명
# ------------------------------------------------
st.title("HR 분석 대시보드 - 그룹 : 조직 현황 및 인력 변동")

st.write(
    """
이 화면은 하나의 페이지에서 **인원 변동 / 퇴사율 / 잔존율 / 근속**을  
순서대로 내려가며 볼 수 있도록 구성했습니다.  
표는 최소화하고, **그래프와 핵심 숫자 중심**으로 정리했습니다.
"""
)

st.markdown("---")

# =================================================
# 1) 인원 변동 현황 (입사자 / 퇴사자 / 총원)
#    시트: 인원변동
#    열: 월 / 입사자 / 퇴사자 / 총원
# =================================================
st.header("1) 인원 변동 현황 (입사자 / 퇴사자 / 총원)")

if flow_df is not None:
    df = flow_df.copy()

    expected_cols = ["월", "입사자", "퇴사자", "총원"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        st.error(f"'인원변동' 시트에 다음 컬럼이 없습니다: {missing}")
    else:
        # 숫자 컬럼은 숫자로 변환 (문자/빈칸은 NaN 처리)
        for col in ["입사자", "퇴사자", "총원"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 월 정렬 (가능하면 날짜로, 아니면 원본 순서)
        try:
            df["월_정렬"] = pd.to_datetime(df["월"])
            df = df.sort_values("월_정렬")
        except Exception:
            df["월_정렬"] = df["월"]

        latest = df.iloc[-1]

        # NaN(빈 값)을 안전하게 처리해서 표시용 텍스트로 변환
        headcount_raw = latest["총원"]
        hire_raw = latest["입사자"]
        term_raw = latest["퇴사자"]

        headcount_display = "데이터 없음" if pd.isna(headcount_raw) else f"{int(headcount_raw)}명"
        if pd.isna(hire_raw) or pd.isna(term_raw):
            hire_term_display = "데이터 없음"
        else:
            hire_term_display = f"{int(hire_raw)}명 / {int(term_raw)}명"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("마지막 기준 월", str(latest["월"]))
        with col2:
            st.metric("마지막 월 총원", headcount_display)
        with col3:
            st.metric("마지막 월 입사 / 퇴사", hire_term_display)

        # 그래프: 월별 입사자 / 퇴사자
        st.subheader("월별 입사자 / 퇴사자")
        chart_flow = df.set_index("월")[["입사자", "퇴사자"]]
        st.bar_chart(chart_flow)

        # 그래프: 월별 총원
        st.subheader("월별 총원 추이")
        chart_headcount = df.set_index("월")[["총원"]]
        st.line_chart(chart_headcount)

        # 원본 데이터는 접어서 보기
        with st.expander("인원변동 원본 데이터 보기"):
            st.dataframe(df[["월", "입사자", "퇴사자", "총원"]])

st.markdown("---")

# =================================================
# 2) 퇴사율 (연도 / 전체 / 아트 / 기획 / 개발지원 / 사업 / 프로그램 / staff)
#    시트: 퇴사율
# =================================================
st.header("2) 연간 퇴사율 (전체 vs 부서 비교)")

if turn_df is not None:
    df = turn_df.copy()

    expected_cols = ["연도", "전체", "아트", "기획", "개발지원", "사업", "프로그램", "staff"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        st.error(f"'퇴사율' 시트에 다음 컬럼이 없습니다: {missing}")
    else:
        # 숫자 컬럼 변환
        for col in expected_cols:
            if col != "연도":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.sort_values("연도")

        latest = df.iloc[-1]
        latest_year = latest["연도"]
        latest_total = latest["전체"]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("마지막 연도", str(latest_year))
        with col2:
            if pd.isna(latest_total):
                st.metric("마지막 연도 전체 퇴사율(%)", "데이터 없음")
            else:
                st.metric("마지막 연도 전체 퇴사율(%)", f"{latest_total}")

        # 비교 대상 부서 선택
        dept_cols = ["아트", "기획", "개발지원", "사업", "프로그램", "staff"]
        선택_부서 = st.selectbox("비교할 부서를 선택하세요", dept_cols)

        chart_df = df.set_index("연도")[["전체", 선택_부서]]

        st.subheader(f"전체 vs {선택_부서} 연간 퇴사율 추이")
        st.line_chart(chart_df)

        with st.expander("퇴사율 원본 데이터 보기"):
            st.dataframe(df)

st.markdown("---")

# =================================================
# 3) 잔존율 (입사연도 / 경과개월 / 잔존율)
#    시트: 잔존율
# =================================================
st.header("3) 입사 연도별 잔존율 (코호트 분석)")

if cohort_df is not None:
    df = cohort_df.copy()

    expected_cols = ["입사연도", "경과개월", "잔존율"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        st.error(f"'잔존율' 시트에 다음 컬럼이 없습니다: {missing}")
    else:
        # 숫자 변환
        df["입사연도"] = pd.to_numeric(df["입사연도"], errors="coerce")
        df["경과개월"] = pd.to_numeric(df["경과개월"], errors="coerce")
        df["잔존율"]   = pd.to_numeric(df["잔존율"], errors="coerce")

        df = df.dropna(subset=["입사연도", "경과개월", "잔존율"])
        df = df.sort_values(["입사연도", "경과개월"])

        years = sorted(df["입사연도"].unique())
        if len(years) == 0:
            st.warning("잔존율 데이터에 유효한 입사연도가 없습니다.")
        else:
            선택_연도 = st.multiselect(
                "보고 싶은 입사연도를 선택하세요",
                years,
                default=years
            )

            for y in 선택_연도:
                sub = df[df["입사연도"] == y].set_index("경과개월")[["잔존율"]]
                st.subheader(f"{int(y)}년 입사 코호트 잔존율")
                st.line_chart(sub)
                st.caption(f"- {int(y)}년 입사자 기준, 경과 개월별 잔존율(%)")

            with st.expander("잔존율 원본 데이터 보기"):
                st.dataframe(df)

st.markdown("---")

# =================================================
# 4) 근속 (구분 / 근속년수)
#    시트: 근속
# =================================================
st.header("4) 인력 유지 현황 (재직자 vs 퇴사자 평균 근속년수)")

if tenure_df is not None:
    df = tenure_df.copy()

    expected_cols = ["구분", "근속년수"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        st.error(f"'근속' 시트에 다음 컬럼이 없습니다: {missing}")
    else:
        df["근속년수"] = pd.to_numeric(df["근속년수"], errors="coerce")

        col1, col2 = st.columns(2)

        재직자 = df[df["구분"].str.contains("재직", na=False)].head(1)
        퇴사자 = df[df["구분"].str.contains("퇴사", na=False)].head(1)

        with col1:
            if not 재직자.empty and not pd.isna(재직자.iloc[0]["근속년수"]):
                st.metric(
                    "재직자 평균 근속(년)",
                    f"{재직자.iloc[0]['근속년수']:.2f} 년"
                )
            else:
                st.metric("재직자 평균 근속(년)", "데이터 없음")

        with col2:
            if not 퇴사자.empty and not pd.isna(퇴사자.iloc[0]["근속년수"]):
                st.metric(
                    "퇴사자 평균 근속(년)",
                    f"{퇴사자.iloc[0]['근속년수']:.2f} 년"
                )
            else:
                st.metric("퇴사자 평균 근속(년)", "데이터 없음")

        st.subheader("평균 근속년수 비교")
        try:
            st.bar_chart(df.set_index("구분")[["근속년수"]])
        except Exception:
            st.warning("근속년수 차트를 그리는 중 문제가 발생했습니다. 데이터 형태를 확인해주세요.")

        with st.expander("근속 원본 데이터 보기"):
            st.dataframe(df)

st.success("엑셀 시트 구조에 맞춘 단일 페이지 HR 대시보드 구성이 완료되었습니다.")
