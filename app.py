import streamlit as st

# Konfiguracja strony
st.set_page_config(
    page_title="FizjoExpert - System Wspomagania Diagnozy",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== BAZA DANYCH =====

# Pytania do wywiadu
interview_questions = {
    'therapist': [
        {
            'id': 'mechanism',
            'question': 'Jaki był mechanizm urazu?',
            'options': [
                {'value': 'inversion', 'text': 'Inwersja stopy (skręcenie do wewnątrz)'},
                {'value': 'eversion', 'text': 'Ewersja stopy (skręcenie na zewnątrz)'},
                {'value': 'dorsiflexion', 'text': 'Nadmierna grzbietowa fleksja'},
                {'value': 'plantarflexion', 'text': 'Nadmierna podeszwowa fleksja'},
                {'value': 'direct_trauma', 'text': 'Bezpośredni uraz/uderzenie'},
                {'value': 'no_trauma', 'text': 'Brak wyraźnego urazu'}
            ]
        },
        {
            'id': 'pain_location',
            'question': 'Lokalizacja bólu:',
            'options': [
                {'value': 'lateral', 'text': 'Strona zewnętrzna stawu'},
                {'value': 'medial', 'text': 'Strona wewnętrzna stawu'},
                {'value': 'anterior', 'text': 'Przód stawu'},
                {'value': 'posterior', 'text': 'Tył stawu'},
                {'value': 'diffuse', 'text': 'Rozlany ból'}
            ]
        },
        {
            'id': 'pain_intensity',
            'question': 'Intensywność bólu (0-10):',
            'options': [
                {'value': '1-3', 'text': '1-3 (łagodny)'},
                {'value': '4-6', 'text': '4-6 (umiarkowany)'},
                {'value': '7-8', 'text': '7-8 (silny)'},
                {'value': '9-10', 'text': '9-10 (bardzo silny)'}
            ]
        },
        {
            'id': 'weight_bearing',
            'question': 'Możliwość obciążenia kończyny:',
            'options': [
                {'value': 'full', 'text': 'Pełne obciążenie bez bólu'},
                {'value': 'partial_pain', 'text': 'Częściowe obciążenie z bólem'},
                {'value': 'partial_no_pain', 'text': 'Częściowe obciążenie bez bólu'},
                {'value': 'impossible', 'text': 'Niemożność obciążenia'}
            ]
        },
        {
            'id': 'swelling',
            'question': 'Obecność obrzęku:',
            'options': [
                {'value': 'none', 'text': 'Brak obrzęku'},
                {'value': 'mild', 'text': 'Niewielki obrzęk'},
                {'value': 'moderate', 'text': 'Umiarkowany obrzęk'},
                {'value': 'severe', 'text': 'Znaczny obrzęk'}
            ]
        },
        {
            'id': 'onset_time',
            'question': 'Czas od urazu:',
            'options': [
                {'value': 'acute', 'text': 'Ostry (0-72h)'},
                {'value': 'subacute', 'text': 'Podostrych (3-14 dni)'},
                {'value': 'chronic', 'text': 'Przewlekły (>2 tygodnie)'}
            ]
        }
    ],
    'patient': [
        {
            'id': 'when_happened',
            'question': 'Kiedy wystąpił problem?',
            'options': [
                {'value': 'just_now', 'text': 'Właśnie teraz/dziś'},
                {'value': 'yesterday', 'text': 'Wczoraj'},
                {'value': 'few_days', 'text': 'Kilka dni temu'},
                {'value': 'week_more', 'text': 'Tydzień lub więcej temu'}
            ]
        },
        {
            'id': 'how_happened',
            'question': 'Jak doszło do urazu?',
            'options': [
                {'value': 'sport', 'text': 'Podczas aktywności sportowej'},
                {'value': 'stairs', 'text': 'Wchodząc/schodząc po schodach'},
                {'value': 'walking', 'text': 'Podczas normalnego chodzenia'},
                {'value': 'fall', 'text': 'Podczas upadku'},
                {'value': 'unknown', 'text': 'Nie pamiętam/nie wiem'}
            ]
        },
        {
            'id': 'pain_level',
            'question': 'Jak silny jest ból?',
            'options': [
                {'value': 'mild', 'text': 'Łagodny - mogę normalnie chodzić'},
                {'value': 'moderate', 'text': 'Umiarkowany - chodzę, ale boli'},
                {'value': 'severe', 'text': 'Silny - trudno mi chodzić'},
                {'value': 'extreme', 'text': 'Bardzo silny - nie mogę stanąć na nodze'}
            ]
        },
        {
            'id': 'swelling_simple',
            'question': 'Czy stopa/kostka jest spuchnięta?',
            'options': [
                {'value': 'no', 'text': 'Nie, wygląda normalnie'},
                {'value': 'little', 'text': 'Trochę spuchnięta'},
                {'value': 'much', 'text': 'Bardzo spuchnięta'}
            ]
        },
        {
            'id': 'walking_ability',
            'question': 'Czy możesz chodzić?',
            'options': [
                {'value': 'normal', 'text': 'Tak, normalnie'},
                {'value': 'limping', 'text': 'Tak, ale utykam'},
                {'value': 'barely', 'text': 'Ledwo, z dużym bólem'},
                {'value': 'cannot', 'text': 'Nie, nie mogę stanąć na nodze'}
            ]
        }
    ]
}

# Testy diagnostyczne
diagnostic_tests = {
    'anterior_drawer': {
        'name': 'Test szuflady przedniej',
        'icon': '🦶➡️',
        'description': 'Ocena stabilności więzadeł bocznych, szczególnie ATFL',
        'procedure': '''
### 🎯 Cel testu:
Ocena integralności więzadła strzałkowo-skokowego przedniego (ATFL)

### 📋 Procedura wykonania:
1. **Pozycja pacjenta:** Na plecach lub siedząc na krawędzi łóżka
2. **Pozycja stopy:** Lekka podeszwowa fleksja (10-15°)
3. **Chwyt terapeuty:** 
   - Jedna ręka stabilizuje golę z przodu
   - Druga ręka chwyć piętę od tyłu
4. **Wykonanie:** Delikatny ruch pięty do przodu względem goleni
5. **Ocena:** Przesunięcie i czucie końcowe

### 📊 Interpretacja:
- **POZYTYWNY:** Zwiększona ruchomość >4mm, brak twardego czucia końcowego
- **NEGATYWNY:** Normalna ruchomość, twarde czucie końcowe
- **Wskazuje na:** Uszkodzenie ATFL (najczęstsze przy inwersji)

### ⚠️ Uwagi:
- Porównaj z kończyną zdrową
- Test może być fałszywie pozytywny przy ostrej fazie (obrzęk, ból)
        '''
    },
    'talar_tilt': {
        'name': 'Test pochylenia talusa',
        'icon': '🦶↗️',
        'description': 'Ocena więzadeł bocznych stawu skokowego (CFL)',
        'procedure': '''
### 🎯 Cel testu:
Ocena integralności więzadła piętowo-strzałkowego (CFL)

### 📋 Procedura wykonania:
1. **Pozycja pacjenta:** Na boku (badana noga na górze) lub na plecach
2. **Pozycja stopy:** Neutralna (90°)
3. **Chwyt terapeuty:** 
   - Jedna ręka stabilizuje golę
   - Druga ręka chwyć stopę od strony przyśrodkowej
4. **Wykonanie:** Inwersja stopy z jednoczesnym adduktem
5. **Ocena:** Stopień nachylenia talusa w widłach kostki

### 📊 Interpretacja:
- **POZYTYWNY:** Nachylenie >10° różnicy między stronami
- **NEGATYWNY:** Różnica <5° między stronami
- **Wskazuje na:** Uszkodzenie CFL ± ATFL

### ⚠️ Uwagi:
- Wykonyj porównanie z kończyną zdrową
- CFL jest drugie w kolejności uszkodzeń po ATFL
        '''
    },
    'squeeze_test': {
        'name': 'Test kompresji goleni',
        'icon': '🤏',
        'description': 'Wykluczenie uszkodzenia syndesmosis',
        'procedure': '''
### 🎯 Cel testu:
Wykluczenie uszkodzenia syndesmosis (więzadeł łączących kości goleni)

### 📋 Procedura wykonania:
1. **Pozycja pacjenta:** Na plecach, noga wyprostowana
2. **Chwyt terapeuty:** Obie ręce na goleni w 1/3 środkowej
3. **Wykonanie:** Kompresja kości strzałkowej ku piszczelowej
4. **Obserwacja:** Reakcja pacjenta, lokalizacja bólu

### 📊 Interpretacja:
- **POZYTYWNY:** Ból w okolicy stawu skokowego (dystalnie)
- **NEGATYWNY:** Brak bólu w stawie skokowym
- **Wskazuje na:** Uszkodzenie syndesmosis

### ⚠️ Uwagi:
- Ból w miejscu ucisku nie jest pozytywny
- Ból musi wystąpić w stawie skokowym
- Uszkodzenie syndesmosis to poważny uraz wymagający leczenia ortopedycznego
        '''
    },
    'ottawa_rules': {
        'name': 'Reguły Ottawy',
        'icon': '📏',
        'description': 'Wykluczenie złamania - wskazania do RTG',
        'procedure': '''
### 🎯 Cel:
Określenie wskazań do badania radiologicznego (RTG)

### 📋 Kryteria dla KOSTKI:
**RTG wskazane gdy ból w okolicy kostki ORAZ:**
- Niemożność obciążenia (4 kroki) bezpośrednio po urazie I w momencie badania
- **LUB** bolesność palpacyjna nad:
  - Końcem dystalnym kości strzałkowej (dolne 6cm)
  - Końcem dystalnym kości piszczelowej (dolne 6cm)

### 📋 Kryteria dla STOPY:
**RTG wskazane gdy ból w środstopiu ORAZ:**
- Niemożność obciążenia (4 kroki) bezpośrednio po urazie I w momencie badania
- **ORAZ** bolesność palpacyjna nad:
  - Kością łódkowatą (os naviculare)
  - Podstawą 5. kości śródstopia

### 📊 Charakterystyka:
- **Czułość:** 96-99% (bardzo rzadko przegapi złamanie)
- **Swoistość:** ~40% (redukuje liczbę niepotrzebnych RTG)
- **Zastosowanie:** Pacjenci >18 lat, do 10 dni od urazu

### ⚠️ Ważne:
- Niemożność obciążenia = niemożność wykonania 4 kroków
- Badanie palpacyjne musi być dokładne
- Przy wątpliwościach zawsze skieruj na RTG
        '''
    },
    'thompson_test': {
        'name': 'Test Thompson\'a',
        'icon': '🦵',
        'description': 'Wykluczenie zerwania ścięgna Achillesa',
        'procedure': '''
### 🎯 Cel testu:
Wykluczenie całkowitego zerwania ścięgna Achillesa

### 📋 Procedura wykonania:
1. **Pozycja pacjenta:** Na brzuchu, stopy zwisające poza łóżko
2. **Pozycja terapeuty:** Z boku łóżka
3. **Wykonanie:** Ściskaj mięsień trójgłowy łydki
4. **Obserwacja:** Ruch stopy w kierunku podeszwowej fleksji

### 📊 Interpretacja:
- **NEGATYWNY (prawidłowy):** Podeszwowa fleksja stopy
- **POZYTYWNY:** Brak ruchu stopy = zerwanie ścięgna
- **Wskazuje na:** Całkowite zerwanie ścięgna Achillesa

### ⚠️ Uwagi:
- Test bardzo wiarygodny przy całkowitym zerwaniu
- Częściowe zerwania mogą dać wynik negatywny
- Przy pozytywnym teście - pilne skierowanie do ortopedy
        '''
    }
}

# ===== FUNKCJE LOGIKI =====

def get_suggested_tests(answers, mode):
    """Algorytm sugerujący testy na podstawie wywiadu"""
    tests = []
    
    if mode == 'therapist':
        # Logika dla fizjoterapeuty
        mechanism = answers.get('mechanism')
        pain_location = answers.get('pain_location')
        pain_intensity = answers.get('pain_intensity')
        weight_bearing = answers.get('weight_bearing')
        swelling = answers.get('swelling')
        
        # Testy dla uszkodzeń inwersyjnych
        if mechanism == 'inversion' or pain_location == 'lateral':
            tests.extend(['anterior_drawer', 'talar_tilt'])
        
        # Testy dla uszkodzeń ewersyjnych
        if mechanism == 'eversion' or pain_location == 'medial':
            tests.append('squeeze_test')
        
        # Reguły Ottawy przy wysokim ryzyku złamania
        if (pain_intensity in ['7-8', '9-10'] or 
            weight_bearing == 'impossible' or 
            swelling == 'severe'):
            tests.append('ottawa_rules')
        
        # Test Thompson'a przy bólu z tyłu
        if pain_location == 'posterior' or mechanism == 'plantarflexion':
            tests.append('thompson_test')
            
    else:  # mode == 'patient'
        # Logika dla pacjenta - uproszczona
        pain_level = answers.get('pain_level')
        swelling = answers.get('swelling_simple')
        walking = answers.get('walking_ability')
        
        # Reguły Ottawy dla poważnych przypadków
        if (pain_level == 'extreme' or 
            swelling == 'much' or 
            walking == 'cannot'):
            tests.append('ottawa_rules')
        
        # Podstawowe testy stabilności
        if pain_level in ['mild', 'moderate']:
            tests.extend(['anterior_drawer', 'talar_tilt'])
    
    return list(set(tests))  # Usuń duplikaty

def generate_diagnosis(answers, test_results, mode):
    """Generuje diagnozę na podstawie wywiadu i testów"""
    diagnosis = {
        'primary': 'Nieokreślone uszkodzenie stawu skokowego',
        'confidence': 60,
        'secondary': None,
        'therapy': 'Podstawowe zalecenia zgodnie z protokołem RICE',
        'referral': None,
        'red_flags': []
    }
    
    # Analiza czerwonych flag
    red_flags = []
    
    if mode == 'therapist':
        # Analiza dla fizjoterapeuty
        mechanism = answers.get('mechanism')
        pain_location = answers.get('pain_location')
        pain_intensity = answers.get('pain_intensity')
        weight_bearing = answers.get('weight_bearing')
        swelling = answers.get('swelling')
        
        # Czerwone flagi
        if pain_intensity == '9-10':
            red_flags.append('Bardzo silny ból')
        if weight_bearing == 'impossible':
            red_flags.append('Niemożność obciążenia')
        if swelling == 'severe':
            red_flags.append('Znaczny obrzęk')
            
        # Analiza mechanizmu i lokalizacji
        lateral_injury = mechanism == 'inversion' or pain_location == 'lateral'
        medial_injury = mechanism == 'eversion' or pain_location == 'medial'
        
        # Analiza wyników testów
        anterior_drawer_pos = test_results.get('anterior_drawer') == 'positive'
        talar_tilt_pos = test_results.get('talar_tilt') == 'positive'
        squeeze_pos = test_results.get('squeeze_test') == 'positive'
        ottawa_pos = test_results.get('ottawa_rules') == 'positive'
        thompson_pos = test_results.get('thompson_test') == 'positive'
        
        # Logika diagnostyczna
        if thompson_pos:
            diagnosis.update({
                'primary': 'Zerwanie ścięgna Achillesa',
                'confidence': 95,
                'therapy': 'PILNE skierowanie do ortopedy - nie podejmować rehabilitacji!',
                'referral': 'PILNE skierowanie do ortopedy/SOR'
            })
        elif ottawa_pos:
            diagnosis.update({
                'primary': 'Wysokie prawdopodobieństwo złamania',
                'confidence': 90,
                'therapy': 'Unieruchomienie, analgetyki, brak obciążenia',
                'referral': 'PILNE skierowanie na RTG + konsultacja ortopedyczna'
            })
        elif squeeze_pos:
            diagnosis.update({
                'primary': 'Uszkodzenie syndesmosis',
                'confidence': 85,
                'therapy': 'Unieruchomienie, brak obciążenia przez 6-8 tygodni',
                'referral': 'Konsultacja ortopedyczna + MRI'
            })
        elif lateral_injury and (anterior_drawer_pos or talar_tilt_pos):
            if anterior_drawer_pos and talar_tilt_pos:
                diagnosis.update({
                    'primary': 'Uszkodzenie kompleksu więzadeł bocznych (ATFL + CFL)',
                    'confidence': 90,
                    'secondary': 'Stopień II-III według klasyfikacji'
                })
            elif anterior_drawer_pos:
                diagnosis.update({
                    'primary': 'Uszkodzenie więzadła ATFL',
                    'confidence': 85,
                    'secondary': 'Możliwe częściowe uszkodzenie CFL'
                })
            elif talar_tilt_pos:
                diagnosis.update({
                    'primary': 'Uszkodzenie więzadła CFL',
                    'confidence': 80,
                    'secondary': 'Sprawdź integralność ATFL'
                })
            
            # Protokół terapeutyczny dla uszkodzeń więzadłowych
            onset = answers.get('onset_time')
            if onset == 'acute':
                therapy = '''
**FAZA OSTRA (0-72h):**
- RICE (Rest, Ice, Compression, Elevation)
- Ochrona przed dalszym uszkodzeniem
- Analgetyki/NLPZ według wskazań lekarskich
- Łagodne ćwiczenia bez bólu

**PLAN DALSZEGO LECZENIA:**
- Faza podostra: mobilizacja, ćwiczenia ROM
- Faza funkcjonalna: wzmacnianie, propriocepcja
- Powrót do sportu: 6-12 tygodni
                '''
            else:
                therapy = '''
**PROTOKÓŁ REHABILITACJI:**
- Mobilizacja stawu skokowego (wszystkie płaszczyzny)
- Wzmacnianie mięśni strzałkowych i piszczelowych
- Trening propriocepcji i równowagi
- Trening funkcjonalny i sportowo-specyficzny
- Edukacja pacjenta o profilaktyce
                '''
            diagnosis['therapy'] = therapy
            
    else:  # mode == 'patient'
        # Analiza dla pacjenta
        pain_level = answers.get('pain_level')
        walking = answers.get('walking_ability')
        swelling = answers.get('swelling_simple')
        when_happened = answers.get('when_happened')
        
        if pain_level == 'extreme' or walking == 'cannot':
            red_flags.append('Bardzo silny ból/niemożność chodzenia')
            diagnosis.update({
                'primary': 'Poważne uszkodzenie stawu skokowego',
                'confidence': 85,
                'referral': 'Zalecamy PILNĄ wizytę w SOR lub u ortopedy'
            })
        elif swelling == 'much':
            red_flags.append('Znaczny obrzęk')
            diagnosis.update({
                'referral': 'Zalecamy wizytę u lekarza w ciągu 24h'
            })
        elif pain_level in ['mild', 'moderate'] and walking in ['normal', 'limping']:
            diagnosis.update({
                'primary': 'Prawdopodobne skręcenie stawu skokowego',
                'confidence': 75,
                'therapy': '''
**Zalecenia domowe:**
- Odpoczynek - unikaj obciążania
- Lód - 15-20 min co 2-3h przez pierwsze 2 dni
- Bandaż elastyczny (nie za ciasno!)
- Uniesienie nogi powyżej poziomu serca
- W razie braku poprawy w ciągu 3-5 dni - wizyta u fizjoterapeuty
                ''',
                'referral': 'Obserwacja domowa. Jeśli brak poprawy w 3-5 dni - fizjoterapeuta'
            })
    
    diagnosis['red_flags'] = red_flags
    return diagnosis

# ===== CSS STYLING =====
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
        transition: all 0.3s ease;
    }
    .test-card:hover {
        border-color: #2196F3;
        background: #f0f8ff;
    }
    .positive-result {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .negative-result {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .diagnosis-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
    }
    .red-flag {
        background-color: #ffebee;
        border: 2px solid #f44336;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .therapy-box {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .referral-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .progress-container {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== GŁÓWNA APLIKACJA =====

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
        st.markdown("### 🧭 Nawigacja")
        
        if st.button("🏠 Nowa diagnoza", use_container_width=True):
            reset_session()
            st.rerun()
        
        if st.session_state.mode:
            mode_name = '👨‍⚕️ Fizjoterapeuta' if st.session_state.mode == 'therapist' else '👤 Pacjent'
            st.info(f"**Tryb:** {mode_name}")
            
            # Progress bar
            if st.session_state.answers:
                questions_total = len(interview_questions[st.session_state.mode])
                progress = len(st.session_state.answers) / questions_total
                st.markdown("**📊 Postęp wywiadu:**")
                st.progress(progress)
                st.write(f"{len(st.session_state.answers)}/{questions_total} pytań")
        
        # Informacje o aplikacji
        with st.expander("ℹ️ O aplikacji"):
            st.markdown("""
            **FizjoExpert v1.0**
            
            System wspomagający diagnozę urazów stawu skokowego górnego.
            
            **Funkcje:**
            - Inteligentny wywiad
            - Sugerowane testy
            - Analiza diagnostyczna
            - Protokoły terapeutyczne
            
            **Uwaga:** Aplikacja nie zastępuje konsultacji medycznej!
            """)
    
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
    st.markdown("## 🎯 Wybierz tryb pracy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👨‍⚕️ Tryb Fizjoterapeuty
        - Szczegółowy wywiad medyczny
        - Dostęp do wszystkich testów diagnostycznych  
        - Propozycje protokołów terapeutycznych
        - Analiza różnicowa
        """)
        if st.button("Rozpocznij jako fizjoterapeuta", use_container_width=True, type="primary"):
            st.session_state.mode = 'therapist'
            st.session_state.current_step = 'interview'
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 👤 Tryb Pacjenta
        - Uproszczone pytania w języku pacjenta
        - Podstawowe wskazówki samoleczenia
        - Informacje kiedy udać się do specjalisty
        - Rozpoznawanie czerwonych flag
        """)
        if st.button("Rozpocznij jako pacjent", use_container_width=True):
            st.session_state.mode = 'patient'
            st.session_state.current_step = 'interview'
            st.rerun()
    
    # Disclaimer
    st.markdown("""
    ---
    ⚠️ **WAŻNE:** Ta aplikacja służy wyłącznie do wspomagania diagnozy i nie zastępuje 
    profesjonalnej konsultacji medycznej. W przypadku poważnych urazów zawsze skonsultuj się z lekarzem.
    """)

def show_interview():
    if st.session_state.mode == 'therapist':
        st.markdown("## 📋 Wywiad diagnostyczny - tryb specjalisty")
    else:
        st.markdown("## ❓ Kilka pytań o Twoje dolegliwości")
    
    questions = interview_questions[st.session_state.mode]
    
    # Progress
    progress = len(st.session_state.answers) / len(questions)
    st.markdown(f"""
    <div class="progress-container">
        <strong>Postęp: {len(st.session_state.answers)}/{len(questions)} pytań</strong>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress)
    
    # Znajdź pierwsze pytanie bez odpowiedzi
    current_question = None
    for question in questions:
        if question['id'] not in st.session_state.answers:
            current_question = question
            break
    
    if current_question:
        # Pokaż aktualne pytanie
        st.markdown(f"### {current_question['question']}")
        
        # Formularz z opcjami
        with st.form("question_form"):
            answer = st.radio(
                "Wybierz odpowiedź:",
                options=[opt['value'] for opt in current_question['options']],
                format_func=lambda x: next(opt['text'] for opt in current_question['options'] if opt['value'] == x),
                key=f"current_question"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if len(st.session_state.answers) > 0:
                    if st.form_submit_button("⬅️ Poprzednie pytanie", use_container_width=True):
                        # Usuń ostatnią odpowiedź
                        last_question_id = list(st.session_state.answers.keys())[-1]
                        del st.session_state.answers[last_question_id]
                        st.rerun()
            
            with col2:
                button_text = "Zakończ wywiad ➡️" if len(st.session_state.answers) == len(questions) - 1 else "Następne pytanie ➡️"
                if st.form_submit_button(button_text, type="primary", use_container_width=True):
                    st.session_state.answers[current_question['id']] = answer
                    
                    if len(st.session_state.answers) == len(questions):
                        st.session_state.current_step = 'tests'
                    
                    st.rerun()
    
    # Podsumowanie odpowiedzi
    if st.session_state.answers:
        with st.expander(f"📝 Twoje odpowiedzi ({len(st.session_state.answers)}/{len(questions)})", expanded=False):
            for q_id, answer in st.session_state.answers.items():
                question = next(q for q in questions if q['id'] == q_id)
                answer_text = next(opt['text'] for opt in question['options'] if opt['value'] == answer)
                st.markdown(f"**{question['question']}**")
                st.markdown(f"↳ *{answer_text}*")
                st.markdown("---")

def show_tests():
    st.markdown("## 🔬 Sugerowane testy diagnostyczne")
    
    suggested_tests = get_suggested_tests(st.session_state.answers, st.session_state.mode)
    
    if not suggested_tests:
        st.warning("Brak sugerowanych testów na podstawie wywiadu.")
        if st.button("➡️ Przejdź do analizy", type="primary"):
            st.session_state.current_step = 'diagnosis'
            st.rerun()
        return
    
    st.success(f"🎯 Na podstawie wywiadu sugeruje się wykonanie **{len(suggested_tests)}** testów diagnostycznych.")
    
    for i, test_id in enumerate(suggested_tests, 1):
        test = diagnostic_tests[test_id]
        
        st.markdown(f"""
        <div class="test-card">
            <h3>{test['icon']} {i}. {test['name']}</h3>
            <p><strong>Cel:</strong> {test['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button(f"📖 Procedura wykonania", key=f"show_{test_id}", use_container_width=True):
                st.session_state[f"show_procedure_{test_id}"] = not st.session_state.get(f"show_procedure_{test_id}", False)
                st.rerun()
        
        # Pokaż procedurę jeśli została wybrana
        if st.session_state.get(f"show_procedure_{test_id}", False):
            with st.expander(f"📋 Procedura - {test['name']}", expanded=True):
                st.markdown(test['procedure'])
        
        if st.session_state.mode == 'therapist':
            with col2:
                if st.button("✅ Negatywny", key=f"neg_{test_id}", use_container_width=True):
                    st.session_state.test_results[test_id] = 'negative'
                    st.rerun()
            
            with col3:
                if st.button("⚠️ Pozytywny", key=f"pos_{test_id}", type="primary", use_container_width=True):
                    st.session_state.test_results[test_id] = 'positive'
                    st.rerun()
            
            # Pokaż wynik
            if test_id in st.session_state.test_results:
                result = st.session_state.test_results[test_id]
                if result == 'positive':
                    st.markdown(f'<div class="positive-result"><strong>⚠️ Wynik: POZYTYWNY</strong></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="negative-result"><strong>✅ Wynik: NEGATYWNY</strong></div>', unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Przycisk do diagnozy
    if st.session_state.mode == 'patient' or st.session_state.test_results:
        st.markdown("### 🎯 Gotowy na analizę?")
        if st.session_state.mode == 'therapist':
            tests_done = len(st.session_state.test_results)
            st.info(f"Wykonano {tests_done}/{len(suggested_tests)} testów")
        
        if st.button("🎯 Przejdź do analizy diagnostycznej", type="primary", use_container_width=True):
            st.session_state.current_step = 'diagnosis'
            st.rerun()

def show_diagnosis():
    st.markdown("## 🎯 Analiza diagnostyczna")
    
    diagnosis = generate_diagnosis(st.session_state.answers, st.session_state.test_results, st.session_state.mode)
    
    # Czerwone flagi
    if diagnosis['red_flags']:
        st.markdown("""
        <div class="red-flag">
            <h3>🚨 CZERWONE FLAGI</h3>
        </div>
        """, unsafe_allow_html=True)
        for flag in diagnosis['red_flags']:
            st.error(f"⚠️ {flag}")
    
    # Główna diagnoza
    confidence_color = "🟢" if diagnosis['confidence'] >= 80 else "🟡" if diagnosis['confidence'] >= 60 else "🔴"
    st.markdown(f"""
    <div class="diagnosis-box">
        <h2>💡 Prawdopodobna diagnoza</h2>
        <h1>{diagnosis['primary']}</h1>
        <h3>{confidence_color} Prawdopodobieństwo: {diagnosis['confidence']}%</h3>
        {f"<p><i>Diagnoza różnicowa: {diagnosis['secondary']}</i></p>" if diagnosis.get('secondary') else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Podsumowanie
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Podsumowanie wywiadu")
        questions = interview_questions[st.session_state.mode]
        for q_id, answer in st.session_state.answers.items():
            question = next(q for q in questions if q['id'] == q_id)
            answer_text = next(opt['text'] for opt in question['options'] if opt['value'] == answer)
            st.markdown(f"**{question['question']}**")
            st.markdown(f"↳ {answer_text}")
    
    with col2:
        if st.session_state.test_results:
            st.markdown("### 🔬 Wyniki testów")
            for test_id, result in st.session_state.test_results.items():
                test_name = diagnostic_tests[test_id]['name']
                icon = "⚠️" if result == 'positive' else "✅"
                color = "🔴" if result == 'positive' else "🟢"
                st.markdown(f"{icon} **{test_name}:** {color} {result.upper()}")
        else:
            st.info("Brak wykonanych testów")
    
    # Zalecenia terapeutyczne
    st.markdown("""
    <div class="therapy-box">
        <h3>🎯 Zalecenia terapeutyczne</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(diagnosis['therapy'])
    
    # Skierowania
    if diagnosis.get('referral'):
        st.markdown("""
        <div class="referral-box">
            <h3>🏥 Dalsze postępowanie</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if 'PILNE' in diagnosis['referral']:
            st.error(f"🚨 {diagnosis['referral']}")
        else:
            st.warning(f"⚠️ {diagnosis['referral']}")
    
    # Akcje
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nowa diagnoza", use_container_width=True):
            reset_session()
            st.rerun()
    
    with col2:
        if st.button("📊 Podsumowanie PDF", use_container_width=True):
            st.info("Funkcja eksportu PDF będzie dostępna w przyszłej wersji")

def reset_session():
    """Reset session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.mode = None
    st.session_state.answers = {}
    st.session_state.test_results = {}
    st.session_state.current_step = 'mode_selection'

if __name__ == "__main__":
    main()
