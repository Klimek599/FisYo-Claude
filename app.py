import streamlit as st
from data.questions import interview_questions
from data.tests import diagnostic_tests
from data.diagnosis import generate_diagnosis, get_suggested_tests

# Konfiguracja strony
st.set_page_config(
    page_title="FizjoExpert - System Wspomagania Diagnozy",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Style
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .test-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    .positive-result {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
    }
    .negative-result {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
    }
    .diagnosis-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 FizjoExpert</h1>
        <p>System wspomagania diagnozy w fizjoterapii</p>
        <p><i>Specjalizacja: Staw skokowy górny</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicjalizacja session state
    if 'mode' not in st.session_state:
        st.session_state.mode = None
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'mode_selection'
    
    # Sidebar dla nawigacji
    with st.sidebar:
        st.image("🏥", width=50)
        st.title("Nawigacja")
        
        if st.button("🏠 Start", use_container_width=True):
            reset_session()
        
        if st.session_state.mode:
            st.write(f"**Tryb:** {'👨‍⚕️ Fizjoterapeuta' if st.session_state.mode == 'therapist' else '👤 Pacjent'}")
            
            if st.session_state.answers:
                st.write("**Postęp:**")
                st.progress(len(st.session_state.answers) / len(interview_questions[st.session_state.mode]))
    
    # Main content
    if st.session_state.current_step == 'mode_selection':
        show_mode_selection()
    elif st.session_state.current_step == 'interview':
        show_interview()
    elif st.session_state.current_step == 'tests':
        show_tests()
    elif st.session_state.current_step == 'diagnosis':
        show_diagnosis()

def show_mode_selection():
    st.subheader("Wybierz tryb pracy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👨‍⚕️ Tryb Fizjoterapeuty", use_container_width=True, type="primary"):
            st.session_state.mode = 'therapist'
            st.session_state.current_step = 'interview'
            st.rerun()
    
    with col2:
        if st.button("👤 Tryb Pacjenta", use_container_width=True):
            st.session_state.mode = 'patient'
            st.session_state.current_step = 'interview'
            st.rerun()
    
    # Informacje o trybach
    with st.expander("ℹ️ Informacje o trybach"):
        st.markdown("""
        **Tryb Fizjoterapeuty:**
        - Szczegółowy wywiad medyczny
        - Dostęp do wszystkich testów diagnostycznych
        - Propozycje protokołów terapeutycznych
        - Analiza różnicowa
        
        **Tryb Pacjenta:**
        - Uproszczone pytania w języku pacjenta
        - Podstawowe wskazówki
        - Informacje kiedy udać się do specjalisty
        - Czerwone flagi
        """)

def show_interview():
    if st.session_state.mode == 'therapist':
        st.subheader("📋 Wywiad diagnostyczny - tryb specjalisty")
    else:
        st.subheader("❓ Kilka pytań o Twoje dolegliwości")
    
    questions = interview_questions[st.session_state.mode]
    
    # Progress bar
    progress = len(st.session_state.answers) / len(questions)
    st.progress(progress)
    st.write(f"Pytanie {len(st.session_state.answers) + 1} z {len(questions)}")
    
    # Formularz z pytaniami
    with st.form("interview_form"):
        for question in questions:
            if question['id'] not in st.session_state.answers:
                st.markdown(f"**{question['question']}**")
                
                answer = st.radio(
                    "Wybierz odpowiedź:",
                    options=[opt['value'] for opt in question['options']],
                    format_func=lambda x: next(opt['text'] for opt in question['options'] if opt['value'] == x),
                    key=f"q_{question['id']}"
                )
                
                if st.form_submit_button("Potwierdź odpowiedź", type="primary"):
                    st.session_state.answers[question['id']] = answer
                    
                    if len(st.session_state.answers) == len(questions):
                        st.session_state.current_step = 'tests'
                    
                    st.rerun()
                break
    
    # Podsumowanie odpowiedzi
    if st.session_state.answers:
        with st.expander("📝 Twoje odpowiedzi"):
            for q_id, answer in st.session_state.answers.items():
                question = next(q for q in questions if q['id'] == q_id)
                answer_text = next(opt['text'] for opt in question['options'] if opt['value'] == answer)
                st.write(f"**{question['question']}**")
                st.write(f"↳ {answer_text}")

def show_tests():
    st.subheader("🔬 Sugerowane testy diagnostyczne")
    
    suggested_tests = get_suggested_tests(st.session_state.answers, st.session_state.mode)
    
    if not suggested_tests:
        st.warning("Brak sugerowanych testów na podstawie wywiadu.")
        return
    
    st.info(f"Na podstawie wywiadu sugeruje się wykonanie {len(suggested_tests)} testów diagnostycznych.")
    
    for test_id in suggested_tests:
        test = diagnostic_tests[test_id]
        
        with st.container():
            st.markdown(f"""
            <div class="test-card">
                <h3>{test['icon']} {test['name']}</h3>
                <p><strong>Cel:</strong> {test['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button(f"📖 Pokaż procedurę - {test['name']}", key=f"show_{test_id}"):
                    with st.expander(f"Procedura wykonania - {test['name']}", expanded=True):
                        st.markdown(test['procedure'])
            
            if st.session_state.mode == 'therapist':
                with col2:
                    if st.button("✅ Negatywny", key=f"neg_{test_id}", type="secondary"):
                        st.session_state.test_results[test_id] = 'negative'
                        st.rerun()
                
                with col3:
                    if st.button("⚠️ Pozytywny", key=f"pos_{test_id}", type="primary"):
                        st.session_state.test_results[test_id] = 'positive'
                        st.rerun()
                
                # Pokaż wynik jeśli został zapisany
                if test_id in st.session_state.test_results:
                    result = st.session_state.test_results[test_id]
                    if result == 'positive':
                        st.markdown(f'<div class="positive-result">✅ Wynik: <strong>POZYTYWNY</strong></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="negative-result">✅ Wynik: <strong>NEGATYWNY</strong></div>', unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Przycisk do diagnozy
    if st.session_state.mode == 'patient' or st.session_state.test_results:
        if st.button("🎯 Przejdź do analizy diagnostycznej", type="primary", use_container_width=True):
            st.session_state.current_step = 'diagnosis'
            st.rerun()

def show_diagnosis():
    st.subheader("🎯 Analiza diagnostyczna")
    
    diagnosis = generate_diagnosis(st.session_state.answers, st.session_state.test_results, st.session_state.mode)
    
    # Główna diagnoza
    st.markdown(f"""
    <div class="diagnosis-box">
        <h2>💡 Prawdopodobna diagnoza</h2>
        <h1>{diagnosis['primary']}</h1>
        <h3>Prawdopodobieństwo: {diagnosis['confidence']}%</h3>
        {f"<p><strong>Diagnoza różnicowa:</strong> {diagnosis['secondary']}</p>" if diagnosis.get('secondary') else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Podsumowanie badania
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Podsumowanie wywiadu")
        questions = interview_questions[st.session_state.mode]
        for q_id, answer in st.session_state.answers.items():
            question = next(q for q in questions if q['id'] == q_id)
            answer_text = next(opt['text'] for opt in question['options'] if opt['value'] == answer)
            st.write(f"**{question['question']}**")
            st.write(f"↳ {answer_text}")
    
    with col2:
        if st.session_state.test_results:
            st.subheader("🔬 Wyniki testów")
            for test_id, result in st.session_state.test_results.items():
                test_name = diagnostic_tests[test_id]['name']
                icon = "⚠️" if result == 'positive' else "✅"
                st.write(f"{icon} **{test_name}:** {result.upper()}")
    
    # Zalecenia terapeutyczne
    st.subheader("🎯 Zalecenia terapeutyczne")
    st.markdown(diagnosis['therapy'])
    
    # Skierowania
    if diagnosis.get('referral'):
        st.error(f"🏥 **Konieczne skierowania:** {diagnosis['referral']}")
    
    # Przycisk restart
    if st.button("🔄 Nowa diagnoza", type="secondary", use_container_width=True):
        reset_session()
        st.rerun()

def reset_session():
    st.session_state.mode = None
    st.session_state.answers = {}
    st.session_state.test_results = {}
    st.session_state.current_step = 'mode_selection'

if __name__ == "__main__":
    main()
