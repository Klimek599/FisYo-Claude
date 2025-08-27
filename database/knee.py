import streamlit as st
from typing import Dict, List, Any, Optional
from .base_module import BaseModule, AssessmentStep
from ..database.models import Patient, DiagnosticTest, Diagnosis

class KneeModule(BaseModule):
    """Moduł diagnostyczny dla kolana"""
    
    def __init__(self):
        super().__init__("Kolano", "🦵")
    
    def _define_assessment_steps(self) -> List[AssessmentStep]:
        return [
            AssessmentStep("red_flags", "Czerwone flagi", "Kontrola objawów alarmowych"),
            AssessmentStep("history", "Wywiad", "Szczegółowy wywiad medyczny"),
            AssessmentStep("physical", "Badanie fizykalne", "Testy stabilności i funkcji"),
            AssessmentStep("meniscus", "Testy łąkotek", "Ocena uszkodzeń łąkotek"),
            AssessmentStep("ligaments", "Testy więzadeł", "Ocena stabilności więzadłowej"),
            AssessmentStep("patellofemoral", "Patellofemoral", "Ocena stawu rzepkowo-udowego"),
            AssessmentStep("diagnosis", "Diagnoza", "Analiza wyników i diagnoza")
        ]
    
    def _define_diagnostic_tests(self) -> List[DiagnosticTest]:
        return [
            DiagnosticTest(
                name="Test Lachmana (ACL)",
                description="Ocena integralności więzadła krzyżowego przedniego",
                procedure="""
                **Pozycja pacjenta:** Na plecach, kolano w 20-30° fleksji
                
                **Procedura:**
                1. Jedną ręką stabilizuj udo pacjenta
                2. Drugą ręką chwyć golę tuż poniżej kolana
                3. Wykonaj ruch goleni do przodu względem uda
                4. Oceń przesunięcie i czucie końcowe
                
                **Interpretacja:**
                - **Pozytywny:** Zwiększone przesunięcie, miękkie czucie końcowe
                - **Negatywny:** Minimalne przesunięcie, twarde czucie końcowe
                """,
                sensitivity=0.87,
                specificity=0.93,
                interpretation={
                    "positive": "Uszkodzenie ACL prawdopodobne",
                    "negative": "ACL prawdopodobnie nieuszkodzone"
                },
                module_type="knee",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test szuflady przedniej (ACL)",
                description="Alternatywny test dla więzadła krzyżowego przedniego",
                procedure="""
                **Pozycja pacjenta:** Na plecach, kolano w 90° fleksji, stopa na podłożu
                
                **Procedura:**
                1. Usiądź na stopie pacjenta aby ją ustabilizować
                2. Obiema rękami chwyć golę tuż poniżej kolana
                3. Wykonaj ruch goleni do przodu
                4. Oceń przesunięcie względem uda
                
                **Interpretacja:**
                - **Pozytywny:** Nadmierne przesunięcie goleni do przodu
                - **Negatywny:** Normalne, ograniczone przesunięcie
                """,
                sensitivity=0.62,
                specificity=0.67,
                interpretation={
                    "positive": "Uszkodzenie ACL możliwe",
                    "negative": "ACL prawdopodobnie nieuszkodzone"
                },
                module_type="knee",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test szuflady tylnej (PCL)",
                description="Ocena integralności więzadła krzyżowego tylnego",
                procedure="""
                **Pozycja pacjenta:** Na plecach, kolano w 90° fleksji
                
                **Procedura:**
                1. Obserwuj pozycję goleni względem uda
                2. Obiema rękami chwyć golę i przesuń do tyłu
                3. Oceń przesunięcie tylne goleni
                
                **Interpretacja:**
                - **Pozytywny:** Nadmierne przesunięcie goleni do tyłu
                - **Pozycja grawitacyjna:** Golenie "opada" do tyłu sama
                """,
                sensitivity=0.79,
                specificity=0.84,
                interpretation={
                    "positive": "Uszkodzenie PCL prawdopodobne",
                    "negative": "PCL prawdopodobnie nieuszkodzone"
                },
                module_type="knee",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test McMurraya (łąkotki)",
                description="Wykrywanie uszkodzeń łąkotek",
                procedure="""
                **Pozycja pacjenta:** Na plecach
                
                **Procedura:**
                1. Jedną ręką chwyć piętę, drugą stabilizuj kolano
                2. Maksymalnie zegnij kolano
                3. Wykonaj rotację zewnętrzną + prostowanie (łąkotka przyśrodkowa)
                4. Wykonaj rotację wewnętrzną + prostowanie (łąkotka boczna)
                5. Słuchaj/wyczuwaj trzaski
                
                **Interpretacja:**
                - **Pozytywny:** Trzask z bólem podczas manewru
                - **Negatywny:** Brak trzasku lub ból bez trzasku
                """,
                sensitivity=0.70,
                specificity=0.71,
                interpretation={
                    "positive": "Uszkodzenie łąkotki prawdopodobne",
                    "negative": "Łąkotki prawdopodobnie nieuszkodzone"
                },
                module_type="knee",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test Thessaly",
                description="Nowoczesny test wykrywania uszkodzeń łąkotek",
                procedure="""
                **Pozycja pacjenta:** Stojąc na jednej nodze
                
                **Procedura:**
                1. Pacjent stoi na badanej nodze
                2. Kolano w 20° fleksji
                3. Pacjent wykonuje rotację wewnętrzną i zewnętrzną
                4. Powtórz test z kolanem w 5° fleksji
                5. Obserwuj ból i blokadę
                
                **Interpretacja:**
                - **Pozytywny:** Ból przyśrodkowy/boczny z uczuciem blokady
                - **Negatywny:** Brak bólu podczas rotacji
                """,
                sensitivity=0.90,
                specificity=0.97,
                interpretation={
                    "positive": "Uszkodzenie łąkotki wysoce prawdopodobne",
                    "negative": "Łąkotki prawdopodobnie nieuszkodzone"
                },
                module_type="knee",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test odchylenia kątowego (MCL/LCL)",
                description="Ocena więzadeł bocznych kolana",
                procedure="""
                **Pozycja pacjenta:** Na plecach
                
                **Procedura MCL (przyśrodkowe):**
                1. Kolano w 30° fleksji
                2. Jedną ręką stabilizuj udo, drugą chwyć kostkę
                3. Wykonaj stres kątowy (valgus stress)
                4. Oceń rozejście stawu po stronie przyśrodkowej
                
                **Procedura LCL (boczne):**
                - Analogicznie, ale wykonuj varus stress
                
                **Interpretacja:**
                - **Pozytywny:** Nadmierne rozejście stawu
                - **Negatywny:** Minimalne rozejście
                """,
                sensitivity=0.86,
                specificity=0.84,
                interpretation={
                    "positive": "Uszkodzenie więzadeł bocznych prawdopodobne",
                    "negative": "Więzadła boczne prawdopodobnie nieuszkodzone"
                },
                module_type="knee",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test kompresji rzepki",
                description="Ocena stawu rzepkowo-udowego",
                procedure="""
                **Pozycja pacjenta:** Na plecach, noga wyprostowana
                
                **Procedura:**
                1. Pacjent napina mięsień czworogłowy uda
                2. Naciśnij rzepkę w kierunku uda
                3. Poproś o utrzymanie napięcia mięśnia
                4. Oceń ból i możliwość utrzymania napięcia
                
                **Interpretacja:**
                - **Pozytywny:** Ból pod rzepką, niemożność utrzymania napięcia
                - **Negatywny:** Brak bólu, prawidłowe napięcie mięśnia
                """,
                sensitivity=0.39,
                specificity=0.67,
                interpretation={
                    "positive": "Patellofemoral pain syndrome możliwy",
                    "negative": "Nie wyklucza problemów rzepkowo-udowych"
                },
                module_type="knee",
                test_category="physical"
            )
        ]
    
    def _define_clinical_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Pittsburgh Knee Rules",
                "description": "Reguły określające wskazania do RTG kolana",
                "criteria": [
                    {
                        "description": "Wiek <12 lub >50 lat",
                        "field": "age_criteria",
                        "comparison": "boolean_true"
                    },
                    {
                        "description": "Niemożność obciążenia w SOR",
                        "field": "unable_to_bear_weight_er",
                        "comparison": "boolean_true"
                    }
                ],
                "outcome_positive": "Wskazane RTG kolana",
                "outcome_negative": "RTG kolana prawdopodobnie niepotrzebne",
                "sensitivity": 0.99,
                "specificity": 0.60
            }
        ]
    
    def _get_red_flags_list(self) -> List[str]:
        return [
            "Widoczna deformacja kolana",
            "Niemożność prostowania kolana (blokada)",
            "Znaczna niestabilność kolana we wszystkich płaszczyznach",
            "Brak tętna na stopie po urazie kolana",
            "Drętwienie lub niedowład stopy",
            "Zimna, blada stopa po urazie",
            "Podejrzenie zwichnięcia rzepki",
            "Znaczny wysięk z napięciem w stawie",
            "Gorączka z bólem stawu (podejrzenie infekcji)"
        ]
    
    def run_interview(self, patient: Patient, mode: str) -> Dict[str, Any]:
        """Przeprowadza wywiad dla kolana"""
        st.markdown("#### Mechanizm urazu i objawy")
        
        findings = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Mechanizm urazu
            mechanism = st.selectbox(
                "Mechanizm urazu:",
                [
                    "Kontakt z rotacją (pivot)",
                    "Bez kontaktu z rotacją", 
                    "Hiperextensja",
                    "Stres kątowy (valgus/varus)",
                    "Bezpośredni uraz przodu kolana",
                    "Uraz rzepki",
                    "Przeciążenie/overuse",
                    "Bez wyraźnego urazu",
                    "Nieznany"
                ],
                key="knee_mechanism"
            )
            findings['mechanism'] = mechanism
            
            # "Pop" podczas urazu
            pop_sound = st.radio(
                "Czy słyszałeś 'pop'/trzask podczas urazu?",
                ["Tak, wyraźny trzask", "Możliwe", "Nie", "Nie pamiętam"],
                key="knee_pop"
            )
            findings['pop_sound'] = pop_sound
            
            # Natychmiastowy obrzęk
            immediate_swelling = st.radio(
                "Obrzęk pojawił się:",
                ["Natychmiast (w ciągu minut)", "W ciągu godzin", "Następnego dnia", "Stopniowo", "Brak obrzęku"],
                key="knee_swelling_timing"
            )
            findings['immediate_swelling'] = immediate_swelling
        
        with col2:
            # Lokalizacja bólu
            pain_locations = st.multiselect(
                "Lokalizacja bólu:",
                [
                    "Przód kolana (anterior)",
                    "Tył kolana (posterior)",
                    "Strona przyśrodkowa",
                    "Strona boczna",
                    "Pod rzepką",
                    "Nad rzepką",
                    "Rozlany ból"
                ],
                key="knee_pain_location"
            )
            findings['pain_locations'] = pain_locations
            
            # Intensywność bólu
            pain_intensity = st.slider(
                "Intensywność bólu (NRS 0-10):",
                min_value=0,
                max_value=10,
                value=5,
                key="knee_pain_intensity"
            )
            findings['pain_intensity'] = pain_intensity
            
            # Uczucie niestabilności
            instability = st.radio(
                "Uczucie niestabilności kolana:",
                ["Nie", "Czasami przy określonych ruchach", "Często", "Ciągle"],
                key="knee_instability"
            )
            findings['instability'] = instability
        
        # Objawy funkcjonalne
        st.markdown("#### Objawy funkcjonalne")
        
        col1, col2 = st.columns(2)
        
        with col1:
            giving_way = st.checkbox(
                "Uczucie 'podłamania się' kolana",
                key="knee_giving_way"
            )
            findings['giving_way'] = giving_way
            
            locking = st.checkbox(
                "Blokada kolana (niemożność pełnego prostowania)",
                key="knee_locking"
            )
            findings['locking'] = locking
            
            catching = st.checkbox(
                "Uczucie 'zaczepienia' podczas ruchu",
                key="knee_catching"
            )
            findings['catching'] = catching
        
        with col2:
            stairs_difficulty = st.selectbox(
                "Trudności ze schodami:",
                ["Brak", "Tylko w górę", "Tylko w dół", "W obu kierunkach"],
                key="knee_stairs"
            )
            findings['stairs_difficulty'] = stairs_difficulty
            
            sports_activity = st.selectbox(
                "Możliwość aktywności sportowej:",
                ["Normalna", "Ograniczona", "Znacznie ograniczona", "Niemożliwa"],
                key="knee_sports"
            )
            findings['sports_activity'] = sports_activity
        
        # Historia medyczna
        st.markdown("#### Historia medyczna")
        
        col1, col2 = st.columns(2)
        
        with col1:
            previous_injuries = st.multiselect(
                "Poprzednie urazy kolana:",
                [
                    "Uszkodzenie ACL",
                    "Uszkodzenie PCL", 
                    "Uszkodzenie łąkotek",
                    "Uszkodzenie więzadeł bocznych",
                    "Zwichnięcie rzepki",
                    "Złamanie w obrębie kolana",
                    "Operacja kolana",
                    "Brak poprzednich urazów"
                ],
                key="knee_previous_injuries"
            )
            findings['previous_injuries'] = previous_injuries
        
        with col2:
            activity_level = st.selectbox(
                "Poziom aktywności przed urazem:",
                [
                    "Bardzo wysoki (sport wyczynowy)",
                    "Wysoki (regularne sporty)", 
                    "Umiarkowany (rekreacyjnie)",
                    "Niski (podstawowe czynności)",
                    "Bardzo niski (siedzący tryb życia)"
                ],
                key="knee_activity_level"
            )
            findings['activity_level'] = activity_level
        
        return {"interview": findings}
    
    def run_physical_examination(self, patient: Patient, mode: str) -> Dict[str, Any]:
        """Przeprowadza badanie fizykalne kolana"""
        findings = {}
        
        # Inspekcja
        st.markdown("#### 👁️ Inspekcja")
        
        col1, col2 = st.columns(2)
        
        with col1:
            swelling = st.selectbox(
                "Obrzęk/wysięk:",
                ["Brak", "Mały", "Umiarkowany", "Znaczny", "Napięty"],
                key="knee_swelling"
            )
            findings['swelling'] = swelling
            
            swelling_location = st.multiselect(
                "Lokalizacja obrzęku:",
                [
                    "Nadrzepkowy",
                    "Podrzepkowy",
                    "Przyśrodkowy",
                    "Boczny",
                    "Tylny (popliteal)",
                    "Rozlany"
                ],
                key="knee_swelling_location"
            )
            findings['swelling_location'] = swelling_location
            
            alignment = st.selectbox(
                "Ustawienie osi kończyny:",
                ["Prawidłowe", "Koślawość (valgus)", "Szpotawość (varus)", "Recurvatum"],
                key="knee_alignment"
            )
            findings['alignment'] = alignment
        
        with col2:
            muscle_atrophy = st.checkbox(
                "Atrofia mięśni (szczególnie VMO)",
                key="knee_atrophy"
            )
            findings['muscle_atrophy'] = muscle_atrophy
            
            ecchymosis = st.checkbox(
                "Krwiak/wybroczyny",
                key="knee_ecchymosis"
            )
            findings['ecchymosis'] = ecchymosis
            
            deformity = st.checkbox(
                "Deformacja widoczna",
                key="knee_deformity"
            )
            findings['deformity'] = deformity
        
        # Palpacja
        st.markdown("#### 👐 Palpacja")
        
        col1, col2 = st.columns(2)
        
        with col1:
            joint_line_tenderness = st.multiselect(
                "Tkliwość szczeliny stawowej:",
                ["Brak", "Przyśrodkowa", "Boczna", "Obie strony"],
                key="knee_joint_line"
            )
            findings['joint_line_tenderness'] = joint_line_tenderness
            
            patella_tenderness = st.checkbox(
                "Tkliwość rzepki",
                key="knee_patella_tenderness"
            )
            findings['patella_tenderness'] = patella_tenderness
            
            popliteal_tenderness = st.checkbox(
                "Tkliwość dołu podkolanowego",
                key="knee_popliteal_tenderness"
            )
            findings['popliteal_tenderness'] = popliteal_tenderness
        
        with col2:
            effusion_test = st.selectbox(
                "Test przemieszczania płynu:",
                ["Negatywny", "Trace", "1+", "2+", "3+"],
                key="knee_effusion"
            )
            findings['effusion_test'] = effusion_test
            
            patella_ballotement = st.checkbox(
                "Ballotement rzepki pozytywny",
                key="knee_ballotement"
            )
            findings['patella_ballotement'] = patella_ballotement
        
        # Zakres ruchu
        st.markdown("#### 📐 Zakres ruchu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            flexion_active = st.slider(
                "Fleksja czynna (stopnie):",
                min_value=0,
                max_value=150,
                value=130,
                key="knee_flexion_active"
            )
            findings['flexion_active'] = flexion_active
            
            flexion_passive = st.slider(
                "Fleksja bierna (stopnie):",
                min_value=0,
                max_value=150,
                value=135,
                key="knee_flexion_passive"
            )
            findings['flexion_passive'] = flexion_passive
        
        with col2:
            extension_deficit = st.slider(
                "Deficyt ekstensji (stopnie):",
                min_value=0,
                max_value=30,
                value=0,
                key="knee_extension_deficit"
            )
            findings['extension_deficit'] = extension_deficit
            
            hyperextension = st.slider(
                "Hyperextensja (stopnie):",
                min_value=0,
                max_value=15,
                value=5,
                key="knee_hyperextension"
            )
            findings['hyperextension'] = hyperextension
        
        # Testy specjalistyczne
        st.markdown("#### 🔬 Testy specjalistyczne")
        
        test_results = {}
        
        for test in self.diagnostic_tests:
            result = self.render_test_interface(test, mode)
            if result and result != "Nie wykonano":
                test_results[test.name] = result
                
                # Zapisz wynik testu do bazy danych
                if 'current_session' in st.session_state and st.session_state.current_session:
                    self.save_test_result(
                        st.session_state.current_session.id,
                        test.name,
                        result
                    )
        
        findings['test_results'] = test_results
        
        # Testy funkcjonalne
        st.markdown("#### 🏃 Testy funkcjonalne")
        
        col1, col2 = st.columns(2)
        
        with col1:
            single_leg_squat = st.selectbox(
                "Test przysiadu na jednej nodze:",
                ["Nie wykonano", "Prawidłowy", "Ból bez kompensacji", "Ból z kompensacją", "Niemożliwy"],
                key="knee_single_squat"
            )
            findings['single_leg_squat'] = single_leg_squat
            
            hop_test = st.selectbox(
                "Test skoku na jednej nodze:",
                ["Nie wykonano", "Prawidłowy", "Ograniczony", "Niemożliwy"],
                key="knee_hop_test"
            )
            findings['hop_test'] = hop_test
        
        with col2:
            duck_walk = st.selectbox(
                "Duck walk test:",
                ["Nie wykonano", "Prawidłowy", "Ograniczony", "Ból", "Niemożliwy"],
                key="knee_duck_walk"
            )
            findings['duck_walk'] = duck_walk
        
        return {"physical_exam": findings}
    
    def calculate_risk_scores(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Oblicza wskaźniki ryzyka dla kolana"""
        scores = {}
        
        # ACL Injury Score
        acl_score = 0
        
        if 'interview' in findings:
            interview = findings['interview']
            
            # Mechanizm urazu
            mechanism = interview.get('mechanism', '')
            if 'kontakt' in mechanism.lower() and 'rotacją' in mechanism:
                acl_score += 4
            elif 'bez kontakt' in mechanism.lower() and 'rotacją' in mechanism:
                acl_score += 5
            
            # Pop sound
            if interview.get('pop_sound') == "Tak, wyraźny trzask":
                acl_score += 3
            
            # Natychmiastowy obrzęk
            if interview.get('immediate_swelling') == "Natychmiast (w ciągu minut)":
                acl_score += 3
            
            # Niestabilność
            instability = interview.get('instability', 'Nie')
            if instability == "Ciągle":
                acl_score += 2
            elif instability in ["Często", "Czasami przy określonych ruchach"]:
                acl_score += 1
        
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            
            # Testy Lachmana i szuflady
            test_results = exam.get('test_results', {})
            if test_results.get('Test Lachmana (ACL)') == 'Pozytywny':
                acl_score += 6
            if test_results.get('Test szuflady przedniej (ACL)') == 'Pozytywny':
                acl_score += 4
            
            # Wysięk
            if exam.get('swelling') in ['Znaczny', 'Napięty']:
                acl_score += 2
        
        scores['acl_injury_risk'] = min(acl_score, 25)  # Max 25 points
        
        # Meniscus Injury Score
        meniscus_score = 0
        
        if 'interview' in findings:
            interview = findings['interview']
            
            # Mechanizm
            if 'rotacją' in interview.get('mechanism', '').lower():
                meniscus_score += 2
            
            # Blokada
            if interview.get('locking', False):
                meniscus_score += 4
            
            # Catching
            if interview.get('catching', False):
                meniscus_score += 2
        
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            
            # Tkliwość szczeliny stawowej
            joint_line = exam.get('joint_line_tenderness', [])
            if any(side in joint_line for side in ['Przyśrodkowa', 'Boczna']):
                meniscus_score += 3
            
            # Testy McMurraya i Thessaly
            test_results = exam.get('test_results', {})
            if test_results.get('Test McMurraya (łąkotki)') == 'Pozytywny':
                meniscus_score += 3
            if test_results.get('Test Thessaly') == 'Pozytywny':
                meniscus_score += 5
        
        scores['meniscus_injury_risk'] = min(meniscus_score, 20)  # Max 20 points
        
        # Patellofemoral Score
        pf_score = 0
        
        if 'interview' in findings:
            interview = findings['interview']
            
            # Lokalizacja bólu
            pain_locations = interview.get('pain_locations', [])
            if 'Pod rzepką' in pain_locations or 'Nad rzepką' in pain_locations:
                pf_score += 3
            
            # Trudności ze schodami
            stairs = interview.get('stairs_difficulty', 'Brak')
            if stairs == 'W obu kierunkach':
                pf_score += 2
            elif stairs in ['Tylko w górę', 'Tylko w dół']:
                pf_score += 1
        
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            
            # Tkliwość rzepki
            if exam.get('patella_tenderness', False):
                pf_score += 2
            
            # Test kompresji rzepki
            test_results = exam.get('test_results', {})
            if test_results.get('Test kompresji rzepki') == 'Pozytywny':
                pf_score += 3
        
        scores['patellofemoral_risk'] = min(pf_score, 15)  # Max 15 points
        
        return scores
    
    def generate_diagnosis(self, findings: Dict[str, Any]) -> Diagnosis:
        """Generuje diagnozę dla kolana"""
        risk_scores = findings.get('risk_scores', {})
        
        # Analiza wyników
        acl_risk = risk_scores.get('acl_injury_risk', 0)
        meniscus_risk = risk_scores.get('meniscus_injury_risk', 0)
        pf_risk = risk_scores.get('patellofemoral_risk', 0)
        
        diagnoses = []
        
        # Diagnoza na podstawie score
        if acl_risk >= 12:
            diagnoses.append({
                'name': 'Uszkodzenie więzadła krzyżowego przedniego (ACL)',
                'confidence': min(95, acl_risk * 4),
                'icd10': 'S83.5'
            })
        elif acl_risk >= 8:
            diagnoses.append({
                'name': 'Podejrzenie uszkodzenia ACL',
                'confidence': min(80, acl_risk * 5),
                'icd10': 'S83.5'
            })
        
        if meniscus_risk >= 10:
            diagnoses.append({
                'name': 'Uszkodzenie łąkotki',
                'confidence': min(90, meniscus_risk * 4.5),
                'icd10': 'S83.2'
            })
        elif meniscus_risk >= 6:
            diagnoses.append({
                'name': 'Podejrzenie uszkodzenia łąkotki',
                'confidence': min(75, meniscus_risk * 6),
                'icd10': 'S83.2'
            })
        
        if pf_risk >= 8:
            diagnoses.append({
                'name': 'Zespół bólu rzepkowo-udowego',
                'confidence': min(85, pf_risk * 5),
                'icd10': 'M25.56'
            })
        
        # Sprawdź inne specific findings
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            test_results = exam.get('test_results', {})
            
            if test_results.get('Test szuflady tylnej (PCL)') == 'Pozytywny':
                diagnoses.append({
                    'name': 'Uszkodzenie więzadła krzyżowego tylnego (PCL)',
                    'confidence': 85,
                    'icd10': 'S83.5'
                })
            
            if test_results.get('Test odchylenia kątowego (MCL/LCL)') == 'Pozytywny':
                diagnoses.append({
                    'name': 'Uszkodzenie więzadeł bocznych kolana',
                    'confidence': 80,
                    'icd10': 'S83.4'
                })
        
        # Domyślna diagnoza
        if not diagnoses:
            diagnoses.append({
                'name': 'Nieokreślone uszkodzenie kolana',
                'confidence': 60,
                'icd10': 'S83.9'
            })
        
        # Sortuj według confidence
        diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
        primary_diagnosis = diagnoses[0]
        
        # Generuj rekomendacje
        treatment_options = self._generate_treatment_recommendations(primary_diagnosis['name'], findings)
        referral_recommendations = self._generate_referral_recommendations(primary_diagnosis['name'], findings)
        
        return Diagnosis(
            name=primary_diagnosis['name'],
            icd10_code=primary_diagnosis.get('icd10'),
            confidence=primary_diagnosis['confidence'],
            evidence_level="high" if primary_diagnosis['confidence'] > 80 else "moderate" if primary_diagnosis['confidence'] > 60 else "low",
            differential_diagnoses=[d['name'] for d in diagnoses[1:5]],
            treatment_options=treatment_options,
            referral_recommendations=referral_recommendations
        )
    
    def _generate_treatment_recommendations(self, diagnosis: str, findings: Dict[str, Any]) -> List[str]:
        """Generuje rekomendacje leczenia dla kolana"""
        treatments = []
        
        if "ACL" in diagnosis:
            treatments = [
                "Konsultacja ortopedyczna - MRI kolana",
                "Decyzja o leczeniu operacyjnym vs. zachowawczym",
                "Wczesna fizjoterapia - kontrola obrzęku i ROM",
                "Protokół rehabilitacji ACL (pre-hab jeśli operacja)",
                "Orteza stabilizująca w fazie ostrej"
            ]
        
        elif "łąkotki" in diagnosis or "łąkotka" in diagnosis:
            treatments = [
                "Fizjoterapia - wzmacnianie czworogłowego i stabilizacja",
                "Modyfikacja aktywności - unikanie rotacji pod obciążeniem",
                "NLPZ w fazie ostrej (jeśli brak przeciwwskazań)",
                "Rozważenie MRI przy braku poprawy po 4-6 tygodniach",
                "Konsultacja ortopedyczna przy mechanicznych objawach"
            ]
        
        elif "rzepkowo-udowego" in diagnosis:
            treatments = [
                "Fizjoterapia - wzmacnianie VMO i gluteals",
                "Korekja wzorców ruchowych",
                "Tejpowanie rzepki",
                "Modyfikacja aktywności - unikanie deep squats",
                "Ortezowanie lub insole przy problemach biomechanicznych"
            ]
        
        elif "więzadeł bocznych" in diagnosis:
            treatments = [
                "Orteza ograniczająca ruchy kątowe",
                "Fizjoterapia - ROM i wzmacnianie",
                "Stopniowa progresja obciążenia",
                "Ocena stabilności po 6-8 tygodniach",
                "Rozważenie operacji przy niestabilności III stopnia"
            ]
        
        else:
            treatments = [
                "Symptomatic treatment - ice, elevation",
                "Fizjoterapia według objawów",
                "Monitorowanie postępu",
                "Dodatkowa diagnostyka przy braku poprawy"
            ]
        
        return treatments
    
    def _generate_referral_recommendations(self, diagnosis: str, findings: Dict[str, Any]) -> List[str]:
        """Generuje rekomendacje skierowań dla kolana"""
        referrals = []
        
        if "ACL" in diagnosis and "Uszkodzenie" in diagnosis:
            referrals.append("Pilna konsultacja ortopedyczna + MRI")
        
        if "łąkotki" in diagnosis and "Uszkodzenie" in diagnosis:
            referrals.append("MRI kolana + konsultacja ortopedyczna")
        
        if "PCL" in diagnosis:
            referrals.append("Konsultacja ortopedyczna + zaawansowane obrazowanie")
        
        if "więzadeł bocznych" in diagnosis:
            referrals.append("Ocena ortopedyczna stabilności")
        
        # Check for mechanical symptoms
        if 'interview' in findings:
            interview = findings['interview']
            if interview.get('locking', False):
                referrals.append("MRI - wykluczenie loose body/bucket handle tear")
        
        # No urgent referrals
        if not referrals:
            referrals.append("Obserwacja, fizjoterapia, kontrola za 2-4 tygodnie")
        
        return referrals
