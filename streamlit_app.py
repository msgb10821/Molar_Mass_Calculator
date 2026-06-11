import re
import streamlit as st

# 1. 스트림릿 세션 상태(Session State) 초기화
# 페이지가 새로고침되어도 데이터(원소 사전, 기록)가 유지되도록 합니다.
if "elements" not in st.session_state:
    st.session_state.elements = {
        "H": 1,
        "Li": 6,
        "C": 12,
        "N": 14,
        "O": 16,
        "F": 18,
        "Na": 22,
        "Mg": 24,
        "Al": 26,
        "Cl": 34,
    }

if "history" not in st.session_state:
    st.session_state.history = []

# 원소 기호와 숫자를 분리하는 정규식 수정
# (대문자+소문자 또는 대문자만) + (있거나 없는 숫자)를 모두 매칭합니다.
ELEMENT_PAT = re.compile(r"([A-Z][a-z]?)(\d*)")

# 2. 웹 앱 UI 레이아웃
st.title("🧪 화학 분자량 계산기")

# 사이드바: 등록된 원소 목록 및 새 원소 추가
st.sidebar.header("⚙️ 원소 관리")
st.sidebar.subheader("현재 등록된 원소 목록")
st.sidebar.json(st.session_state.elements)

# 사용자가 수동으로 원소를 미리 추가할 수 있는 기능
st.sidebar.subheader("새 원소 직접 등록")
new_elem = st.sidebar.text_input("원소 기호 (예: He)", max_chars=2).strip()
new_weight = st.sidebar.number_input("원자량 (g/mol)", min_value=0.0, format="%.2f")
if st.sidebar.button("원소 등록"):
    if new_elem:
        st.session_state.elements[new_elem] = new_weight
        st.sidebar.success(f"✅ {new_elem}({new_weight})이 등록되었습니다!")
        st.rerun()
    else:
        st.sidebar.error("원소 기호를 입력해주세요.")


# 메인 화면 탭 구성 (계산기 / 계산 기록)
tab1, tab2 = st.tabs(["🧮 분자량 계산", "📜 계산 기록"])

with tab1:
    st.subheader("화학식 입력")
    formula = st.text_input(
        "분자량을 계산할 화학식을 입력하세요.", placeholder="예: H2O, CO2, NaCl"
    ).strip()

    if st.button("계산하기"):
        if not formula:
            st.warning("화학식을 입력해주세요.")
        else:
            # 정규식을 통해 원소와 개수 추출
            tokens = ELEMENT_PAT.findall(formula)

            # 빈 매칭 제거 및 올바른 화학식인지 검증
            tokens = [t for t in tokens if t[0]]

            if not tokens:
                st.error("올바른 화학식 형식이 아닙니다.")
            else:
                total_weight = 0.0
                missing_elements = []

                # 1차 검증: 등록되지 않은 원소가 있는지 확인
                for elem, count in tokens:
                    if elem not in st.session_state.elements:
                        missing_elements.append(elem)

                if missing_elements:
                    st.error(
                        f"🚨 등록되지 않은 원소가 있습니다: {', '.join(set(missing_elements))}"
                    )
                    st.info("왼쪽 사이드바의 '새 원소 직접 등록' 메뉴에서 해당 원소를 먼저 등록해주세요.")
                else:
                    # 모든 원소가 존재할 때 계산 진행
                    for elem, count_str in tokens:
                        count = int(count_str) if count_str else 1
                        total_weight += st.session_state.elements[elem] * count

                    result_text = f"**{formula}**의 분자량: `{total_weight:,.2f} g/mol`"
                    st.success(result_text)

                    # 기록 추가 (중복 방지)
                    if result_text not in st.session_state.history:
                        st.session_state.history.append(result_text)

with tab2:
    st.subheader("📊 최근 계산 기록")
    if st.session_state.history:
        for idx, record in enumerate(reversed(st.session_state.history)):
            st.markdown(f"{idx+1}. {record}")

        if st.button("기록 전체 삭제"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("계산된 기록이 없습니다.")
