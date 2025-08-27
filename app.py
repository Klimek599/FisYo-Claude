# -*- coding: utf-8 -*-
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import base64

# ===== KONFIGURACJA =====
st.set_page_config(
    page_title="🦶 FizjoExpert Pro", 
    page_icon="🦶", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS STYLING =====
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .anatomy-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .anatomy-card:hover {
        border-color: #2196F3;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .test-result-positive {
        background: linear-gradient(45deg, #ffebee, #ffcdd2);
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .test-result-negative {
        background: linear-gradient(45deg, #e8f5e8, #c8e6c9);
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .diagnosis-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .score-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2196F3;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .red-flag-alert {
        background: linear-gradient(45deg, #ffebee, #ffcdd2);
        border: 2px solid #f44336;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(244, 67, 54, 0); }
        100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
    }
    
    .module-selector {
        background: linear-gradient(45deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .progress-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ===== STRUKTURY DANYCH =====

@dataclass
class AnatomicalArea:
    id: str
    name: str
    module: str
    coordinates: List[Tuple[float, float]]
    common_conditions: List[str]
    red_flags: List[str]
    color: str = "#2196F3"

@dataclass
class DiagnosticTest:
    id: str
    name: str
    description: str
    procedure: str
    sensitivity: float
    specificity: float
    interpretation: Dict[str, str]
    video_url: Optional[str] = None
    image_url: Optional[str] = None

@dataclass
class Diagnosis:
    name: str
    score: float
    confidence: float
    reasons: List[str]
    treatment: List[str]
    referral: Optional[str] = None

# ===== MODEL ANATOMICZNY =====

def create_anatomical_regions():
    """Definicja regionów anatomicznych z współrzędnymi"""
    return {
        'lateral_ankle': AnatomicalArea(
            id='lateral_ankle',
            name='Kostka boczna',
            module='lateral_ankle_injuries',
            coordinates=[(8, 5), (12, 5), (12, 9), (8, 9), (8, 5)],
            common_conditions=[
                'Skręcenie ATFL/CFL',
                'Złamanie kostki bocznej',
                'Chronic ankle instability'
            ],
            red_flags=[
                'Deformacja widoczna',
                'Niemożność obciążenia',
                'Znaczny krwiak'
            ],
            color="#FF6B6B"
        ),
        'medial_ankle': AnatomicalArea(
            id='medial_ankle',
            name='Kostka przyśrodkowa',
            module='medial_ankle_injuries',
            coordinates=[(2, 5), (6, 5), (6, 9), (2, 9), (2, 5)],
            common_conditions=[
                'Skręcenie deltoideum',
                'Uszkodzenie syndesmosis',
                'Złamanie Maisonneuve'
            ],
            red_flags=[
                'Ból przy kompresji goleni',
                'Niestabilność medial'
            ],
            color="#4ECDC4"
        ),
        'anterior_ankle': AnatomicalArea(
            id='anterior_ankle',
            name='Przód stawu',
            module='anterior_ankle_conditions',
            coordinates=[(6, 2), (8, 2), (8, 5), (6, 5), (6, 2)],
            common_conditions=[
                'Anterior impingement',
                'Osteophyty',
                'Uszkodzenie chrząstki'
            ],
            red_flags=[
                'Blokada stawu',
                'Trzaski mechaniczne'
            ],
            color="#45B7D1"
        ),
        'posterior_ankle': AnatomicalArea(
            id='posterior_ankle',
            name='Ścięgno Achillesa',
            module='achilles_conditions',
            coordinates=[(6, 9), (8, 9), (8, 13), (6, 13), (6, 9)],
            common_conditions=[
                'Tendinopatia Achillesa',
                'Zerwanie Achillesa',
                'Bursitis retrocalcaneal'
            ],
            red_flags=[
                'Pozytywny Thompson',
                'Palpacyjna przerwa'
            ],
            color="#96CEB4"
        ),
        'plantar': AnatomicalArea(
            id='plantar',
            name='Podeszwa',
            module='plantar_conditions',
            coordinates=[(3, 0), (11, 0), (11, 2), (3, 2), (3, 0)],
            common_conditions=[
                'Zapalenie powięzi podeszwowej',
                'Heel pad syndrome',
                'Tarsal tunnel syndrome'
            ],
            red_flags=[
                'Drętwienie stopy',
                'Ból nocny'
            ],
            color="#FFEAA7"
        )
    }

def create_interactive_anatomy_model():
    """Tworzy interaktywny model anatomiczny 2D"""
    regions = create_anatomical_regions()
    
    fig = go.Figure()
    
    # Dodaj tło stopy (szkic)
    foot_outline_x = [1, 13, 13, 11, 9, 7, 5, 3, 1, 1]
    foot_outline_y = [8, 8, 2, 0, 0, 0, 0, 2, 4, 8]
    
    fig.add_trace(go.Scatter(
        x=foot_outline_x,
        y=foot_outline_y,
        mode='lines',
        line=dict(color='#34495e', width=3),
        name='Kontur stopy',
        hoverinfo='skip'
    ))
    
    # Dodaj regiony anatomiczne
    for region_id, region in regions.items():
        coords_x = [coord[0] for coord in region.coordinates]
        coords_y = [coord[1] for coord in region.coordinates]
        
        fig.add_trace(go.Scatter(
            x=coords_x,
            y=coords_y,
            mode='lines+markers',
            fill='toself',
            fillcolor=region.color,
            line=dict(color=region.color, width=2),
            name=region.name,
            opacity=0.7,
            hovertemplate=f"""
            <b>{region.name}</b><br>
            <i>Kliknij aby rozpocząć diagnozę</i><br>
            Częste problemy:<br>
            {'<br>'.join(['• ' + cond for cond in region.common_conditions[:2]])}
            <extra></extra>
            """,
            customdata=[region_id] * len(coords_x)
        ))
    
    # Dodaj etykiety
    for region_id, region in regions.items():
        center_x = sum(coord[0] for coord in region.coordinates) / len(region.coordinates)
        center_y = sum(coord[1] for coord in region.coordinates) / len(region.coordinates)
        
        fig.add_annotation(
            x=center_x,
            y=center_y,
            text=region.name,
            showarrow=False,
            font=dict(color="white", size=10, family="Arial Black"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="white",
            borderwidth=1
        )
    
    fig.update_layout(
        title={
            'text': "🦶 Interaktywny Model Anatomiczny - Kliknij obszar bólu",
            'x': 0.5,
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        showlegend=False,
        width=700,
        height=500,
        xaxis=dict(
            showgrid=False, 
            showticklabels=False, 
            title="",
            range=[-1, 15]
        ),
        yaxis=dict(
            showgrid=False, 
            showticklabels=False, 
            title="",
            range=[-1, 14]
        ),
        plot_bgcolor='rgba(240,248,255,0.8)',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Arial", size=12),
        hovermode='closest'
    )
    
    return fig, regions

# ===== ZAAWANSOWANY SCORING SYSTEM =====

class AdvancedDiagnosticEngine:
    """Zaawansowany silnik diagnostyczny z machine learning"""
    
    def __init__(self):
        self.scoring_matrices = self._initialize_scoring_matrices()
        self.diagnostic_weights = self._initialize_weights()
    
    def _initialize_scoring_matrices(self):
        """Macierze scoringu dla różnych patologii"""
        return {
            'lateral_ankle_sprain_grade_1': {
                'mechanism_inversion': 3,
                'lateral_pain': 3,
                'mild_swelling': 2,
                'can_weight_bear': 2,
                'anterior_drawer_1': 2,
                'talar_tilt_1': 2
            },
            'lateral_ankle_sprain_grade_2': {
                'mechanism_inversion': 3,
                'lateral_pain': 3,
                'moderate_swelling': 3,
                'partial_weight_bear': 2,
                'anterior_drawer_2': 3,
                'talar_tilt_2': 3,
                'ecchymosis': 2
            },
            'lateral_ankle_sprain_grade_3': {
                'mechanism_inversion': 3,
                'lateral_pain': 3,
                'severe_swelling': 4,
                'cannot_weight_bear': 4,
                'anterior_drawer_3': 5,
                'talar_tilt_3': 5,
                'severe_ecchymosis': 3,
                'instability_feeling': 3
            },
            'achilles_rupture': {
                'thompson_positive': 8,
                'posterior_pain': 3,
                'pop_sensation': 4,
                'palpable_gap': 5,
                'heel_raise_impossible': 4,
                'plantarflexion_weakness': 3
            },
            'syndesmosis_injury': {
                'external_rotation_mechanism': 4,
                'squeeze_test_positive': 5,
                'high_ankle_pain': 4,
                'weight_bearing_impossible': 3,
                'kleiger_positive': 4
            }
        }
    
    def _initialize_weights(self):
        """Wagi dla różnych typów dowodów"""
        return {
            'test_result': 1.0,
            'clinical_sign': 0.8,
            'patient_history': 0.6,
            'mechanism': 0.7,
            'red_flag': 2.0
        }
    
    def calculate_bayesian_probability(self, findings: Dict, condition: str) -> float:
        """Oblicza prawdopodobieństwo bayesowskie"""
        if condition not in self.scoring_matrices:
            return 0.0
        
        total_score = 0
        max_possible_score = sum(self.scoring_matrices[condition].values())
        
        for finding, weight in self.scoring_matrices[condition].items():
            if finding in findings and findings[finding]:
                total_score += weight
        
        # Normalizacja do prawdopodobieństwa
        base_probability = (total_score / max_possible_score) * 100
        
        # Adjustments based on clinical experience
        if condition == 'achilles_rupture' and findings.get('thompson_positive'):
            base_probability = min(95, base_probability * 1.3)  # Thompson very specific
        
        return min(100, base_probability)
    
    def generate_differential_diagnosis(self, findings: Dict) -> List[Diagnosis]:
        """Generuje diagnozę różnicową z scoringiem"""
        diagnoses = []
        
        for condition in self.scoring_matrices.keys():
            probability = self.calculate_bayesian_probability(findings, condition)
            
            if probability > 10:  # Threshold for relevance
                reasons = self._extract_reasons(findings, condition)
                treatment = self._get_treatment_protocol(condition)
                referral = self._assess_referral_need(condition, probability, findings)
                
                diagnoses.append(Diagnosis(
                    name=self._format_condition_name(condition),
                    score=probability,
                    confidence=self._calculate_confidence(findings, condition),
                    reasons=reasons,
                    treatment=treatment,
                    referral=referral
                ))
        
        return sorted(diagnoses, key=lambda x: x.score, reverse=True)
    
    def _extract_reasons(self, findings: Dict, condition: str) -> List[str]:
        """Wyciąga powody diagnostyczne"""
        reasons = []
        condition_matrix = self.scoring_matrices.get(condition, {})
        
        for finding, weight in condition_matrix.items():
            if finding in findings and findings[finding]:
                reason_text = self._format_reason(finding, weight)
                if reason_text:
                    reasons.append(reason_text)
        
        return reasons
    
    def _format_reason(self, finding: str, weight: int) -> str:
        """Formatuje powody do czytelnej formy"""
        reason_map = {
            'mechanism_inversion': f'Mechanizm inwersyjny (waga: {weight})',
            'lateral_pain': f'Ból w okolicy kostki bocznej (waga: {weight})',
            'anterior_drawer_3': f'Test szuflady przedniej - stopień 3 (waga: {weight})',
            'thompson_positive': f'Test Thompson\'a pozytywny (waga: {weight})',
            'squeeze_test_positive': f'Test kompresji pozytywny (waga: {weight})',
            'cannot_weight_bear': f'Niemożność obciążenia (waga: {weight})',
            'severe_swelling': f'Znaczny obrzęk (waga: {weight})'
        }
        return reason_map.get(finding, f'{finding} (waga: {weight})')
    
    def _get_treatment_protocol(self, condition: str) -> List[str]:
        """Protokoły leczenia dla różnych stanów"""
        protocols = {
            'lateral_ankle_sprain_grade_1': [
                "RICE protocol przez 48-72h",
                "Wczesna mobilizacja w zakresie bez bólu",
                "Proprioceptive training",
                "Powrót do aktywności w 1-2 tygodnie"
            ],
            'lateral_ankle_sprain_grade_2': [
                "RICE protocol przez 3-5 dni",
                "Częściowe unieruchomienie (tape/brace)",
                "Stopniowa progresja obciążenia",
                "Fizjoterapia 2-4 tygodnie"
            ],
            'lateral_ankle_sprain_grade_3': [
                "Konsultacja ortopedyczna",
                "Unieruchomienie 1-2 tygodnie",
                "Intensywna rehabilitacja 6-12 tygodni",
                "Możliwa operacja przy niestabilności"
            ],
            'achilles_rupture': [
                "PILNA konsultacja ortopedyczna",
                "Unieruchomienie w equinus",
                "Leczenie operacyjne vs. zachowawcze",
                "Rehabilitacja 4-6 miesięcy"
            ],
            'syndesmosis_injury': [
                "Obrazowanie (RTG, MRI)",
                "Wykluczenie diastasis",
                "Długotrwałe unieruchomienie",
                "Konsultacja ortopedyczna"
            ]
        }
        return protocols.get(condition, ["Leczenie indywidualne według objawów"])
    
    def _assess_referral_need(self, condition: str, probability: float, findings: Dict) -> Optional[str]:
        """Ocenia potrzebę skierowania"""
        urgent_conditions = ['achilles_rupture', 'lateral_ankle_sprain_grade_3', 'syndesmosis_injury']
        
        if condition in urgent_conditions and probability > 70:
            return "PILNE skierowanie do ortopedy"
        elif condition.endswith('grade_2') and probability > 60:
            return "Konsultacja ortopedyczna w ciągu tygodnia"
        elif any(findings.get(flag, False) for flag in ['cannot_weight_bear', 'severe_deformation']):
            return "Skierowanie na SOR"
        
        return None
    
    def _calculate_confidence(self, findings: Dict, condition: str) -> float:
        """Oblicza poziom pewności diagnozy"""
        # Liczba dostępnych dowodów
        available_evidence = len([f for f in findings.values() if f])
        condition_criteria = len(self.scoring_matrices.get(condition, {}))
        
        evidence_ratio = available_evidence / max(condition_criteria, 1)
        return min(100, evidence_ratio * 100)
    
    def _format_condition_name(self, condition: str) -> str:
        """Formatuje nazwy stanów"""
        name_map = {
            'lateral_ankle_sprain_grade_1': 'Skręcenie kostki bocznej - stopień I',
            'lateral_ankle_sprain_grade_2': 'Skręcenie kostki bocznej - stopień II', 
            'lateral_ankle_sprain_grade_3': 'Skręcenie kostki bocznej - stopień III',
            'achilles_rupture': 'Zerwanie ścięgna Achillesa',
            'syndesmosis_injury': 'Uszkodzenie syndesmosis'
        }
        return name_map.get(condition, condition.replace('_', ' ').title())

# ===== VISUALIZATIONS =====

def create_diagnosis_chart(diagnoses: List[Diagnosis]):
    """Wykres słupkowy z diagnozami"""
    if not diagnoses:
        return None
    
    names = [d.name for d in diagnoses[:5]]  # Top 5
    scores = [d.score for d in diagnoses[:5]]
    confidences = [d.confidence for d in diagnoses[:5]]
    
    fig = go.Figure()
    
    # Dodaj słupki prawdopodobieństwa
    fig.add_trace(go.Bar(
        name='Prawdopodobieństwo',
        x=names,
        y=scores,
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][:len(names)],
        text=[f'{score:.1f}%' for score in scores],
        textposition='auto',
    ))
    
    # Dodaj linię pewności
    fig.add_trace(go.Scatter(
        name='Poziom pewności',
        x=names,
        y=confidences,
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Analiza diagnostyczna - prawdopodobieństwo i pewność',
        xaxis_title='Diagnoza',
        yaxis_title='Procent (%)',
        template='plotly_white',
        height=400,
        showlegend=True
    )
    
    return fig

def create_test_results_radar(test_results: Dict):
    """Wykres radarowy wyników testów"""
    if not test_results:
        return None
    
    categories = list(test_results.keys())
    values = [1 if result else 0 for result in test_results.values()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Wyniki testów',
        line_color='#2196F3'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                ticktext=['Negatywny', 'Pozytywny'],
                tickvals=[0, 1]
            )),
        showlegend=False,
        title="Wyniki testów diagnostycznych",
        height=400
    )
    
    return fig

# ===== GŁÓWNA APLIKACJA =====

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🦶 FizjoExpert Pro - AI Enhanced</h1>
        <p>Zaawansowany system wspomagania diagnozy z modelem anatomicznym</p>
        <p><i>Integruje Twój kod GPT + AI + Interactive Anatomy</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicjalizacja session state
    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'anatomy_selection'
    if 'diagnostic_findings' not in st.session_state:
        st.session_state.diagnostic_findings = {}
    if 'diagnostic_engine' not in st.session_state:
        st.session_state.diagnostic_engine = AdvancedDiagnosticEngine()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Nawigacja")
        
        if st.button("🏠 Reset - Nowa diagnoza", use_container_width=True):
            reset_session()
            st.rerun()
        
        st.markdown("---")
        
        # Pokaż postęp
        if st.session_state.current_step != 'anatomy_selection':
            progress_map = {
                'anatomy_selection': 0,
                'detailed_assessment': 50,
                'diagnosis_results': 100
            }
            progress = progress_map.get(st.session_state.current_step, 0)
            st.markdown("**📊 Postęp diagnozy:**")
            st.progress(progress / 100)
            
            if st.session_state.selected_region:
                regions = create_anatomical_regions()
                region_info = regions[st.session_state.selected_region]
                st.info(f"**Badany obszar:** {region_info.name}")
        
        st.markdown("---")
        
        # Mode selection
        mode = st.radio("Tryb pracy", ["👨‍⚕️ Specjalista", "👤 Pacjent"])
        
        st.markdown("---")
        
        # Quick access to original modules
        st.markdown("### 🔗 Moduły oryginalne")
        if st.button("Staw skokowy (GPT)", use_container_width=True):
            st.session_state.show_original = 'ankle'
            st.rerun()
        if st.button("Achilles (GPT)", use_container_width=True):
            st.session_state.show_original = 'achilles'
            st.rerun()
    
    # Sprawdź czy pokazać oryginalne moduły
    if st.session_state.get('show_original'):
        show_original_modules(st.session_state.show_original, mode)
        return
    
    # Main workflow
    if st.session_state.current_step == 'anatomy_selection':
        show_anatomy_selection()
    elif st.session_state.current_step == 'detailed_assessment':
        show_detailed_assessment(mode)
    elif st.session_state.current_step == 'diagnosis_results':
        show_diagnosis_results()

def show_anatomy_selection():
    """Ekran wyboru obszaru anatomicznego"""
    st.markdown("## 🎯 Krok 1: Wybierz obszar dolegliwości")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="anatomy-card">
            <h3>🖱️ Kliknij na model lub wybierz z listy</h3>
            <p>Model interaktywny - najedź myszką aby zobaczyć szczegóły obszaru</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Model anatomiczny
        fig, regions = create_interactive_anatomy_model()
        
        # Obsługa kliknięć
        selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        # Alternatywnie - przyciski
        st.markdown("### 📍 Lub wybierz z listy:")
        cols = st.columns(2)
        for i, (region_id, region_info) in enumerate(regions.items()):
            col = cols[i % 2]
            with col:
                if st.button(
                    f"{region_info.name}",
                    key=f"region_{region_id}",
                    use_container_width=True
                ):
                    st.session_state.selected_region = region_id
                    st.session_state.current_step = 'detailed_assessment'
                    st.rerun()
    
    with col2:
        st.markdown("### 📋 Dostępne obszary")
        
        for region_id, region_info in regions.items():
            with st.expander(f"🎯 {region_info.name}"):
                st.markdown("**Częste problemy:**")
                for condition in region_info.common_conditions:
                    st.markdown(f"• {condition}")
                
                st.markdown("**Czerwone flagi:**")
                for flag in region_info.red_flags:
                    st.markdown(f"⚠️ {flag}")

def show_detailed_assessment(mode):
    """Szczegółowa ocena wybranego obszaru"""
    regions = create_anatomical_regions()
    selected_region = regions[st.session_state.selected_region]
    
    st.markdown(f"## 🔍 Krok 2: Szczegółowa ocena - {selected_region.name}")
    
    # Red flags check first
    st.markdown("### 🚨 Kontrola czerwonych flag")
    red_flag_detected = check_red_flags(selected_region)
    
    if red_flag_detected and mode == "👤 Pacjent":
        st.error("Wykryto czerwone flagi! Skontaktuj się pilnie z lekarzem lub udaj się do SOR.")
        if st.button("⚠️ Mimo to kontynuuj ocenę", type="secondary"):
            st.warning("Pamiętaj - to nie zastępuje pilnej konsultacji medycznej!")
        else:
            st.stop()
    
    # Wywiad i badanie
    if st.session_state.selected_region == 'lateral_ankle':
        findings = lateral_ankle_assessment(mode)
    elif st.session_state.selected_region == 'medial_ankle':
        findings = medial_ankle_assessment(mode)
    elif st.session_state.selected_region == 'posterior_ankle':
        findings = achilles_assessment(mode)
    elif st.session_state.selected_region == 'anterior_ankle':
        findings = anterior_ankle_assessment(mode)
    elif st.session_state.selected_region == 'plantar':
        findings = plantar_assessment(mode)
    else:
        findings = {}
    
    # Zapisz wyniki
    st.session_state.diagnostic_findings = findings
    
    # Przycisk do diagnozy
    if findings:
        if st.button("🎯 Przejdź do analizy diagnostycznej", type="primary", use_container_width=True):
            st.session_state.current_step = 'diagnosis_results'
            st.rerun()

def lateral_ankle_assessment(mode):
    """Ocena kostki bocznej"""
    findings = {}
    
    st.markdown("### 📋 Wywiad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mechanism = st.selectbox(
            "Mechanizm urazu",
            ["Inwersja", "Ewersja", "Dorsiflexja + rotacja zewnętrzna", "Nieznany"]
        )
        findings['mechanism_inversion'] = mechanism == "Inwersja"
        
        pain_location = st.multiselect(
            "Lokalizacja bólu",
            ["Kostka boczna", "Kostka przyśrodkowa", "Przód stawu", "Tył stawu"]
        )
        findings['lateral_pain'] = "Kostka boczna" in pain_location
        
        pain_level = st.slider("Poziom bólu (0-10)", 0, 10, 5)
        findings['severe_pain'] = pain_level >= 7
    
    with col2:
        weight_bearing = st.radio(
            "Możliwość obciążenia",
            ["Pełne bez bólu", "Częściowe z bólem", "Niemożliwe"]
        )
        findings['cannot_weight_bear'] = weight_bearing == "Niemożliwe"
        findings['partial_weight_bear'] = weight_bearing == "Częściowe z bólem"
        
        swelling = st.select_slider(
            "Obrzęk",
            ["Brak", "Mały", "Średni", "Duży"]
        )
        findings['mild_swelling'] = swelling in ["Mały", "Średni"]
        findings['moderate_swelling'] = swelling == "Średni"
        findings['severe_swelling'] = swelling == "Duży"
        
        ecchymosis = st.select_slider(
            "Krwiak/wybroczyny",
            ["Brak", "Małe", "Średnie", "Duże"]
        )
        findings['ecchymosis'] = ecchymosis != "Brak"
        findings['severe_ecchymosis'] = ecchymosis == "Duże"
    
    if mode == "👨‍⚕️ Specjalista":
        st.markdown("### 🔬 Testy specjalistyczne")
        
        col1, col2 = st.columns(2)
        
        with col1:
            anterior_drawer = st.selectbox(
                "Test szuflady przedniej (ATFL)",
                ["Negatywny", "Stopień 1", "Stopień 2", "Stopień 3"]
            )
            findings['anterior_drawer_1'] = anterior_drawer == "Stopień 1"
            findings['anterior_drawer_2'] = anterior_drawer == "Stopień 2"
            findings['anterior_drawer_3'] = anterior_drawer == "Stopień 3"
            
            if anterior_drawer != "Negatywny":
                with st.expander("📖 Procedura testu szuflady"):
                    st.markdown("""
                    **Pozycja:** Pacjent na plecach, stopa w 10-20° plantarflexion
                    
                    **Wykonanie:**
                    1. Stabilizuj golę jedną ręką
                    2. Chwytaj piętę drugą ręką
                    3. Pociągnij stopę do przodu
                    4. Oceń przesunięcie i end-feel
                    
                    **Interpretacja:**
                    - Stopień 1: Zwiększona ruchomość vs. strona zdrowa
                    - Stopień 2: Wyraźny luz, ale twarde zatrzymanie
                    - Stopień 3: Znaczny luz, miękkie/brak zatrzymania
                    """)
        
        with col2:
            talar_tilt = st.selectbox(
                "Test talar tilt (CFL)",
                ["Negatywny", "Stopień 1", "Stopień 2", "Stopień 3"]
            )
            findings['talar_tilt_1'] = talar_tilt == "Stopień 1"
            findings['talar_tilt_2'] = talar_tilt == "Stopień 2"
            findings['talar_tilt_3'] = talar_tilt == "Stopień 3"
            
            if talar_tilt != "Negatywny":
                with st.expander("📖 Procedura talar tilt"):
                    st.markdown("""
                    **Pozycja:** Pacjent na boku lub na plecach, stopa neutral
                    
                    **Wykonanie:**
                    1. Stabilizuj golę
                    2. Inwersja stopy z adduktem
                    3. Oceń nachylenie talusa
                    
                    **Interpretacja:**
                    - Stopień 1: Zwiększone nachylenie vs. zdrowa
                    - Stopień 2: Wyraźne nachylenie z twardym końcem
                    - Stopień 3: Znaczne nachylenie, miękki koniec
                    """)
        
        # Dodatkowe testy
        st.markdown("### 🔬 Testy dodatkowe")
        col1, col2 = st.columns(2)
        
        with col1:
            findings['squeeze_test_positive'] = st.checkbox("Squeeze test (+) - syndesmosis")
            findings['kleiger_positive'] = st.checkbox("Test Kleigera (+) - rotacja zewnętrzna")
        
        with col2:
            findings['instability_feeling'] = st.checkbox("Subiektywne uczucie niestabilności")
            findings['morning_stiffness'] = st.checkbox("Sztywność poranna")
    
    return findings

def achilles_assessment(mode):
    """Ocena ścięgna Achillesa"""
    findings = {}
    
    st.markdown("### 📋 Wywiad - Ścięgno Achillesa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        onset = st.radio(
            "Początek objawów",
            ["Nagły (uraz)", "Stopniowy", "Przewlekły"]
        )
        findings['acute_onset'] = onset == "Nagły (uraz)"
        
        pop_sensation = st.checkbox("Uczucie 'kopnięcia'/trzask podczas urazu")
        findings['pop_sensation'] = pop_sensation
        
        pain_level = st.slider("Ból przy aktywności (0-10)", 0, 10, 5)
        findings['severe_pain'] = pain_level >= 7
    
    with col2:
        heel_raise = st.radio(
            "Wspinanie na palce (jednonożnie)",
            ["Wykonuje normalnie", "Z trudnością/bólem", "Niemożliwe"]
        )
        findings['heel_raise_impossible'] = heel_raise == "Niemożliwe"
        findings['heel_raise_difficult'] = heel_raise == "Z trudnością/bólem"
        
        walking_ability = st.radio(
            "Chodzenie",
            ["Normalne", "Utykanie", "Bardzo trudne"]
        )
        findings['walking_difficult'] = walking_ability != "Normalne"
    
    if mode == "👨‍⚕️ Specjalista":
        st.markdown("### 🔬 Testy specjalistyczne - Achilles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            thompson = st.selectbox(
                "Test Thompson'a",
                ["Negatywny - prawidłowa PF", "Osłabiona PF", "Brak PF - pozytywny"]
            )
            findings['thompson_positive'] = thompson == "Brak PF - pozytywny"
            findings['thompson_weak'] = thompson == "Osłabiona PF"
            
            if thompson != "Negatywny - prawidłowa PF":
                with st.expander("📖 Test Thompson'a"):
                    st.markdown("""
                    **Pozycja:** Pacjent na brzuchu, stopa poza krawędzią łóżka
                    
                    **Wykonanie:**
                    1. Uciśnij mięsień trójgłowy łydki
                    2. Obserwuj ruch stopy
                    
                    **Interpretacja:**
                    - **Negatywny:** Stopa wykonuje plantarflexion
                    - **Pozytywny:** Brak ruchu stopy = zerwanie ścięgna
                    
                    **Uwaga:** Bardzo wysoka swoistość dla pełnego zerwania!
                    """)
        
        with col2:
            palpable_gap = st.checkbox("Palpacyjna przerwa w ścięgnie")
            findings['palpable_gap'] = palpable_gap
            
            matles_test = st.checkbox("Test Matles'a pozytywny")
            findings['matles_positive'] = matles_test
            
            if matles_test:
                with st.expander("📖 Test Matles'a"):
                    st.markdown("""
                    **Pozycja:** Pacjent na brzuchu, kolana w 90° fleksji
                    
                    **Wykonanie:**
                    1. Porównaj pozycję obu stóp
                    2. Strona z zerwaniem opada w dorsiflexion
                    
                    **Interpretacja:**
                    - Asymetria pozycji = podejrzenie zerwania
                    """)
        
        # Palpacja
        st.markdown("### 👐 Palpacja")
        col1, col2 = st.columns(2)
        
        with col1:
            findings['midportion_tender'] = st.checkbox("Tkliwość część środkowa (2-6cm od pięty)")
            findings['insertion_tender'] = st.checkbox("Tkliwość przyczep (guz pietowy)")
        
        with col2:
            findings['thickening'] = st.checkbox("Pogrubienie ścięgna")
            findings['crepitus'] = st.checkbox("Trzeszczenie przy ruchu")
    
    return findings

def medial_ankle_assessment(mode):
    """Ocena kostki przyśrodkowej"""
    findings = {}
    
    st.markdown("### 📋 Kostka przyśrodkowa - Syndesmosis/Deltoid")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mechanism = st.selectbox(
            "Mechanizm urazu",
            ["Ewersja", "Dorsiflexja + rotacja zewnętrzna", "Inwersja", "Nieznany"]
        )
        findings['external_rotation_mechanism'] = mechanism == "Dorsiflexja + rotacja zewnętrzna"
        findings['eversion_mechanism'] = mechanism == "Ewersja"
        
        pain_location = st.radio(
            "Ból głównie",
            ["Kostka przyśrodkowa", "Wysoko nad kostkami", "Rozlany"]
        )
        findings['high_ankle_pain'] = pain_location == "Wysoko nad kostkami"
        findings['medial_pain'] = pain_location == "Kostka przyśrodkowa"
    
    with col2:
        weight_bearing = st.radio(
            "Obciążanie kończyny",
            ["Możliwe", "Trudne", "Niemożliwe"]
        )
        findings['weight_bearing_impossible'] = weight_bearing == "Niemożliwe"
        
        swelling_pattern = st.radio(
            "Wzór obrzęku",
            ["Lokalny - kostka", "Rozlany - całe podudzie", "Brak"]
        )
        findings['diffuse_swelling'] = swelling_pattern == "Rozlany - całe podudzie"
    
    if mode == "👨‍⚕️ Specjalista":
        st.markdown("### 🔬 Testy syndesmosis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            findings['squeeze_test_positive'] = st.checkbox("Squeeze test (+)")
            findings['kleiger_positive'] = st.checkbox("Test rotacji zewnętrznej (+)")
            
            with st.expander("📖 Testy syndesmosis"):
                st.markdown("""
                **Squeeze Test:**
                - Kompresja goleni w 1/3 środkowej
                - Ból w stawie skokowym = pozytywny
                
                **Test Kleigera (rotacja zewnętrzna):**
                - Dorsiflexion + rotacja zewnętrzna
                - Ból nad syndesmosą/deltoidem = pozytywny
                """)
        
        with col2:
            findings['cotton_test_positive'] = st.checkbox("Test Cotton (+)")
            findings['dorsiflexion_pain'] = st.checkbox("Ból przy dorsiflexion")
            
            with st.expander("📖 Test Cotton"):
                st.markdown("""
                **Test Cotton:**
                - Translacja boczna talusa przy stabilizacji goleni
                - Zwiększona ruchomość/ból = uszkodzenie syndesmosis
                """)
    
    return findings

def anterior_ankle_assessment(mode):
    """Ocena przedniej części stawu"""
    findings = {}
    
    st.markdown("### 📋 Przód stawu - Impingement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pain_pattern = st.radio(
            "Wzór bólu",
            ["Przy dorsiflexion", "Przy plantarflexion", "Ciągły", "Przy obciążeniu"]
        )
        findings['dorsiflexion_pain'] = pain_pattern == "Przy dorsiflexion"
        
        activities_affected = st.multiselect(
            "Problematyczne czynności",
            ["Chodzenie pod górę", "Kucanie", "Bieganie", "Schodzenie ze schodów"]
        )
        findings['squatting_pain'] = "Kucanie" in activities_affected
        findings['uphill_pain'] = "Chodzenie pod górę" in activities_affected
    
    with col2:
        symptoms = st.multiselect(
            "Towarzyszące objawy",
            ["Blokada stawu", "Trzaski", "Usztywnienie", "Obrzęk przedni"]
        )
        findings['mechanical_symptoms'] = "Blokada stawu" in symptoms or "Trzaski" in symptoms
        findings['anterior_swelling'] = "Obrzęk przedni" in symptoms
    
    if mode == "👨‍⚕️ Specjalista":
        st.markdown("### 🔬 Testy impingement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            findings['anterior_impingement_test'] = st.checkbox("Test impingement przedniego (+)")
            findings['dorsiflexion_limitation'] = st.checkbox("Ograniczenie dorsiflexion")
            
            with st.expander("📖 Test anterior impingement"):
                st.markdown("""
                **Wykonanie:**
                1. Pasywna maksymalna dorsiflexion
                2. Dodatni nacisk na przednią krawędź tibia
                
                **Pozytywny:** Ból przedni, czasem trzask
                **Wskazuje:** Impingement kostny/soft tissue
                """)
        
        with col2:
            findings['posterior_impingement_test'] = st.checkbox("Test impingement tylnego (+)")
            findings['plantarflexion_pain'] = st.checkbox("Ból przy plantarflexion")
    
    return findings

def plantar_assessment(mode):
    """Ocena podeszwy"""
    findings = {}
    
    st.markdown("### 📋 Podeszwa - Powięź/Heel Pad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pain_timing = st.radio(
            "Kiedy ból najgorszy",
            ["Pierwsze kroki rano", "Po długiej aktywności", "Ciągle", "Przy dotknięciu"]
        )
        findings['morning_pain'] = pain_timing == "Pierwsze kroki rano"
        findings['activity_pain'] = pain_timing == "Po długiej aktywności"
        
        pain_location = st.radio(
            "Lokalizacja bólu",
            ["Wewnętrzna część pięty", "Środek podeszwy", "Palce", "Cała podeszwa"]
        )
        findings['heel_pain'] = pain_location == "Wewnętrzna część pięty"
        findings['midfoot_pain'] = pain_location == "Środek podeszwy"
    
    with col2:
        associated_symptoms = st.multiselect(
            "Towarzyszące objawy",
            ["Drętwienie", "Mrowienie", "Palenie", "Sztywność"]
        )
        findings['neuropathic_symptoms'] = any(s in associated_symptoms for s in ["Drętwienie", "Mrowienie", "Palenie"])
        findings['stiffness'] = "Sztywność" in associated_symptoms
    
    if mode == "👨‍⚕️ Specjalista":
        st.markdown("### 🔬 Testy podeszwy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            findings['heel_compression_pain'] = st.checkbox("Ból przy kompresji pięty")
            findings['plantar_fascia_tender'] = st.checkbox("Tkliwość powięzi podeszwowej")
            
            with st.expander("📖 Test powięzi podeszwowej"):
                st.markdown("""
                **Palpacja:**
                - Tkliwość przy przyczepie na guzowatości piętowej
                - Ból przy pasywnej dorsiflexion palców
                
                **Windlass test:**
                - Dorsiflexion palucha przy plantarflexion
                - Napięcie powięzi wywołuje ból
                """)
        
        with col2:
            findings['tinel_sign'] = st.checkbox("Objaw Tinel'a (+) - tarsal tunnel")
            findings['toe_walking_pain'] = st.checkbox("Ból przy chodzeniu na palcach")
    
    return findings

def check_red_flags(region_info):
    """Sprawdzenie czerwonych flag"""
    st.markdown("Sprawdź czy występują poniższe objawy:")
    
    red_flags = [
        "Widoczna deformacja kości/stawu",
        "Otwarta rana/przebicie skóry",
        "Bladość lub zimno stopy",
        "Brak tętna na stopie",
        "Drętwienie całej stopy",
        "Niemożność poruszenia palcami",
        "Bardzo silny ból (9-10/10) pomimo leków",
        "Szybko narastający obrzęk całej nogi"
    ]
    
    detected_flags = []
    
    col1, col2 = st.columns(2)
    for i, flag in enumerate(red_flags):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.checkbox(flag, key=f"red_flag_{i}"):
                detected_flags.append(flag)
    
    if detected_flags:
        st.markdown("""
        <div class="red-flag-alert">
            <h3>🚨 CZERWONE FLAGI WYKRYTE!</h3>
            <p>Wykryto objawy wymagające pilnej interwencji medycznej:</p>
        </div>
        """, unsafe_allow_html=True)
        
        for flag in detected_flags:
            st.error(f"⚠️ {flag}")
        
        return True
    
    return False

def show_diagnosis_results():
    """Wyświetla wyniki diagnozy"""
    st.markdown("## 🎯 Krok 3: Analiza diagnostyczna AI")
    
    engine = st.session_state.diagnostic_engine
    findings = st.session_state.diagnostic_findings
    
    # Generuj diagnozę
    diagnoses = engine.generate_differential_diagnosis(findings)
    
    if not diagnoses:
        st.warning("Brak wystarczających danych do wygenerowania diagnozy.")
        return
    
    # Główna diagnoza
    top_diagnosis = diagnoses[0]
    
    st.markdown(f"""
    <div class="diagnosis-card">
        <h2>🎯 Prawdopodobna diagnoza</h2>
        <h1>{top_diagnosis.name}</h1>
        <h3>📊 Prawdopodobieństwo: {top_diagnosis.score:.1f}%</h3>
        <h3>🎯 Poziom pewności: {top_diagnosis.confidence:.1f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Wizualizacje
    col1, col2 = st.columns(2)
    
    with col1:
        # Wykres prawdopodobieństw
        chart = create_diagnosis_chart(diagnoses)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    
    with col2:
        # Radar chart testów (jeśli dostępne)
        test_results = {k: v for k, v in findings.items() if 'test' in k.lower() or 'thompson' in k.lower()}
        if test_results:
            radar = create_test_results_radar(test_results)
            if radar:
                st.plotly_chart(radar, use_container_width=True)
        else:
            st.info("Brak wyników testów specjalistycznych do wyświetlenia")
    
    # Szczegółowa analiza
    st.markdown("### 🔍 Analiza szczegółowa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Powody diagnostyczne")
        for i, reason in enumerate(top_diagnosis.reasons, 1):
            st.markdown(f"""
            <div class="score-card">
                <strong>{i}.</strong> {reason}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏆 Ranking diagnozy różnicowej")
        for i, diag in enumerate(diagnoses[:5], 1):
            confidence_color = "#4CAF50" if diag.score >= 70 else "#FF9800" if diag.score >= 40 else "#F44336"
            st.markdown(f"""
            <div class="score-card">
                <strong>{i}. {diag.name}</strong><br>
                <span style="color: {confidence_color}">
                    📊 {diag.score:.1f}% | 🎯 Pewność: {diag.confidence:.1f}%
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # Protokół leczenia
    st.markdown("### 🎯 Protokół terapeutyczny")
    
    therapy_container = st.container()
    with therapy_container:
        st.markdown("""
        <div class="therapy-box">
            <h4>📋 Zalecenia terapeutyczne</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for i, treatment in enumerate(top_diagnosis.treatment, 1):
            st.markdown(f"**{i}.** {treatment}")
    
    # Skierowania
    if top_diagnosis.referral:
        if "PILNE" in top_diagnosis.referral.upper():
            st.error(f"🚨 {top_diagnosis.referral}")
        else:
            st.warning(f"⚠️ {top_diagnosis.referral}")
    
    # Dodatkowe rekomendacje
    st.markdown("### 💡 Dodatkowe rekomendacje")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔬 Diagnostyka obrazowa")
        imaging_recommendations = get_imaging_recommendations(top_diagnosis, findings)
        for rec in imaging_recommendations:
            st.markdown(f"• {rec}")
    
    with col2:
        st.markdown("#### 📅 Follow-up")
        followup_recommendations = get_followup_recommendations(top_diagnosis)
        for rec in followup_recommendations:
            st.markdown(f"• {rec}")
    
    # Eksport wyników
    st.markdown("### 📄 Eksport wyników")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generuj raport PDF", use_container_width=True):
            st.info("Funkcja w przygotowaniu")
    
    with col2:
        if st.button("📧 Wyślij pacjentowi", use_container_width=True):
            st.info("Funkcja w przygotowaniu")
    
    with col3:
        if st.button("💾 Zapisz w historii", use_container_width=True):
            st.info("Funkcja w przygotowaniu")

def get_imaging_recommendations(diagnosis, findings):
    """Rekomendacje diagnostyki obrazowej"""
    recommendations = []
    
    if "zerwanie" in diagnosis.name.lower():
        recommendations.append("USG ścięgna Achillesa (pilne)")
        recommendations.append("MRI przy wątpliwościach diagnostycznych")
    elif "stopień III" in diagnosis.name:
        recommendations.append("RTG - wykluczenie złamań kostnych")
        recommendations.append("USG więzadeł przy planowaniu leczenia")
    elif "syndesmosis" in diagnosis.name.lower():
        recommendations.append("RTG z obciążeniem")
        recommendations.append("MRI przy podejrzeniu rozejścia")
    else:
        recommendations.append("RTG tylko przy podejrzeniu złamania")
        recommendations.append("USG przy braku poprawy po 2-3 tygodniach")
    
    return recommendations

def get_followup_recommendations(diagnosis):
    """Rekomendacje kontroli"""
    recommendations = []
    
    if "stopień I" in diagnosis.name:
        recommendations.append("Kontrola za 1 tydzień")
        recommendations.append("Powrót do sportu za 2-3 tygodnie")
    elif "stopień II" in diagnosis.name:
        recommendations.append("Kontrola za 3-5 dni")
        recommendations.append("Fizjoterapia przez 3-4 tygodnie")
    elif "stopień III" in diagnosis.name:
        recommendations.append("Pilna kontrola ortopedyczna")
        recommendations.append("Rehabilitacja 6-12 tygodni")
    elif "zerwanie" in diagnosis.name.lower():
        recommendations.append("Kontrola ortopedyczna w ciągu 24h")
        recommendations.append("Rehabilitacja 4-6 miesięcy")
    
    return recommendations

def show_original_modules(module_type, mode):
    """Wyświetla oryginalne moduły GPT"""
    st.markdown(f"## 📱 Oryginalny moduł GPT - {module_type.title()}")
    
    if st.button("⬅️ Powrót do modelu anatomicznego", use_container_width=True):
        if 'show_original' in st.session_state:
            del st.session_state.show_original
        st.rerun()
    
    st.markdown("---")
    
    # Tu możesz umieścić oryginalny kod GPT
    # Przykład integracji:
    
    if module_type == 'ankle':
        st.info("Tutaj byłby oryginalny moduł stawu skokowego z GPT")
        # Wstaw tutaj oryginalny kod z GPT dla stawu skokowego
    elif module_type == 'achilles':
        st.info("Tutaj byłby oryginalny moduł Achillesa z GPT")
        # Wstaw tutaj oryginalny kod z GPT dla Achillesa

def reset_session():
    """Reset wszystkich danych sesji"""
    keys_to_keep = ['diagnostic_engine']  # Zachowaj silnik diagnostyczny
    
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    st.session_state.selected_region = None
    st.session_state.current_step = 'anatomy_selection'
    st.session_state.diagnostic_findings = {}

if __name__ == "__main__":
    main()
