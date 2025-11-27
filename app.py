import streamlit as st
import pandas as pd

# ============================================
# 기본 설정
# ============================================

st.title("HR 분석 대시보드 - 그룹 1: 조직 현황 및 인력 변동")

st.write("""
이 대시보드는 회사 HR 데이터를 기반으로  
입·퇴사, 퇴사율, 잔존율, 근속, 휴가 사용 패턴을 시각화합니다.

엑셀 파일 구조(가정):
- 파일명: company_hr_data.xlsx  (app.py와 같은 폴더)
- 시트: 인원변동 / 퇴사율 / 잔존율 / 근속 / 휴가패턴
""")

EXCEL_FILE = "company_hr_data.xlsx"


# ============================================
# 공통: 엑셀 컬럼 구조 디버그용 함수
# ============================================

def show_columns_debug(df, sheet_name: str):
    """엑셀에서 읽어온 컬럼명을 화면에 보여주는 디버그용."""
    st.caption(f"ⓘ '{sheet_name}' 시트에서 읽은 컬럼: {list(df.columns)}")


# ============================================
# 1) 기본 인원 변동 현황
#    시트: 인원변동
#    열: 월 / 입사자 / 퇴사자 / 총원
# ============================================

st.header("1) 기본 인원 변동 현황 (입·퇴사 + 총원)")

try:
    flow_df = pd.read_excel(EXCEL_FILE, sheet_name="인원변동")
    st.write("▶ 인원변동 데이터 (엑셀에서 불러옴)")
    st.dataframe(flow_df)

    if flow_df.empty:
        st.warning("❗ '인원변동' 시트에 데이터가 없습니다. 월 / 입사자 / 퇴사자 / 총원 데이터를 입력해주세요.")
        show_columns_debug(flow_df, "인원변동")
    else:
        expected_cols = ["월", "입사자", "퇴사자", "총원"]
        missing = [c for c in expected_cols if c not in flow_df.columns]
        if missing:
            st.error(f"'인원변동' 시트에 다음 컬럼이 없습니다: {missing}")
            show_columns_debug(flow_df, "인원변동")
        else:
            flow_indexed = flow_df.set_index("월")

            st.write("▶ 입사자 / 퇴사자 (막대차트)")
            st.bar_chart(
                data=flow_indexed[["입사자", "퇴사자"]]
            )

            st.write("▶ 총원 (라인차트)")
            st.line_chart(
                data=flow_indexed[["총원"]]
            )

except FileNotFoundError:
    st.error("❗ company_hr_data.xlsx 파일을 찾을 수 없습니다. hr_dashboard 폴더 안에 엑셀 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error("인원변동 시트에서 데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)


# ============================================
# 2) 연간 퇴사율 (전체 vs 실 비교)
#    시트: 퇴사율
#    열: 연도 / 전체 / 경영기획실 / 프로그램실 / 아트실 / 게임디자인실 / 라이브지원실 / 시네마실
# ============================================

st.header("2) 연간 퇴사율 (전체 평균 vs 실 비교)")

try:
    turnover_df = pd.read_excel(EXCEL_FILE, sheet_name="퇴사율")
    st.write("▶ 퇴사율 데이터 (엑셀에서 불러옴)")
    st.dataframe(turnover_df)

    if turnover_df.empty:
        st.warning("❗ '퇴사율' 시트에 데이터가 없습니다. 연도 / 전체 / 실별 퇴사율 데이터를 입력해주세요.")
        show_columns_debug(turnover_df, "퇴사율")
    else:
        year_col = "연도"
        base_col = "전체"

        if year_col not in turnover_df.columns or base_col not in turnover_df.columns:
            st.error(f"'퇴사율' 시트에 '연도' 또는 '전체' 컬럼이 없습니다.")
            show_columns_debug(turnover_df, "퇴사율")
        else:
            all_cols = list(turnover_df.columns)
            group_cols = [c for c in all_cols if c not in [year_col, base_col]]

            if not group_cols:
                st.warning("비교할 실(부서) 컬럼이 없습니다. '퇴사율' 시트에 실(부서)별 컬럼을 추가해주세요.")
                show_columns_debug(turnover_df, "퇴사율")
            else:
                선택_실 = st.selectbox(
                    "비교할 실(부서)을 선택하세요",
                    group_cols,
                    index=0
                )

                chart_df = turnover_df.set_index(year_col)[[base_col, 선택_실]]

                st.write(f"▶ 전체 vs {선택_실} 연간 퇴사율")
                st.line_chart(chart_df)

except FileNotFoundError:
    st.error("❗ company_hr_data.xlsx 파일을 찾을 수 없습니다. hr_dashboard 폴더 안에 엑셀 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error("퇴사율 시트에서 데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)


# ============================================
# 3) 입사 연도별 잔존율 (코호트)
#    시트: 잔존율
#    열: 입사연도 / 경과개월 / 잔존율(%)
# ============================================

st.header("3) 입사 연도별 잔존율 (코호트 분석)")

try:
    cohort_df = pd.read_excel(EXCEL_FILE, sheet_name="잔존율")
    st.write("▶ 잔존율 데이터 (엑셀에서 불러옴)")
    st.dataframe(cohort_df)

    if cohort_df.empty:
        st.warning("❗ '잔존율' 시트에 데이터가 없습니다. 입사연도 / 경과개월 / 잔존율(%) 데이터를 입력해주세요.")
        show_columns_debug(cohort_df, "잔존율")
    else:
        hire_year_col = "입사연도"
        month_col = "경과개월"
        rate_col = "잔존율(%)"

        missing = [c for c in [hire_year_col, month_col, rate_col] if c not in cohort_df.columns]
        if missing:
            st.error(f"'잔존율' 시트에 다음 컬럼이 없습니다: {missing}")
            show_columns_debug(cohort_df, "잔존율")
        else:
            for year in cohort_df[hire_year_col].unique():
                sub = (
                    cohort_df[cohort_df[hire_year_col] == year]
                    .sort_values(by=month_col)
                    .set_index(month_col)[[rate_col]]
                )
                st.line_chart(sub, height=200)
                st.caption(f"• {year}년 입사 코호트 잔존율 추이")

except FileNotFoundError:
    st.error("❗ company_hr_data.xlsx 파일을 찾을 수 없습니다. hr_dashboard 폴더 안에 엑셀 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error("잔존율 시트에서 데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)


# ============================================
# 4) 인력 유지 현황 (평균 근속년수 비교)
#    시트: 근속
#    열: 구분 / 근속년수
# ============================================

st.header("4) 인력 유지 현황 (평균 근속년수 비교)")

try:
    tenure_df = pd.read_excel(EXCEL_FILE, sheet_name="근속")
    st.write("▶ 근속 데이터 (엑셀에서 불러옴)")
    st.dataframe(tenure_df)

    if tenure_df.empty:
        st.warning("❗ '근속' 시트에 데이터가 없습니다. 구분 / 근속년수 데이터를 입력해주세요.")
        show_columns_debug(tenure_df, "근속")
    else:
        expected_cols = ["구분", "근속년수"]
        missing = [c for c in expected_cols if c not in tenure_df.columns]
        if missing:
            st.error(f"'근속' 시트에 다음 컬럼이 없습니다: {missing}")
            show_columns_debug(tenure_df, "근속")
        else:
            st.write("▶ 재직자 vs 퇴사자 평균 근속 비교")
            st.bar_chart(
                data=tenure_df.set_index("구분")
            )

except FileNotFoundError:
    st.error("❗ company_hr_data.xlsx 파일을 찾을 수 없습니다. hr_dashboard 폴더 안에 엑셀 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error("근속 시트에서 데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)


# ============================================
# 5) 퇴사 예측 선행 지표 (휴가 사용 패턴)
#    시트: 휴가패턴
#    열: 월 / 재직자 평균 휴가일 / 퇴사자 평균 휴가일
# ============================================

st.header("5) 퇴사 예측 선행 지표 (휴가 사용 패턴)")

try:
    leave_df = pd.read_excel(EXCEL_FILE, sheet_name="휴가패턴")
    st.write("▶ 휴가 사용 패턴 데이터 (엑셀에서 불러옴)")
    st.dataframe(leave_df)

    if leave_df.empty:
        st.warning("❗ '휴가패턴' 시트에 데이터가 없습니다. 월 / 재직자 평균 휴가일 / 퇴사자 평균 휴가일 데이터를 입력해주세요.")
        show_columns_debug(leave_df, "휴가패턴")
    else:
        expected_cols = ["월", "재직자 평균 휴가일", "퇴사자 평균 휴가일"]
        missing = [c for c in expected_cols if c not in leave_df.columns]
        if missing:
            st.error(f"'휴가패턴' 시트에 다음 컬럼이 없습니다: {missing}")
            show_columns_debug(leave_df, "휴가패턴")
        else:
            leave_indexed = leave_df.set_index("월")

            st.write("▶ 휴가 사용 패턴 라인차트")
            st.line_chart(
                data=leave_indexed[["재직자 평균 휴가일", "퇴사자 평균 휴가일"]]
            )

except FileNotFoundError:
    st.error("❗ company_hr_data.xlsx 파일을 찾을 수 없습니다. hr_dashboard 폴더 안에 엑셀 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error("휴가패턴 시트에서 데이터를 불러오는 중 오류가 발생했습니다.")
    st.write(e)

st.success("엑셀 기반 HR 대시보드 (그룹 1) 구성이 완료되었습니다. 엑셀 내용만 바꾸면 그래프도 함께 바뀝니다 😊")
