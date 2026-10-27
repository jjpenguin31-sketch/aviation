
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="연도별 항공사고 통계",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ 연도별 항공사고 발생현황 통계")
st.write("국토교통부 연도별 항공사고 통계 자료를 분석합니다.")

FILE_NAME = "국토교통부_연도별 항공사고 발생현황 통계_20251231.csv"

@st.cache_data
def load_data():
    for encoding in ["utf-8-sig", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(FILE_NAME, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(FILE_NAME)

try:
    df = load_data()
    df.columns = df.columns.str.strip()

    st.success("항공사고 통계 데이터를 불러왔습니다.")

    st.subheader("원본 통계 자료")
    st.dataframe(df, use_container_width=True)

    year_col = next(
        (c for c in df.columns if c in ["년도", "연도", "발생년도", "발생연도"]),
        None
    )
    count_col = next(
        (c for c in df.columns if c in ["발생건수", "사고건수", "건수"]),
        None
    )

    if year_col and count_col:
        df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
        df[count_col] = pd.to_numeric(
            df[count_col].astype(str).str.replace(",", ""),
            errors="coerce"
        )

        chart_df = df.dropna(subset=[year_col, count_col]).copy()
        chart_df[year_col] = chart_df[year_col].astype(int)
        chart_df = chart_df.sort_values(year_col)

        if not chart_df.empty:
            st.subheader("연도별 항공사고 발생 건수")

            years = sorted(chart_df[year_col].unique())
            selected_years = st.slider(
                "조회할 연도 범위",
                min_value=int(min(years)),
                max_value=int(max(years)),
                value=(int(min(years)), int(max(years)))
            )

            filtered = chart_df[
                chart_df[year_col].between(*selected_years)
            ]

            total = filtered[count_col].sum()
            c1, c2 = st.columns(2)
            c1.metric("조회 기간", f"{selected_years[0]}~{selected_years[1]}년")
            c2.metric("발생 건수 합계", f"{total:,.0f}건")

            fig = px.bar(
                filtered,
                x=year_col,
                y=count_col,
                labels={
                    year_col: "연도",
                    count_col: "발생 건수"
                },
                title="연도별 항공사고 발생 현황",
                text=count_col
            )
            fig.update_layout(xaxis=dict(dtick=1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("연도와 발생 건수 데이터를 확인해 주세요.")
    else:
        st.warning(
            "연도 또는 발생 건수 열을 자동으로 찾지 못했습니다. "
            "위 원본 통계 자료에서 실제 열 이름을 확인해 주세요."
        )

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. GitHub 저장소의 파일 이름을 확인해 주세요.")
except Exception as e:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
