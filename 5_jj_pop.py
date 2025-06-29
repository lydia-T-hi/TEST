from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import platform
from matplotlib import rc

## 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 깃허브 리눅스 기준
if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    font_files = fm.findSystemFonts(fontpaths=fontname)
    fm.fontManager.addfont(fontname)
    fm._load_fontmanager(try_read_cache=False)
    rc('font', family='NanumGothic')
st.set_page_config(page_title="우리 동네 인구 구조 시각화")

# ───── 사이드바 메뉴 ─────
with st.sidebar:
    selected = option_menu(
        menu_title="우리 동네 인구 구조 시각화하기",
        options=[
            "데이터 불러오기 및 전처리",
            "전체 연령대 인구 분포",  
            "행정구역별 총인구 Top 10",
            "지역별 연령대 인구 분포",
            "지역별 성별 인구 피라미드",
            "인구 지표 분석 - 고령화 지수", 
            "인구 지표 분석 - 연령대별 성비"
        ],
        icons=[
            "file-earmark-arrow-up",            
            "graph-up-arrow",
            "people",            
            "graph-up",
            "gender-ambiguous",
            "activity",
            "gender-female"
        ],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "black", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0",
                "color": "black",
                "padding": "6px 14px"
            },
            "nav-link-selected": {
                "color": "#FF4B4B",
                "background-color": "transparent"
            }
        }
    )

# ───── 본문 처리 ─────
st.title("📍 우리 동네 인구 구조 시각화 ")

# 실제 기능 메뉴들
if selected == "데이터 불러오기 및 전처리":
    st.subheader("📁 데이터 불러오기")

    # 업로더를 오른쪽 본문에 표시
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    # 데이터 불러오기
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='cp949', thousands=',')
        st.session_state.df = df
        st.success("✅ 데이터 업로드 완료!")
        st.dataframe(df, use_container_width=True)

elif selected == "행정구역별 총인구 Top 10":
    st.subheader("👥 행정구역별 총인구 Top 10")

    if st.session_state.df is None:
        st.error("먼저 데이터를 업로드해주세요.")
    else:
        df = st.session_state.df.copy()        
        # '동' 포함 필터링 및 총 인구 계산
        df_filtered = df[df['행정구역'].str.contains("동")].copy()
        df_filtered['총인구'] = df_filtered.iloc[:, 3:104].sum(axis=1)

        # 상위 10개 동 추출
        top_total = df_filtered[['행정구역', '총인구']].sort_values(by='총인구', ascending=False).head(10)

        # 시각화
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        ax.barh(top_total['행정구역'], top_total['총인구'], color='steelblue')
        ax.set_xlabel("총 인구수")
        ax.set_title("전주시 내 총 인구 상위 동 Top 10")
        ax.invert_yaxis()
        fig.tight_layout()  # 여백 조정
        st.pyplot(fig, bbox_inches='tight')
        st.caption("※ 0세부터 100세까지의 인구 합계를 기준으로 상위 10개 동을 시각화하였습니다.")

elif selected == "전체 연령대 인구 분포":
    st.subheader("👶 전체 연령대 인구 분포")
    
    if st.session_state.get("df") is None:
        st.error("먼저 데이터를 업로드해주세요.")
    else:
        df = st.session_state.df.copy()        
        result = df.iloc[0][3:104]
       
        # 시각화
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(result.index, result.values, color='blue', linewidth=2)
        ax.set_title("전주시 인구 그래프", fontsize=16)
        ax.set_xlabel("나이")
        plt.xticks([i for i in range(0,101,10)], rotation=80)
        st.pyplot(fig)
        st.caption("※ 전주시 전체 인구의 연령별 분포를 시각화한 그래프입니다.")

elif selected == "지역별 연령대 인구 분포":
    st.subheader("👥 지역별 연령대 인구 분포")

    if st.session_state.get("df") is None:
        st.error("먼저 데이터를 업로드해주세요.")
    else:
        df1 = st.session_state.df.copy()

        # '동'만 포함된 행정구역 필터링
        dong_list = df1[df1['행정구역'].str.contains("동")]['행정구역'].unique()
        selected_dong_list = st.multiselect("동을 선택하세요", dong_list)

        if selected_dong_list:
            matched_rows = df1[df1['행정구역'].isin(selected_dong_list)]
            
            result = matched_rows.iloc[:, 3:104]

            fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

            for i in result.index:
                values = result.loc[i].values.astype(float)
                if not (pd.isna(values).all() or (values == 0).all()):
                    ax.plot(range(0, 101), values, label=matched_rows.loc[i, '행정구역'])

            ax.set_title("선택된 동들의 연령별 인구 그래프")
            ax.set_xlabel("나이")
            ax.set_ylabel("인구수")
            ax.set_xticks([i for i in range(0, 101, 10)])
            ax.legend(fontsize=8)
            fig.tight_layout()
            st.pyplot(fig)
        else:
            st.info("먼저 하나 이상의 동을 선택하세요.")
elif selected == "지역별 성별 인구 피라미드":
    st.subheader("🚻 지역별 성별 인구 피라미드")

    if st.session_state.get("df") is None:
        st.error("먼저 데이터를 업로드해주세요.")
    else:
        df1 = st.session_state.df.copy()

        # '동' 포함 행정구역 필터링
        dong_list = df1[df1['행정구역'].str.contains("동")]['행정구역'].unique()
        selected_dong = st.selectbox("동을 선택하세요", dong_list)

        # 선택된 동의 데이터 가져오기
        try:
            row = df1[df1['행정구역'] == selected_dong].iloc[0]
            male = (row.iloc[106:207] * -1).tolist()  # 남성: 음수
            female = row.iloc[209:310].tolist()       # 여성: 양수

            # 그래프 시각화
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(range(101), male, color='skyblue', label='남성')
            ax.barh(range(101), female, color='lightcoral', label='여성')

            ax.set_title(f"{selected_dong} 지역의 성별 인구 구조", fontsize=16)
            ax.set_xlabel("인구수")
            ax.set_ylabel("나이")
            ax.set_yticks(range(0, 101, 10))
            ax.set_yticklabels([f"{i}세" for i in range(0, 101, 10)])
            ax.set_xlim(-120, 120)
            ax.legend()
            fig.tight_layout()

            st.pyplot(fig)

        except IndexError:
            st.warning(f"{selected_dong}에 대한 데이터를 찾을 수 없습니다.")

elif selected == "인구 지표 분석 - 고령화 지수":
    st.subheader("📈 인구 지표 분석 - 고령화 지수")

    if st.session_state.get("df") is None:
        st.error("먼저 데이터를 업로드해주세요.")
    else:
        df1 = st.session_state.df.copy()

/        # 고령화 지수 계산
        df1['고령화지수'] = df1.iloc[:, 71:104].sum(axis=1) / df1.iloc[:, 21:64].sum(axis=1) * 100

        # 상위 10개 지역 추출
        top_aging = df1[['행정구역', '고령화지수']].sort_values(by='고령화지수', ascending=False).head(10)

        # 시각화
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(top_aging['행정구역'], top_aging['고령화지수'], color='orange')
        ax.set_xlabel("고령화 지수")
        ax.set_title("고령화 지수 높은 지역 Top 10")
        ax.invert_yaxis()
        fig.tight_layout()

        st.pyplot(fig)
        st.caption("※ 고령화 지수 = (65세 이상 인구 / 15~64세 인구) × 100 기준")
elif selected == "인구 지표 분석 - 연령대별 성비":
    st.subheader("📊 인구 지표 분석 - 연령대별 성비")

    if st.session_state.get("df") is None:
        st.error("먼저 데이터를 업로드해주세요.")
    else:
        # 데이터 복사
        pop_df = st.session_state.df.copy()

        # 남성, 여성 데이터 범위
        df_m = pop_df.iloc[:, 106:207]  # 남성 0~100세
        df_f = pop_df.iloc[:, 209:310]  # 여성 0~100세

        # 성비 지수 계산
        age_ranges = {
            '20대_성비': (20, 30),
            '30대_성비': (30, 40),
            '40대_성비': (40, 50),
            '50대_성비': (50, 60),
            '60세이상_성비': (60, 101)
        }

        for label, (start, end) in age_ranges.items():
            male_sum = df_m.iloc[:, start:end].sum(axis=1)
            female_sum = df_f.iloc[:, start:end].sum(axis=1)
            pop_df[label] = male_sum / female_sum * 100

        # 히트맵 그릴 데이터 준비
        heat_cols = list(age_ranges.keys())
        heat_df = pop_df[['행정구역'] + heat_cols].set_index('행정구역')

        # 시각화
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(heat_df, annot=True, fmt=".1f", cmap="RdYlBu_r", center=100, ax=ax)
        ax.set_title("전주시 연령대별 성비 히트맵 (남/여 × 100)")
        fig.tight_layout()

        st.pyplot(fig)
        st.caption("※ 성비 = (남성 인구 / 여성 인구) × 100 → 100이면 성비 균형, 110이면 남성 10% 많음")

# 추가 메뉴는 필요시 계속 elif로 확장
