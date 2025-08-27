import streamlit as st
from typing import Dict, List, Any, Optional
from .base_module import BaseModule, AssessmentStep
from ..database.models import Patient, DiagnosticTest, Diagnosis
import json

class AnkleModule(BaseModule):
    """Moduł diagnostyczny dla stawu skokowego"""
    
    def __init__(self):
        super().__init__("Staw skokowy", "🦶")
    
    def _define_assessment_steps(self) -> List[AssessmentStep]:
        return [
            AssessmentStep("red_flags", "Czerwone flagi", "Kontrola objawów alarmowych"),
            AssessmentStep("history", "Wywiad", "Szczegółowy wywiad medyczny"),
            AssessmentStep("physical", "Badanie fizykalne", "Testy stabilności i funkcji"),
            AssessmentStep("ottawa", "Reguły Ottawy", "Wykluczenie złamań"),
            AssessmentStep("diagnosis", "Diagnoza", "Analiza wyników i diagnoza")
        ]
    
    def _define_diagnostic_tests(self) -> List[DiagnosticTest]:
        return [
            DiagnosticTest(
                name="Test szuflady przedniej (ATFL)",
                description="Ocena integralności więzadła strzałkowo-skokowego przedniego",
                procedure="""
                **Pozycja pacjenta:** Na plecach lub siedząc na krawędzi łóżka
                
                **Procedura:**
                1. Stopa w pozycji lekko podeszwowej fleksji (10-15°)
                2. Jedną ręką stabilizuj golę od przodu
                3. Drugą ręką chwyć piętę od tyłu
                4. Wykonaj delikatny ruch pięty do przodu względem goleni
                5. Oceń przesunięcie i czucie końcowe
                
                **Interpretacja:**
                - **Pozytywny:** Zwiększona ruchomość >4mm, brak twardego czucia końcowego
                - **Negatywny:** Normalna ruchomość, twarde czucie końcowe
                """,
                sensitivity=0.58,
                specificity=0.83,
                interpretation={
                    "positive": "Uszkodzenie ATFL prawdopodobne",
                    "negative": "ATFL prawdopodobnie nieuszkodzone"
                },
                module_type="ankle",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test talar tilt (CFL)",
                description="Ocena integralności więzadła piętowo-strzałkowego",
                procedure="""
                **Pozycja pacjenta:** Na boku (badana noga na górze) lub na plecach
                
                **Procedura:**
                1. Stopa w pozycji neutralnej (90°)
                2. Jedną ręką stabilizuj golę
                3. Drugą ręką chwyć stopę od strony przyśrodkowej
                4. Wykonaj inwersję stopy z jednoczesnym adduktem
                5. Oceń stopień nachylenia talusa w widłach kostki
                
                **Interpretacja:**
                - **Pozytywny:** Nachylenie >10° różnicy między stronami
                - **Negatywny:** Różnica <5° między stronami
                """,
                sensitivity=0.52,
                specificity=0.84,
                interpretation={
                    "positive": "Uszkodzenie CFL prawdopodobne",
                    "negative": "CFL prawdopodobnie nieuszkodzone"
                },
                module_type="ankle",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test Thompson'a",
                description="Wykluczenie zerwania ścięgna Achillesa",
                procedure="""
                **Pozycja pacjenta:** Na brzuchu, stopa zwisająca poza krawędzią łóżka
                
                **Procedura:**
                1. Pacjent leży na brzuchu
                2. Stopa zwisa swobodnie poza krawędzią
                3. Ściskaj mięsień trójgłowy łydki
                4. Obserwuj ruch stopy w kierunku podeszwowej fleksji
                
                **Interpretacja:**
                - **Negatywny (prawidłowy):** Podeszwowa fleksja stopy
                - **Pozytywny:** Brak ruchu stopy = podejrzenie zerwania ścięgna
                """,
                sensitivity=0.96,
                specificity=0.93,
                interpretation={
                    "positive": "Wysokie podejrzenie zerwania ścięgna Achillesa",
                    "negative": "Ścięgno Achillesa prawdopodobnie nieuszkodzone"
                },
                module_type="ankle",
                test_category="physical"
            ),
            DiagnosticTest(
                name="Test kompresji goleni (Squeeze)",
                description="Wykluczenie uszkodzenia syndesmosis",
                procedure="""
                **Pozycja pacjenta:** Na plecach, noga wyprostowana
                
                **Procedura:**
                1. Chwytaj golę obiema rękami w 1/3 środkowej
                2. Wykonaj kompresję kości strzałkowej ku piszczelowej
                3. Obserwuj reakcję pacjenta
                4. Zwróć uwagę na lokalizację bólu
                
                **Interpretacja:**
                - **Pozytywny:** Ból w okolicy stawu skokowego (dystalnie)
                - **Negatywny:** Brak bólu w stawie skokowym
                """,
                sensitivity=0.30,
                specificity=0.93,
                interpretation={
                    "positive": "Podejrzenie uszkodzenia syndesmosis",
                    "negative": "Syndesmosis prawdopodobnie nieuszkodzona"
                },
                module_type="ankle",
                test_category="physical"
            )
        ]
    
    def _define_clinical_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Ottawa Ankle Rules",
                "description": "Reguły określające wskazania do RTG kostki",
                "criteria": [
                    {
                        "description": "Niemożność obciążenia (4 kroki) bezpośrednio po urazie i teraz",
                        "field": "unable_to_bear_weight",
                        "comparison": "boolean_true"
                    },
                    {
                        "description": "Tkliwość nad końcem dystalnym kości strzałkowej (6cm)",
                        "field": "tender_lateral_malleolus",
                        "comparison": "boolean_true"
                    },
                    {
                        "description": "Tkliwość nad końcem dystalnym kości piszczelowej (6cm)",
                        "field": "tender_medial_malleolus",
                        "comparison": "boolean_true"
                    }
                ],
                "outcome_positive": "Wskazane RTG kostki",
                "outcome_negative": "RTG kostki prawdopodobnie niepotrzebne",
                "sensitivity": 0.99,
                "specificity": 0.40
            },
            {
                "name": "Ottawa Foot Rules",
                "description": "Reguły określające wskazania do RTG stopy",
                "criteria": [
                    {
                        "description": "Niemożność obciążenia (4 kroki) bezpośrednio po urazie i teraz",
                        "field": "unable_to_bear_weight",
                        "comparison": "boolean_true"
                    },
                    {
                        "description": "Tkliwość nad kością łódkowatą",
                        "field": "tender_navicular",
                        "comparison": "boolean_true"
                    },
                    {
                        "description": "Tkliwość nad podstawą 5. kości śródstopia",
                        "field": "tender_base_5th_metatarsal",
                        "comparison": "boolean_true"
                    }
                ],
                "outcome_positive": "Wskazane RTG stopy",
                "outcome_negative": "RTG stopy prawdopodobnie niepotrzebne",
                "sensitivity": 0.99,
                "specificity": 0.79
            }
        ]
    
    def _get_red_flags_list(self) -> List[str]:
        return [
            "Widoczna deformacja kości/stawu",
            "Otwarta rana z przebiciem skóry", 
            "Bladość, zimno lub siniec stopy",
            "Brak tętna na stopie (a. dorsalis pedis, a. tibialis posterior)",
            "Drętwienie całej stopy lub znaczne zaburzenia czucia",
            "Niemożność poruszenia palcami stopy",
            "Bardzo silny ból (9-10/10) oporny na analgetyki",
            "Szybko narastający obrzęk całej stopy/goleni",
            "Podejrzenie zespołu ciasnoty przedziałów"
        ]
    
    def run_interview(self, patient: Patient, mode: str) -> Dict[str, Any]:
        """Przeprowadza wywiad dla stawu skokowego"""
        st.markdown("#### Mechanizm urazu i objawy")
        
        findings = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Mechanizm urazu
            mechanism = st.selectbox(
                "Mechanizm urazu:",
                [
                    "Inwersja (skręcenie do wewnątrz)",
                    "Ewersja (skręcenie na zewnątrz)", 
                    "Dorsiflexja + rotacja zewnętrzna",
                    "Nadmierna plantarflexion",
                    "Bezpośredni uraz/uderzenie",
                    "Brak wyraźnego urazu",
                    "Nieznany"
                ],
                key="ankle_mechanism"
            )
            findings['mechanism'] = mechanism
            
            # Czas od urazu
            time_since_injury = st.selectbox(
                "Czas od urazu:",
                [
                    "Ostry (0-72h)",
                    "Podostrych (3-14 dni)",
                    "Przewlekły (>2 tygodnie)"
                ],
                key="ankle_time_since"
            )
            findings['time_since_injury'] = time_since_injury
            
            # Lokalizacja bólu
            pain_locations = st.multiselect(
                "Lokalizacja bólu:",
                [
                    "Kostka boczna (lateral)",
                    "Kostka przyśrodkowa (medial)",
                    "Przód stawu (anterior)",
                    "Tył stawu/Achilles (posterior)",
                    "Podeszwa",
                    "Rozlany ból"
                ],
                key="ankle_pain_location"
            )
            findings['pain_locations'] = pain_locations
        
        with col2:
            # Intensywność bólu
            pain_intensity = st.slider(
                "Intensywność bólu (NRS 0-10):",
                min_value=0,
                max_value=10,
                value=5,
                key="ankle_pain_intensity"
            )
            findings['pain_intensity'] = pain_intensity
            
            # Charakter bólu
            pain_character = st.multiselect(
                "Charakter bólu:",
                [
                    "Ostry, kłujący",
                    "Tępy, ściskający", 
                    "Pulsujący",
                    "Promieniujący",
                    "Palący",
                    "Stały",
                    "Okresowy"
                ],
                key="ankle_pain_character"
            )
            findings['pain_character'] = pain_character
            
            # Czynniki nasilające/łagodzące
            aggravating_factors = st.multiselect(
                "Co nasila ból:",
                [
                    "Chodzenie",
                    "Stanie",
                    "Bieganie",
                    "Schody w górę",
                    "Schody w dół",
                    "Rotacja stopy",
                    "Dorsiflexion",
                    "Plantarflexion",
                    "Rano po wstaniu",
                    "Wieczorem"
                ],
                key="ankle_aggravating"
            )
            findings['aggravating_factors'] = aggravating_factors
        
        # Historia medyczna specyficzna dla kostki
        st.markdown("#### Historia medyczna")
        
        col1, col2 = st.columns(2)
        
        with col1:
            previous_injuries = st.multiselect(
                "Poprzednie urazy kostki:",
                [
                    "Skręcenie kostki bocznej",
                    "Skręcenie kostki przyśrodkowej",
                    "Złamanie kostki",
                    "Zerwanie ścięgna Achillesa",
                    "Operacja kostki",
                    "Brak poprzednich urazów"
                ],
                key="ankle_previous_injuries"
            )
            findings['previous_injuries'] = previous_injuries
            
            chronic_instability = st.checkbox(
                "Chronicznie niestabilna kostka (powtarzające się skręcenia)",
                key="ankle_chronic_instability"
            )
            findings['chronic_instability'] = chronic_instability
        
        with col2:
            activity_level = st.selectbox(
                "Poziom aktywności fizycznej:",
                [
                    "Bardzo wysoki (sport wyczynowy)",
                    "Wysoki (regularne sporty)",
                    "Umiarkowany (rekreacyjnie)",
                    "Niski (podstawowe czynności)",
                    "Bardzo niski (siedzący tryb życia)"
                ],
                key="ankle_activity_level"
            )
            findings['activity_level'] = activity_level
            
            footwear = st.text_input(
                "Rodzaj obuwia podczas urazu:",
                placeholder="Buty sportowe, szpilki, sandały...",
                key="ankle_footwear"
            )
            findings['footwear'] = footwear
        
        return {"interview": findings}
    
    def run_physical_examination(self, patient: Patient, mode: str) -> Dict[str, Any]:
        """Przeprowadza badanie fizykalne stawu skokowego"""
        findings = {}
        
        # Inspekcja
        st.markdown("#### 👁️ Inspekcja")
        
        col1, col2 = st.columns(2)
        
        with col1:
            swelling = st.selectbox(
                "Obrzęk:",
                ["Brak", "Mały", "Umiarkowany", "Znaczny"],
                key="ankle_swelling"
            )
            findings['swelling'] = swelling
            
            swelling_location = st.multiselect(
                "Lokalizacja obrzęku:",
                [
                    "Kostka boczna",
                    "Kostka przyśrodkowa", 
                    "Przód stawu",
                    "Tył stawu",
                    "Rozlany"
                ],
                key="ankle_swelling_location"
            )
            findings['swelling_location'] = swelling_location
        
        with col2:
            ecchymosis = st.selectbox(
                "Krwiak/wybroczyny:",
                ["Brak", "Małe", "Umiarkowane", "Rozległe"],
                key="ankle_ecchymosis"
            )
            findings['ecchymosis'] = ecchymosis
            
            deformity = st.checkbox(
                "Deformacja widoczna",
                key="ankle_deformity"
            )
            findings['deformity'] = deformity
        
        # Palpacja
        st.markdown("#### 👐 Palpacja")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lateral_tenderness = st.checkbox(
                "Tkliwość kostki bocznej",
                key="ankle_lateral_tenderness"
            )
            findings['lateral_tenderness'] = lateral_tenderness
            
            medial_tenderness = st.checkbox(
                "Tkliwość kostki przyśrodkowej",
                key="ankle_medial_tenderness"
            )
            findings['medial_tenderness'] = medial_tenderness
            
            achilles_tenderness = st.checkbox(
                "Tkliwość ścięgna Achillesa",
                key="ankle_achilles_tenderness"
            )
            findings['achilles_tenderness'] = achilles_tenderness
        
        with col2:
            # Reguły Ottawy - szczegółowa palpacja
            tender_lateral_malleolus = st.checkbox(
                "Tkliwość końca dystalnego kości strzałkowej (6cm)",
                key="tender_lateral_malleolus"
            )
            findings['tender_lateral_malleolus'] = tender_lateral_malleolus
            
            tender_medial_malleolus = st.checkbox(
                "Tkliwość końca dystalnego kości piszczelowej (6cm)",
                key="tender_medial_malleolus"
            )
            findings['tender_medial_malleolus'] = tender_medial_malleolus
            
            tender_navicular = st.checkbox(
                "Tkliwość kości łódkowatej",
                key="tender_navicular"
            )
            findings['tender_navicular'] = tender_navicular
            
            tender_base_5th_metatarsal = st.checkbox(
                "Tkliwość podstawy 5. kości śródstopia",
                key="tender_base_5th_metatarsal"
            )
            findings['tender_base_5th_metatarsal'] = tender_base_5th_metatarsal
        
        # Testy funkcjonalne
        st.markdown("#### 🚶 Testy funkcjonalne")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight_bearing = st.selectbox(
                "Możliwość obciążenia:",
                [
                    "Pełne obciążenie bez bólu",
                    "Pełne obciążenie z bólem",
                    "Częściowe obciążenie",
                    "Niemożność obciążenia"
                ],
                key="ankle_weight_bearing"
            )
            findings['weight_bearing'] = weight_bearing
            
            unable_to_bear_weight = st.checkbox(
                "Niemożność przejścia 4 kroków teraz i bezpośrednio po urazie",
                key="unable_to_bear_weight"
            )
            findings['unable_to_bear_weight'] = unable_to_bear_weight
        
        with col2:
            rom_dorsiflexion = st.slider(
                "Zakres dorsiflexion (stopnie):",
                min_value=0,
                max_value=30,
                value=15,
                key="ankle_rom_dorsiflexion"
            )
            findings['rom_dorsiflexion'] = rom_dorsiflexion
            
            rom_plantarflexion = st.slider(
                "Zakres plantarflexion (stopnie):",
                min_value=0,
                max_value=50,
                value=30,
                key="ankle_rom_plantarflexion"
            )
            findings['rom_plantarflexion'] = rom_plantarflexion
        
        # Testy stabilności
        st.markdown("#### 🔬 Testy stabilności")
        
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
        
        return {"physical_exam": findings}
    
    def calculate_risk_scores(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Oblicza wskaźniki ryzyka dla stawu skokowego"""
        scores = {}
        
        # Score dla skręcenia bocznego
        lateral_sprain_score = 0
        
        if 'interview' in findings:
            interview = findings['interview']
            
            # Mechanizm inwersyjny
            if 'Inwersja' in interview.get('mechanism', ''):
                lateral_sprain_score += 3
            
            # Lokalizacja bólu lateralna
            if 'Kostka boczna (lateral)' in interview.get('pain_locations', []):
                lateral_sprain_score += 2
            
            # Intensywność bólu
            pain_intensity = interview.get('pain_intensity', 0)
            if pain_intensity >= 7:
                lateral_sprain_score += 2
            elif pain_intensity >= 4:
                lateral_sprain_score += 1
        
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            
            # Obrzęk
            swelling = exam.get('swelling', 'Brak')
            if swelling == 'Znaczny':
                lateral_sprain_score += 3
            elif swelling == 'Umiarkowany':
                lateral_sprain_score += 2
            elif swelling == 'Mały':
                lateral_sprain_score += 1
            
            # Krwiak
            ecchymosis = exam.get('ecchymosis', 'Brak')
            if ecchymosis == 'Rozległe':
                lateral_sprain_score += 2
            elif ecchymosis in ['Umiarkowane', 'Małe']:
                lateral_sprain_score += 1
            
            # Tkliwość lateralna
            if exam.get('lateral_tenderness', False):
                lateral_sprain_score += 2
            
            # Testy stabilności
            test_results = exam.get('test_results', {})
            if test_results.get('Test szuflady przedniej (ATFL)') == 'Pozytywny':
                lateral_sprain_score += 4
            if test_results.get('Test talar tilt (CFL)') == 'Pozytywny':
                lateral_sprain_score += 3
        
        scores['lateral_sprain_risk'] = min(lateral_sprain_score, 20)  # Max 20 points
        
        # Score dla Achillesa
        achilles_rupture_score = 0
        
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            test_results = exam.get('test_results', {})
            
            if test_results.get("Test Thompson'a") == 'Pozytywny':
                achilles_rupture_score += 8
            
            if exam.get('achilles_tenderness', False):
                achilles_rupture_score += 2
            
            if exam.get('unable_to_bear_weight', False):
                achilles_rupture_score += 3
        
        scores['achilles_rupture_risk'] = min(achilles_rupture_score, 15)  # Max 15 points
        
        # Score według reguł Ottawy
        ottawa_score = 0
        
        if 'physical_exam' in findings:
            exam = findings['physical_exam']
            
            if exam.get('unable_to_bear_weight', False):
                ottawa_score += 1
            if exam.get('tender_lateral_malleolus', False):
                ottawa_score += 1
            if exam.get('tender_medial_malleolus', False):
                ottawa_score += 1
            if exam.get('tender_navicular', False):
                ottawa_score += 1
            if exam.get('tender_base_5th_metatarsal', False):
                ottawa_score += 1
        
        scores['ottawa_fracture_risk'] = ottawa_score
        
        return scores
    
    def generate_diagnosis(self, findings: Dict[str, Any]) -> Diagnosis:
        """Generuje diagnozę dla stawu skokowego"""
        risk_scores = findings.get('risk_scores', {})
        
        # Analiza wyników
        lateral_sprain_risk = risk_scores.get('lateral_sprain_risk', 0)
        achilles_rupture_risk = risk_scores.get('achilles_rupture_risk', 0)
        ottawa_risk = risk_scores.get('ottawa_fracture_risk', 0)
        
        diagnoses = []
        
        # Diagnoza główna na podstawie najwyższego score
        if ottawa_risk > 0:
            diagnoses.append({
                'name': 'Podejrzenie złamania (wskazania do RTG)',
                'confidence': min(95, ottawa_risk * 20),
                'icd10': 'S82-S99'
            })
        
        if achilles_rupture_risk >= 6:
            diagnoses.append({
                'name': 'Podejrzenie zerwania ścięgna Achillesa',
                'confidence': min(95, achilles_rupture_risk * 6),
                'icd10': 'S86.0'
            })
        
        if lateral_sprain_risk >= 10:
            diagnoses.append({
                'name': 'Skręcenie więzadeł bocznych stawu skokowego - stopień III',
                'confidence': min(90, lateral_sprain_risk * 4),
                'icd10': 'S93.4'
            })
        elif lateral_sprain_risk >= 6:
            diagnoses.append({
                'name': 'Skręcenie więzadeł bocznych stawu skokowego - stopień II',
                'confidence': min(85, lateral_sprain_risk * 5),
                'icd10': 'S93.4'
            })
        elif lateral_sprain_risk >= 3:
            diagnoses.append({
                'name': 'Skręcenie więzadeł bocznych stawu skokowego - stopień I',
                'confidence': min(80, lateral_sprain_risk * 6),
                'icd10': 'S93.4'
            })
        
        # Domyślna diagnoza jeśli brak wyraźnych wskazań
        if not diagnoses:
            diagnoses.append({
                'name': 'Nieokreślone uszkodzenie stawu skokowego',
                'confidence': 60,
                'icd10': 'S99.9'
            })
        
        # Sortuj według confidence
        diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
        primary_diagnosis = diagnoses[0]
        
        # Generuj rekomendacje leczenia
        treatment_options = self._generate_treatment_recommendations(primary_diagnosis['name'], findings)
        
        # Generuj skierowania
        referral_recommendations = self._generate_referral_recommendations(primary_diagnosis['name'], findings)
        
        return Diagnosis(
            name=primary_diagnosis['name'],
            icd10_code=primary_diagnosis.get('icd10'),
            confidence=primary_diagnosis['confidence'],
            evidence_level="moderate" if primary_diagnosis['confidence'] > 70 else "low",
            differential_diagnoses=[d['name'] for d in diagnoses[1:5]],
            treatment_options=treatment_options,
            referral_recommendations=referral_recommendations
        )
    
    def _generate_treatment_recommendations(self, diagnosis: str, findings: Dict[str, Any]) -> List[str]:
        """Generuje rekomendacje leczenia"""
        treatments = []
        
        if "stopień I" in diagnosis:
            treatments = [
                "RICE protocol (Rest, Ice, Compression, Elevation) przez 48-72h",
                "Wczesna mobilizacja w zakresie bez bólu",
                "Ćwiczenia propriocepcyjne od 3-5 dnia",
                "Stopniowy powrót do aktywności w 1-2 tygodnie",
                "Tejpowanie funkcjonalne lub orteza przez pierwsze tygodnie"
            ]
        
        elif "stopień II" in diagnosis:
            treatments = [
                "RICE protocol przez 3-5 dni",
                "Częściowe unieruchomienie (orteza/tape) przez 1-2 tygodnie",
                "Fizjoterapia: mobilizacja, wzmacnianie, propriocepcja",
                "Stopniowa progresja obciążenia",
                "Powrót do sportu za 2-4 tygodnie"
            ]
        
        elif "stopień III" in diagnosis:
            treatments = [
                "Konsultacja ortopedyczna - rozważenie leczenia operacyjnego",
                "Unieruchomienie w ortezie przez 2-3 tygodnie",
                "Intensywna rehabilitacja 6-12 tygodni",
                "Trening neuromotoryczny i kontrola stabilności",
                "Powrót do sportu za 3-6 miesięcy"
            ]
        
        elif "Achillesa" in diagnosis:
            treatments = [
                "PILNA konsultacja ortopedyczna",
                "Unieruchomienie w pozycji plantarflexion (but/orteza)",
                "Decyzja o leczeniu operacyjnym vs. zachowawczym",
                "Protokół rehabilitacji 4-6 miesięcy",
                "Stopniowy powrót do pełnej aktywności"
            ]
        
        elif "złamania" in diagnosis:
            treatments = [
                "RTG w dwóch projekcjach",
                "Konsultacja ortopedyczna",
                "Unieruchomienie do czasu wykluczenia złamania",
                "Analgetyki według potrzeb",
                "Dalsze postępowanie według obrazowania"
            ]
        
        else:
            treatments = [
                "Obserwacja i monitorowanie objawów",
                "Modyfikacja aktywności według tolerancji bólu",
                "Fizjoterapia według potrzeb",
                "Kontrola za 1-2 tygodnie"
            ]
        
        return treatments
    
    def _generate_referral_recommendations(self, diagnosis: str, findings: Dict[str, Any]) -> List[str]:
        """Generuje rekomendacje skierowań"""
        referrals = []
        
        if "złamania" in diagnosis:
            referrals.append("PILNE skierowanie na RTG + konsultacja ortopedyczna")
        
        if "Achillesa" in diagnosis:
            referrals.append("PILNA konsultacja ortopedyczna + USG ścięgna")
        
        if "stopień III" in diagnosis:
            referrals.append("Konsultacja ortopedyczna w ciągu 1-2 tygodni")
        
        risk_scores = findings.get('risk_scores', {})
        if risk_scores.get('ottawa_fracture_risk', 0) > 0:
            referrals.append("RTG według reguł Ottawy")
        
        # Brak pilnych skierowań
        if not referrals:
            referrals.append("Obserwacja, kontrola u fizjoterapeuty za 1 tydzień")
        
        return referrals
