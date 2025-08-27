from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import streamlit as st
from ..database.models import Patient, DiagnosisSession, TestResult, DiagnosticTest, Diagnosis

@dataclass
class AssessmentStep:
    """Krok w procesie oceny"""
    name: str
    title: str
    description: str
    required: bool = True
    completed: bool = False

class BaseModule(ABC):
    """Bazowa klasa dla wszystkich modułów diagnostycznych"""
    
    def __init__(self, module_name: str, module_icon: str):
        self.module_name = module_name
        self.module_icon = module_icon
        self.assessment_steps = self._define_assessment_steps()
        self.diagnostic_tests = self._define_diagnostic_tests()
        self.clinical_rules = self._define_clinical_rules()
        self.current_findings = {}
    
    @abstractmethod
    def _define_assessment_steps(self) -> List[AssessmentStep]:
        """Definiuje kroki oceny dla modułu"""
        pass
    
    @abstractmethod
    def _define_diagnostic_tests(self) -> List[DiagnosticTest]:
        """Definiuje testy diagnostyczne dla modułu"""
        pass
    
    @abstractmethod
    def _define_clinical_rules(self) -> List[Dict[str, Any]]:
        """Definiuje reguły kliniczne dla modułu"""
        pass
    
    @abstractmethod
    def run_interview(self, patient: Patient, mode: str) -> Dict[str, Any]:
        """Przeprowadza wywiad medyczny"""
        pass
    
    @abstractmethod
    def run_physical_examination(self, patient: Patient, mode: str) -> Dict[str, Any]:
        """Przeprowadza badanie fizykalne"""
        pass
    
    @abstractmethod
    def calculate_risk_scores(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Oblicza wskaźniki ryzyka"""
        pass
    
    @abstractmethod
    def generate_diagnosis(self, findings: Dict[str, Any]) -> Diagnosis:
        """Generuje diagnozę na podstawie wyników"""
        pass
    
    def run_assessment(self, patient: Patient, session: DiagnosisSession, mode: str) -> Dict[str, Any]:
        """Główna funkcja przeprowadzająca pełną ocenę"""
        st.markdown(f"## {self.module_icon} {self.module_name} - Ocena diagnostyczna")
        
        # Progress tracking
        progress = self._calculate_progress()
        st.progress(progress)
        st.write(f"Postęp: {progress*100:.0f}%")
        
        # Red flags check
        if self._check_red_flags(patient, mode):
            return {"red_flags_detected": True}
        
        # Wywiad
        st.markdown("### 📋 Wywiad medyczny")
        interview_results = self.run_interview(patient, mode)
        self.current_findings.update(interview_results)
        
        # Badanie fizykalne
        if mode == "specialist":
            st.markdown("### 🔬 Badanie fizykalne")
            exam_results = self.run_physical_examination(patient, mode)
            self.current_findings.update(exam_results)
        
        # Risk scores
        risk_scores = self.calculate_risk_scores(self.current_findings)
        self.current_findings['risk_scores'] = risk_scores
        
        return self.current_findings
    
    def _calculate_progress(self) -> float:
        """Oblicza postęp oceny"""
        completed_steps = sum(1 for step in self.assessment_steps if step.completed)
        total_steps = len(self.assessment_steps)
        return completed_steps / total_steps if total_steps > 0 else 0
    
    def _check_red_flags(self, patient: Patient, mode: str) -> bool:
        """Sprawdza czerwone flagi"""
        st.markdown("#### 🚨 Kontrola czerwonych flag")
        
        red_flags = self._get_red_flags_list()
        detected_flags = []
        
        col1, col2 = st.columns(2)
        for i, flag in enumerate(red_flags):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.checkbox(flag, key=f"red_flag_{self.module_name}_{i}"):
                    detected_flags.append(flag)
        
        if detected_flags:
            st.error("🚨 CZERWONE FLAGI WYKRYTE!")
            for flag in detected_flags:
                st.error(f"⚠️ {flag}")
            
            if mode == "patient":
                st.error("Skontaktuj się pilnie z lekarzem lub udaj się do SOR!")
                return True
            else:
                st.warning("Rozważ pilne skierowanie lub dodatkową diagnostykę.")
        
        return False
    
    @abstractmethod
    def _get_red_flags_list(self) -> List[str]:
        """Zwraca listę czerwonych flag dla modułu"""
        pass
    
    def render_test_interface(self, test: DiagnosticTest, mode: str) -> Optional[str]:
        """Renderuje interfejs dla konkretnego testu"""
        with st.expander(f"🔬 {test.name}", expanded=False):
            st.markdown(f"**Opis:** {test.description}")
            
            if st.button(f"📖 Pokaż procedurę", key=f"procedure_{test.name}"):
                st.markdown("#### Procedura wykonania:")
                st.markdown(test.procedure)
                
                if test.video_url:
                    st.video(test.video_url)
                
                if test.image_urls:
                    for img_url in test.image_urls:
                        st.image(img_url)
            
            if mode == "specialist":
                st.markdown("#### Wynik testu:")
                
                if test.test_category == "physical":
                    result = st.selectbox(
                        "Wybierz wynik:",
                        ["Nie wykonano", "Negatywny", "Pozytywny", "Nieokreślony"],
                        key=f"test_result_{test.name}"
                    )
                    
                    if result != "Nie wykonano":
                        notes = st.text_area(
                            "Notatki (opcjonalne):",
                            key=f"test_notes_{test.name}",
                            placeholder="Dodatkowe obserwacje..."
                        )
                        return result
                
                elif test.test_category == "scored":
                    score = st.slider(
                        "Wynik (punkty):",
                        min_value=0,
                        max_value=10,
                        value=0,
                        key=f"test_score_{test.name}"
                    )
                    return str(score)
        
        return None
    
    def save_test_result(self, session_id: int, test_name: str, result: str, score: float = None, notes: str = None):
        """Zapisuje wynik testu do bazy danych"""
        if 'db_manager' in st.session_state:
            test_result = TestResult(
                session_id=session_id,
                test_name=test_name,
                test_result=result,
                test_score=score,
                test_notes=notes
            )
            st.session_state.db_manager.add_test_result(test_result)
    
    def get_treatment_recommendations(self, diagnosis: Diagnosis) -> List[str]:
        """Pobiera rekomendacje leczenia dla diagnozy"""
        # Bazowe rekomendacje - mogą być nadpisane w konkretnych modułach
        base_recommendations = [
            "Edukacja pacjenta o stanie",
            "Modyfikacja aktywności według tolerancji bólu",
            "Monitorowanie objawów",
            "Kontrola w odpowiednich odstępach czasu"
        ]
        
        return base_recommendations + diagnosis.treatment_options
    
    def format_assessment_summary(self, findings: Dict[str, Any]) -> str:
        """Formatuje podsumowanie oceny"""
        summary = f"## Podsumowanie oceny - {self.module_name}\n\n"
        
        # Wywiad
        if 'interview' in findings:
            summary += "### 📋 Wywiad:\n"
            for key, value in findings['interview'].items():
                summary += f"- **{key}:** {value}\n"
            summary += "\n"
        
        # Badanie fizykalne
        if 'physical_exam' in findings:
            summary += "### 🔬 Badanie fizykalne:\n"
            for key, value in findings['physical_exam'].items():
                summary += f"- **{key}:** {value}\n"
            summary += "\n"
        
        # Wyniki testów
        if 'test_results' in findings:
            summary += "### 🧪 Wyniki testów:\n"
            for test_name, result in findings['test_results'].items():
                summary += f"- **{test_name}:** {result}\n"
            summary += "\n"
        
        # Risk scores
        if 'risk_scores' in findings:
            summary += "### 📊 Wskaźniki ryzyka:\n"
            for score_name, score_value in findings['risk_scores'].items():
                summary += f"- **{score_name}:** {score_value:.1f}\n"
        
        return summary
    
    def export_findings_to_json(self, findings: Dict[str, Any]) -> str:
        """Eksportuje wyniki do JSON"""
        import json
        return json.dumps(findings, ensure_ascii=False, indent=2, default=str)
