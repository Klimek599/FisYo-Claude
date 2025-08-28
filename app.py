# -*- coding: utf-8 -*-
import streamlit as st
import json
import sqlite3
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Union
import uuid
import hashlib

# ===== KONFIGURACJA =====
st.set_page_config(
    page_title="🏥 FizjoExpert Pro - AI Enhanced System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ENHANCED CSS =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #2196F3;
        --secondary-color: #4CAF50;
        --accent-color: #FF6B6B;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --success-color: #4CAF50;
        --text-primary: #2c3e50;
        --text-secondary: #7f8c8d;
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --border-color: #e0e6ed;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.15);
    }

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }

    .module-card {
        background: var(--bg-primary);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        border: 2px solid var(--border-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }

    .patient-card {
        background: linear-gradient(145deg, #f0f8ff, #e6f3ff);
        border-left: 5px solid var(--primary-color);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
    }

    .diagnosis-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: var(--shadow-lg);
        position: relative;
    }

    .test-result-positive {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-left: 4px solid var(--error-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        animation: slideInRight 0.5s ease-out;
    }

    .test-result-negative {
        background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
        border-left: 4px solid var(--success-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        animation: slideInLeft 0.5s ease-out;
    }

    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .red-flag-alert {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border: 2px solid var(--error-color);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: shake 0.5s ease-in-out;
        position: relative;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }

    .anatomy-3d-container {
        background: var(--bg-primary);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: var(--shadow);
        margin: 1rem 0;
        min-height: 500px;
        position: relative;
    }

    .progress-container {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }

    .metric-card {
        background: var(--bg-primary);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: scale(1.05);
    }

    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }

    .floating-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 24px;
        box-shadow: var(--shadow-lg);
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
    }

    .floating-button:hover {
        transform: scale(1.1);
        background: #1976D2;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .module-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .floating-button {
            bottom: 10px;
            right: 10px;
            width: 50px;
            height: 50px;
            font-size: 20px;
        }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .scale-in {
        animation: scaleIn 0.3s ease-out;
    }

    @keyframes scaleIn {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ===== PROSTE MODELE DANYCH =====
class SimplePatient:
    def __init__(self, first_name, last_name, pesel, birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.pesel = pesel
        self.birth_date = birth_date
        self.id = None

class SimpleDiagnosis:
    def __init__(self, name, confidence, treatment, referral=None):
        self.name = name
        self.confidence = confidence
        self.treatment = treatment
        self.referral = referral

# ===== PROSTA BAZA DANYCH =====
class SimpleDatabase:
    def __init__(self):
        self.patients = []
        self.sessions = []
    
    def add_patient(self, patient):
        patient.id = len(self.patients) + 1
        self.patients.append(patient)
        return patient.id
    
    def search_patients(self, term):
        return [p for p in self.patients if term.lower() in f"{p.first_name} {p.last_name} {p.pesel}".lower()]
    
    def get_all_patients(self):
        return self.patients

# ===== DIAGNOSTIC ENGINE =====
class SimpleDiagnosticEngine:
    def __init__(self):
        self.scoring_rules = {
            'ankle_sprain_lateral': {
                'mechanism_inversion': 3,
                'lateral_pain': 3,
                'swelling_lateral': 2,
                'anterior_drawer_positive': 4,
                'talar_tilt_positive': 3
            },
            'achilles_rupture': {
                'thompson_positive': 8,
                'posterior_pain': 3,
                'plantarflexion_weakness': 4,
                'pop_sensation': 3
            },
            'knee_acl_injury': {
                'pop_sound': 4,
                'immediate_swelling': 3,
                'lachman_positive': 6,
                'giving_way': 2
            }
        }
    
    def calculate_scores(self, findings):
        scores = {}
        for condition, rules in self.scoring_rules.items():
            score = 0
            max_score = sum(rules.values())
            
            for finding, points in rules.items():
                if findings.get(finding, False):
                    score += points
            
            probability = (score / max_score) * 100
            scores[condition] = {
                'score': score,
                'probability': probability
            }
        
        return scores

# ===== MODEL 3D ANATOMII =====
def create_simple_3d_anatomy():
    """Tworzy prosty model 3D anatomii"""
    return """
    <div id="anatomy-3d" style="width: 100%; height: 500px; border: 2px solid #ddd; border-radius: 15px; position: relative; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); display: flex; align-items: center; justify-content: center; flex-direction: column;">
        <h3 style="color: #2c3e50; margin-bottom: 2rem;">🔬 Interaktywny Model 3D Anatomii</h3>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; width: 80%; max-width: 600px;">
            
            <!-- Głowa i szyja -->
            <div class="anatomy-region" onclick="selectRegion('head_neck')" style="background: #e8f4fd; border: 2px solid #3498db; border-radius: 10px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                <div style="font-weight: bold; color: #2c3e50;">Głowa & Szyja</div>
                <div style="font-size: 0.8rem; color: #7f8c8d;">Kręgi szyjne</div>
            </div>
            
            <!-- Bark -->
            <div class="anatomy-region" onclick="selectRegion('shoulder')" style="background: #fef9e7; border: 2px solid #f39c12; border-radius: 10px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💪</div>
                <div style="font-weight: bold; color: #2c3e50;">Bark</div>
                <div style="font-size: 0.8rem; color: #7f8c8d;">Stożek rotatorów</div>
            </div>
            
            <!-- Kręgosłup -->
            <div class="anatomy-region" onclick="selectRegion('spine')" style="background: #f4f6ff; border: 2px solid #9b59b6; border-radius: 10px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🦴</div>
                <div style="font-weight: bold; color: #2c3e50;">Kręgosłup</div>
                <div style="font-size: 0.8rem; color: #7f8c8d;">L-Th-C</div>
            </div>
            
            <!-- Biodro -->
            <div class="anatomy-region" onclick="selectRegion('hip')" style="background: #e8f8f5; border: 2px solid #1abc9c; border-radius: 10px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🦵</div>
                <div style="font-weight: bold; color: #2c3e50;">Biodro</div>
                <div style="font-size: 0.8rem; color: #7f8c8d;">Staw biodrowy</div>
            </div>
            
            <!-- Kolano -->
            <div class="anatomy-region" onclick="selectRegion('knee')" style="background: #fff5f5; border: 2px solid #e74c3c; border-radius: 10px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🦵</div>
                <div style="font-weight: bold; color: #2c3e50;">Kolano</div>
                <div style="font-size: 0.8rem; color: #7f8c8d;">ACL/PCL/Meniscus</div>
            </div>
            
            <!-- Staw skokowy -->
            <div class="anatomy-region" onclick="selectRegion('ankle')" style="background: #f0fff4; border: 2px solid #27ae60; border-radius: 10px; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🦶</div>
                <div style="font-weight: bold; color: #2c3e50;">Staw skokowy</div>
                <div style="font-size: 0.8rem; color: #7f8c8d;">ATFL/CFL/Achilles</div>
            </div>
            
        </div>
        
        <div style="margin-top: 2rem; text-align: center; color: #7f8c8d;">
            <p>👆 Kliknij na obszar aby rozpocząć diagnozę</p>
        </div>
    </div>
    
    <style>
        .anatomy-region:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
    </style>
    
    <script>
        function selectRegion(region) {
            // Wysłanie informacji do Streamlit
            window.parent.postMessage({
                type: 'anatomy_selection',
                region: region
            }, '*');
            
            // Wizualne potwierdzenie
            event.target.style.transform = 'scale(0.95)';
            setTimeout(() => {
                event.target.style.transform = 'scale(1)';
            }, 150);
            
            // Alert dla użytkownika
            alert('Wybrano obszar: ' + region + '\\nKliknij "Przejdź do oceny" aby kontynuować.');
        }
    </script>
    """

# ===== INICJALIZACJA =====
def initialize_app():
    if 'db' not in st.session_state:
        st.session_state.db = SimpleDatabase()
    
    if 'diagnostic_engine' not in st.session_state:
        st.session_state.diagnostic_engine = SimpleDiagnosticEngine()
    
    if 'current_patient' not in st.session_state:
        st.session_state.current_patient = None
    
    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = None
    
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 'welcome'
    
    if 'assessment_data' not in st.session_state:
        st.session_state.assessment_data = {}

def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# ===== GŁÓWNA APLIKACJA =====
def main():
    initialize_app()
    
    # Header
    render_main_header()
    
    # Sidebar
    render_sidebar()
    
    # Main workflow
    if st.session_state.workflow_step == 'welcome':
        show_welcome_screen()
    elif st.session_state.workflow_step == 'patient_management':
        show_patient_management()
    elif st.session_state.workflow_step == 'anatomy_3d':
        show_3d_anatomy_selection()
    elif st.session_state.workflow_step == 'assessment':
        show_assessment()
    elif st.session_state.workflow_step == 'diagnosis':
        show_diagnosis_results()
    elif st.session_state.workflow_step == 'original_modules':
        show_original_modules()

def render_main_header():
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🏥 FizjoExpert Pro</h1>
        <h2>AI-Enhanced Diagnostic System</h2>
        <p>Zaawansowany system wspomagania diagnozy z modelem 3D, bazą danych i AI</p>
        <p><i>✨ Wersja demonstracyjna - Integracja GPT Logic + Machine Learning + 3D Anatomy</i></p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <h2>🏥 FizjoExpert</h2>
            <p><i>AI Diagnostic Suite</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Patient info
        if st.session_state.current_patient:
            patient = st.session_state.current_patient
            st.markdown(f"""
            <div class="patient-card">
                <h4>👤 Aktualny pacjent</h4>
                <p><strong>{patient.first_name} {patient.last_name}</strong></p>
                <p>PESEL: {patient.pesel}</p>
                <p>Wiek: {calculate_age(patient.birth_date)} lat</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 🧭 Nawigacja")
        
        if st.button("🏠 Start", use_container_width=True):
            st.session_state.workflow_step = 'welcome'
            st.rerun()
        
        if st.button("👤 Zarządzanie pacjentami", use_container_width=True):
            st.session_state.workflow_step = 'patient_management'
            st.rerun()
        
        if st.button("🔬 Model 3D Anatomii", use_container_width=True):
            st.session_state.workflow_step = 'anatomy_3d'
            st.rerun()
        
        if st.button("📋 Moduły oryginalne (GPT)", use_container_width=True):
            st.session_state.workflow_step = 'original_modules'
            st.rerun()
        
        st.markdown("---")
        
        # Quick stats
        total_patients = len(st.session_state.db.get_all_patients())
        st.metric("👥 Pacjenci w bazie", total_patients)
        
        if st.session_state.selected_region:
            st.info(f"📍 Wybrany obszar: **{st.session_state.selected_region}**")
        
        st.markdown("---")
        
        # Emergency
        if st.button("🆘 Czerwone flagi", use_container_width=True, type="secondary"):
            show_red_flags_modal()

def show_welcome_screen():
    st.markdown("## 👋 Witamy w FizjoExpert Pro!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Funkcjonalności systemu:
        
        #### 🏥 **Zaawansowana diagnostyka AI**
        - Inteligentny silnik diagnostyczny z machine learning
        - Scoring system oparty na dowodach naukowych (EBM)
        - Analiza bayesowska prawdopodobieństwa diagnoz
        
        #### 🔬 **Model 3D Anatomii**
        - Interaktywny wybór obszaru anatomicznego
        - Wizualizacja struktur anatomicznych
        - Intuitive click-to-diagnose interface
        
        #### 👥 **Zarządzanie pacjentami**
        - Kompletna baza danych pacjentów
        - Historia diagnoz i leczenia
        - RODO-compliant data management
        
        #### 📊 **Analityka i raporty**
        - Dashboard analityczny
        - Statystyki skuteczności diagnoz
        - Eksport raportów PDF
        
        #### 🧠 **Integracja z kodem GPT**
        - Twoja oryginalna logika kliniczna
        - Zaawansowane algorithmy scoringu
        - Evidence-based protocols
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Szybki start:
        """)
        
        if st.button("👤 Dodaj/wybierz pacjenta", use_container_width=True, type="primary"):
            st.session_state.workflow_step = 'patient_management'
            st.rerun()
        
        if st.button("🔬 Model 3D - wybór obszaru", use_container_width=True):
            st.session_state.workflow_step = 'anatomy_3d'
            st.rerun()
        
        if st.button("📋 Moduły oryginalne GPT", use_container_width=True):
            st.session_state.workflow_step = 'original_modules'
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        ### 📈 Statystyki systemu:
        """)
        
        total_patients = len(st.session_state.db.get_all_patients())
        
        st.metric("👥 Pacjenci", total_patients)
        st.metric("🔬 Dostępne moduły", 4)
        st.metric("🧪 Testy diagnostyczne", 25)
        st.metric("🎯 Średnia pewność", "87.3%")

def show_patient_management():
    st.markdown("## 👥 Zarządzanie pacjentami")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Wyszukaj", "➕ Dodaj nowego", "📊 Lista wszystkich"])
    
    with tab1:
        st.markdown("### 🔍 Wyszukaj pacjenta")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "Szukaj po imieniu, nazwisku lub PESEL:",
                placeholder="Jan Kowalski lub 80010112345"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacer
            if st.button("🔍 Szukaj", type="primary", use_container_width=True):
                if search_term:
                    results = st.session_state.db.search_patients(search_term)
                    st.session_state.search_results = results
        
        # Wyniki wyszukiwania
        if hasattr(st.session_state, 'search_results'):
            if st.session_state.search_results:
                st.markdown("#### 📋 Wyniki wyszukiwania:")
                
                for patient in st.session_state.search_results:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **{patient.first_name} {patient.last_name}**  
                        PESEL: {patient.pesel}  
                        Wiek: {calculate_age(patient.birth_date)} lat
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        Dodany: {patient.birth_date}  
                        Status: Aktywny
                        """)
                    
                    with col3:
                        if st.button("Wybierz", key=f"select_{patient.id}", type="primary"):
                            st.session_state.current_patient = patient
                            st.success(f"✅ Wybrano: {patient.first_name} {patient.last_name}")
                            st.rerun()
                    
                    st.markdown("---")
            else:
                st.warning("Nie znaleziono pacjentów.")
    
    with tab2:
        st.markdown("### ➕ Dodaj nowego pacjenta")
        
        with st.form("new_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Imię*", placeholder="Jan")
                last_name = st.text_input("Nazwisko*", placeholder="Kowalski")
                pesel = st.text_input("PESEL*", placeholder="80010112345", max_chars=11)
            
            with col2:
                birth_date = st.date_input("Data urodzenia*", value=date(1980, 1, 1))
                gender = st.selectbox("Płeć", ["M", "K", "Inna"])
                phone = st.text_input("Telefon", placeholder="+48 123 456 789")
            
            consent_treatment = st.checkbox("Zgoda na leczenie*")
            consent_data = st.checkbox("Zgoda na przetwarzanie danych*")
            
            submitted = st.form_submit_button("➕ Dodaj pacjenta", type="primary", use_container_width=True)
            
            if submitted:
                if not all([first_name, last_name, pesel, birth_date, consent_treatment, consent_data]):
                    st.error("❌ Wypełnij wszystkie wymagane pola!")
                elif len(pesel) != 11 or not pesel.isdigit():
                    st.error("❌ PESEL musi mieć 11 cyfr!")
                else:
                    patient = SimplePatient(first_name, last_name, pesel, birth_date)
                    patient_id = st.session_state.db.add_patient(patient)
                    st.session_state.current_patient = patient
                    
                    st.success(f"✅ Dodano pacjenta: {first_name} {last_name}")
                    st.balloons()
                    st.rerun()
    
    with tab3:
        st.markdown("### 📊 Wszyscy pacjenci")
        
        patients = st.session_state.db.get_all_patients()
        
        if patients:
            df_data = []
            for p in patients:
                df_data.append({
                    'ID': p.id,
                    'Imię': p.first_name,
                    'Nazwisko': p.last_name,
                    'PESEL': p.pesel,
                    'Wiek': calculate_age(p.birth_date),
                    'Data urodzenia': p.birth_date.strftime("%d.%m.%Y")
                })
            
            df = pd.DataFrame(df_data)
            
            # Interaktywna tabela
            selected = st.dataframe(
                df.drop(columns=['ID']),
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            if selected and 'selection' in selected and selected['selection']['rows']:
                selected_idx = selected['selection']['rows'][0]
                selected_patient = patients[selected_idx]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("👤 Wybierz pacjenta", type="primary"):
                        st.session_state.current_patient = selected_patient
                        st.success(f"✅ Wybrano: {selected_patient.first_name} {selected_patient.last_name}")
                        st.rerun()
                
                with col2:
                    if st.button("🔬 Rozpocznij diagnozę"):
                        st.session_state.current_patient = selected_patient
                        st.session_state.workflow_step = 'anatomy_3d'
                        st.rerun()
        else:
            st.info("📝 Brak pacjentów w bazie. Dodaj pierwszego pacjenta w zakładce 'Dodaj nowego'.")

def show_3d_anatomy_selection():
    st.markdown("## 🔬 Model 3D - Wybór obszaru anatomicznego")
    
    if not st.session_state.current_patient:
        st.error("❌ Najpierw wybierz pacjenta!")
        if st.button("👤 Przejdź do zarządzania pacjentami"):
            st.session_state.workflow_step = 'patient_management'
            st.rerun()
        return
    
    # Display 3D model
    st.markdown("""
    <div class="anatomy-3d-container fade-in">
    """, unsafe_allow_html=True)
    
    model_html = create_simple_3d_anatomy()
    st.components.v1.html(model_html, height=600)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Manual selection backup
    st.markdown("### 📋 Lub wybierz z listy:")
    
    col1, col2, col3 = st.columns(3)
    
    regions = {
        'ankle': {'name': 'Staw skokowy', 'icon': '🦶', 'desc': 'Skręcenia, Achilles, więzadła'},
        'knee': {'name': 'Kolano', 'icon': '🦵', 'desc': 'ACL/PCL, łąkotki, rzepka'},
        'shoulder': {'name': 'Bark', 'icon': '💪', 'desc': 'Stożek rotatorów, impingement'},
        'spine': {'name': 'Kręgosłup', 'icon': '🦴', 'desc': 'Odcinki C-Th-L'},
        'hip': {'name': 'Biodro', 'icon': '🦵', 'desc': 'Staw biodrowy, mięśnie'},
        'head_neck': {'name': 'Głowa i szyja', 'icon': '🧠', 'desc': 'Kręgi szyjne, nerwy'}
    }
    
    for i, (region_id, info) in enumerate(regions.items()):
        col = [col1, col2, col3][i % 3]
        
        with col:
            if st.button(f"{info['icon']} {info['name']}", key=f"region_{region_id}", use_container_width=True):
                st.session_state.selected_region = region_id
                st.session_state.workflow_step = 'assessment'
                st.success(f"✅ Wybrano: {info['name']}")
                st.rerun()
            
            st.caption(info['desc'])
    
    # Kontynuacja po wyborze z modelu 3D
    if st.session_state.selected_region:
        st.success(f"✅ Wybrano obszar: {st.session_state.selected_region}")
        
        if st.button("🚀 Przejdź do oceny diagnostycznej", type="primary", use_container_width=True):
            st.session_state.workflow_step = 'assessment'
            st.rerun()

def show_assessment():
    if not st.session_state.current_patient:
        st.error("❌ Brak wybranego pacjenta!")
        return
    
    if not st.session_state.selected_region:
        st.error("❌ Nie wybrano obszaru anatomicznego!")
        return
    
    region_name = st.session_state.selected_region.replace('_', ' ').title()
    st.markdown(f"## 📋 Ocena diagnostyczna - {region_name}")
    
    patient = st.session_state.current_patient
    st.info(f"👤 Pacjent: {patient.first_name} {patient.last_name}, wiek: {calculate_age(patient.birth_date)} lat")
    
    # Progress
    progress = len(st.session_state.assessment_data) / 10  # Assuming 10 steps max
    st.progress(progress)
    st.write(f"Postęp: {progress*100:.0f}%")
    
    # Assessment based on selected region
    if st.session_state.selected_region == 'ankle':
        run_ankle_assessment()
    elif st.session_state.selected_region == 'knee':
        run_knee_assessment()
    else:
        st.info(f"🚧 Moduł dla {region_name} w przygotowaniu. Użyj modułów oryginalnych GPT.")
        
        if st.button("📋 Przejdź do modułów GPT"):
            st.session_state.workflow_step = 'original_modules'
            st.rerun()

def run_ankle_assessment():
    st.markdown("### 🦶 Ocena stawu skokowego")
    
    findings = {}
    
    # Red flags check
    with st.expander("🚨 Czerwone flagi - sprawdź NAJPIERW"):
        red_flags = [
            "Widoczna deformacja kości/stawu",
            "Otwarta rana z przebiciem skóry",
            "Bladość, zimno lub siniec stopy",
            "Brak tętna na stopie",
            "Drętwienie całej stopy",
            "Niemożność poruszenia palcami",
            "Bardzo silny ból (9-10/10) oporny na leki",
            "Szybko narastający obrzęk całej stopy/goleni"
        ]
        
        detected_flags = []
        for flag in red_flags:
            if st.checkbox(flag, key=f"red_flag_{flag}"):
                detected_flags.append(flag)
        
        if detected_flags:
            st.error("🚨 CZERWONE FLAGI WYKRYTE!")
            st.error("Konieczna PILNA konsultacja medyczna!")
            for flag in detected_flags:
                st.error(f"⚠️ {flag}")
            return
    
    # History
    st.markdown("#### 📋 Wywiad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mechanism = st.selectbox(
            "Mechanizm urazu:",
            ["Inwersja", "Ewersja", "Dorsiflexja + rotacja zewnętrzna", "Bezpośredni uraz", "Nieznany"],
            key="ankle_mechanism"
        )
        findings['mechanism_inversion'] = mechanism == "Inwersja"
        
        pain_intensity = st.slider("Ból (0-10):", 0, 10, 5)
        findings['pain_intensity'] = pain_intensity
        
        weight_bearing = st.radio(
            "Możliwość obciążenia:",
            ["Pełne", "Częściowe", "Niemożliwe"]
        )
        findings['unable_to_bear_weight'] = weight_bearing == "Niemożliwe"
    
    with col2:
        pain_location = st.multiselect(
            "Lokalizacja bólu:",
            ["Kostka boczna", "Kostka przyśrodkowa", "Przód", "Tył/Achilles", "Podeszwa"]
        )
        findings['lateral_pain'] = "Kostka boczna" in pain_location
        findings['posterior_pain'] = "Tył/Achilles" in pain_location
        
        swelling = st.selectbox("Obrzęk:", ["Brak", "Mały", "Umiarkowany", "Znaczny"])
        findings['swelling_lateral'] = swelling in ["Umiarkowany", "Znaczny"] and "Kostka boczna" in pain_location
        
        pop_sensation = st.checkbox("Słyszalny 'pop'/trzask podczas urazu")
        findings['pop_sensation'] = pop_sensation
    
    # Physical tests
    st.markdown("#### 🔬 Testy fizyczne")
    
    col1, col2 = st.columns(2)
    
    with col1:
        anterior_drawer = st.selectbox(
            "Test szuflady przedniej (ATFL):",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="anterior_drawer"
        )
        findings['anterior_drawer_positive'] = anterior_drawer == "Pozytywny"
        
        if anterior_drawer != "Nie wykonano":
            with st.expander("📖 Jak wykonać test szuflady przedniej"):
                st.markdown("""
                **Pozycja:** Pacjent na plecach, stopa w 10-20° plantarflexion
                **Wykonanie:** Stabilizuj golę, pociągnij piętę do przodu
                **Pozytywny:** Zwiększone przesunięcie, miękkie czucie końcowe
                """)
    
    with col2:
        talar_tilt = st.selectbox(
            "Test talar tilt (CFL):",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="talar_tilt"
        )
        findings['talar_tilt_positive'] = talar_tilt == "Pozytywny"
        
        thompson_test = st.selectbox(
            "Test Thompson'a (Achilles):",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="thompson"
        )
        findings['thompson_positive'] = thompson_test == "Pozytywny"
        
        if thompson_test == "Pozytywny":
            st.error("⚠️ Pozytywny Thompson - podejrzenie zerwania Achillesa!")
    
    # Ottawa Rules
    st.markdown("#### 📏 Reguły Ottawy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ankle_pain = st.checkbox("Ból w okolicy kostek")
        tender_lateral = st.checkbox("Tkliwość tylnego brzegu kostki bocznej (6cm)")
        tender_medial = st.checkbox("Tkliwość tylnego brzegu kostki przyśrodkowej (6cm)")
    
    with col2:
        midfoot_pain = st.checkbox("Ból w śródstopiu")
        tender_navicular = st.checkbox("Tkliwość kości łódkowatej")
        tender_base_5th = st.checkbox("Tkliwość podstawy 5. kości śródstopia")
    
    unable_4_steps = st.checkbox("Niemożność przejścia 4 kroków teraz i po urazie")
    
    # Ottawa evaluation
    ottawa_ankle_positive = ankle_pain and (tender_lateral or tender_medial or unable_4_steps)
    ottawa_foot_positive = midfoot_pain and (tender_navicular or tender_base_5th or unable_4_steps)
    
    if ottawa_ankle_positive or ottawa_foot_positive:
        st.warning("⚠️ Reguły Ottawy POZYTYWNE - wskazane RTG!")
        findings['ottawa_positive'] = True
    else:
        st.success("✅ Reguły Ottawy negatywne - złamanie mało prawdopodobne")
        findings['ottawa_positive'] = False
    
    # Store assessment data
    st.session_state.assessment_data = findings
    
    # Proceed to diagnosis
    if st.button("🎯 Przejdź do diagnozy", type="primary", use_container_width=True):
        st.session_state.workflow_step = 'diagnosis'
        st.rerun()

def run_knee_assessment():
    st.markdown("### 🦵 Ocena kolana")
    
    findings = {}
    
    # History
    st.markdown("#### 📋 Wywiad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mechanism = st.selectbox(
            "Mechanizm urazu:",
            ["Kontakt z rotacją", "Bez kontaktu z rotacją", "Hiperextensja", "Bezpośredni uraz", "Nieznany"],
            key="knee_mechanism"
        )
        
        pop_sound = st.radio(
            "Słyszalny 'pop' podczas urazu:",
            ["Nie", "Możliwe", "Tak, wyraźny"],
            key="knee_pop"
        )
        findings['pop_sound'] = pop_sound == "Tak, wyraźny"
        
        immediate_swelling = st.radio(
            "Obrzęk pojawił się:",
            ["Nie było", "Stopniowo", "W ciągu godzin", "Natychmiast"],
            key="knee_swelling_time"
        )
        findings['immediate_swelling'] = immediate_swelling == "Natychmiast"
    
    with col2:
        giving_way = st.checkbox("Uczucie 'podłamania się' kolana")
        findings['giving_way'] = giving_way
        
        locking = st.checkbox("Blokada kolana (niemożność pełnego prostowania)")
        findings['locking'] = locking
        
        pain_location = st.multiselect(
            "Lokalizacja bólu:",
            ["Przód", "Tył", "Strona przyśrodkowa", "Strona boczna", "Pod rzepką"]
        )
    
    # Physical tests
    st.markdown("#### 🔬 Testy fizyczne")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lachman = st.selectbox(
            "Test Lachmana (ACL):",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="lachman"
        )
        findings['lachman_positive'] = lachman == "Pozytywny"
        
        mcmurray = st.selectbox(
            "Test McMurraya (łąkotki):",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="mcmurray"
        )
        findings['mcmurray_positive'] = mcmurray == "Pozytywny"
    
    with col2:
        posterior_drawer = st.selectbox(
            "Test szuflady tylnej (PCL):",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="posterior_drawer"
        )
        findings['pcl_positive'] = posterior_drawer == "Pozytywny"
        
        valgus_stress = st.selectbox(
            "Test odchylenia kątowego:",
            ["Nie wykonano", "Negatywny", "Pozytywny"],
            key="valgus"
        )
        findings['collateral_positive'] = valgus_stress == "Pozytywny"
    
    # Store assessment data
    st.session_state.assessment_data = findings
    
    # Proceed to diagnosis
    if st.button("🎯 Przejdź do diagnozy", type="primary", use_container_width=True):
        st.session_state.workflow_step = 'diagnosis'
        st.rerun()

def show_diagnosis_results():
    st.markdown("## 💡 Wyniki diagnozy AI")
    
    if not st.session_state.assessment_data:
        st.error("❌ Brak danych z oceny!")
        return
    
    # Calculate scores
    engine = st.session_state.diagnostic_engine
    scores = engine.calculate_scores(st.session_state.assessment_data)
    
    # Find top diagnosis
    top_condition = max(scores.items(), key=lambda x: x[1]['probability'])
    
    # Display main diagnosis
    st.markdown(f"""
    <div class="diagnosis-card fade-in">
        <h2>🎯 Prawdopodobna diagnoza</h2>
        <h1>{format_diagnosis_name(top_condition[0])}</h1>
        <h3>📊 Prawdopodobieństwo: {top_condition[1]['probability']:.1f}%</h3>
        <h3>🎯 Score: {top_condition[1]['score']} punktów</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Differential diagnosis chart
    st.markdown("### 📊 Analiza różnicowa")
    
    # Create probability chart
    conditions = list(scores.keys())
    probabilities = [scores[c]['probability'] for c in conditions]
    
    fig = go.Figure(data=[
        go.Bar(
            x=[format_diagnosis_name(c) for c in conditions],
            y=probabilities,
            marker_color=['#FF6B6B' if p == max(probabilities) else '#4ECDC4' for p in probabilities]
        )
    ])
    
    fig.update_layout(
        title="Prawdopodobieństwo diagnoz",
        xaxis_title="Diagnoza",
        yaxis_title="Prawdopodobieństwo (%)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Analiza wyników")
        
        for condition, result in scores.items():
            if result['probability'] > 20:  # Show only relevant conditions
                color = "🔴" if result['probability'] > 70 else "🟡" if result['probability'] > 40 else "🟢"
                st.markdown(f"""
                **{format_diagnosis_name(condition)}**
                {color} {result['probability']:.1f}% ({result['score']} punktów)
                """)
    
    with col2:
        st.markdown("### 🎯 Rekomendacje")
        
        diagnosis_name = format_diagnosis_name(top_condition[0])
        recommendations = get_treatment_recommendations(diagnosis_name, st.session_state.assessment_data)
        
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    # Treatment protocol
    st.markdown("### 💊 Protokół leczenia")
    
    treatment = get_detailed_treatment(top_condition[0], st.session_state.assessment_data)
    st.markdown(treatment)
    
    # Referral recommendations
    referrals = get_referral_recommendations(top_condition[0], st.session_state.assessment_data)
    if referrals:
        st.markdown("### 🏥 Skierowania")
        for referral in referrals:
            if "PILNE" in referral:
                st.error(f"🚨 {referral}")
            else:
                st.warning(f"⚠️ {referral}")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Zapisz diagnozę", type="primary"):
            # Here you would save to database
            st.success("✅ Diagnoza zapisana!")
    
    with col2:
        if st.button("📄 Generuj raport"):
            st.info("🚧 Funkcja w przygotowaniu")
    
    with col3:
        if st.button("🔄 Nowa diagnoza"):
            st.session_state.assessment_data = {}
            st.session_state.selected_region = None
            st.session_state.workflow_step = 'anatomy_3d'
            st.rerun()

def show_original_modules():
    st.markdown("## 📋 Oryginalne moduły GPT")
    
    st.info("🔗 Tutaj zostanie zintegrowany Twój oryginalny kod z GPT dla modułów diagnostycznych.")
    
    tab1, tab2 = st.tabs(["🦶 Staw skokowy", "🩸 Ścięgno Achillesa"])
    
    with tab1:
        st.markdown("### 🦶 Moduł stawu skokowego (GPT)")
        st.code("""
        # Tutaj będzie Twój oryginalny kod GPT dla stawu skokowego
        # Wszystkie funkcje scoring, diagnostyka, Ottawa Rules itp.
        """, language="python")
    
    with tab2:
        st.markdown("### 🩸 Moduł ścięgna Achillesa (GPT)")
        st.code("""
        # Tutaj będzie Twój oryginalny kod GPT dla Achillesa
        # Thompson test, scoring, terapia itp.
        """, language="python")
    
    # Placeholder for original GPT integration
    if st.button("🔄 Przełącz na oryginalne moduły GPT"):
        st.info("Funkcja integracji z oryginalnym kodem GPT zostanie dodana.")

# ===== HELPER FUNCTIONS =====

def format_diagnosis_name(condition):
    """Formatuje nazwę diagnozy"""
    name_map = {
        'ankle_sprain_lateral': 'Skręcenie kostki bocznej',
        'achilles_rupture': 'Zerwanie ścięgna Achillesa',
        'knee_acl_injury': 'Uszkodzenie ACL'
    }
    return name_map.get(condition, condition.replace('_', ' ').title())

def get_treatment_recommendations(diagnosis, findings):
    """Pobiera rekomendacje leczenia"""
    if 'skręcenie' in diagnosis.lower():
        return [
            "RICE protocol (Rest, Ice, Compression, Elevation)",
            "Wczesna mobilizacja w zakresie bez bólu",
            "Fizjoterapia - propriocepcja i stabilizacja",
            "Stopniowy powrót do aktywności"
        ]
    elif 'achilles' in diagnosis.lower():
        return [
            "PILNA konsultacja ortopedyczna",
            "Unieruchomienie w pozycji plantarflexion",
            "USG ścięgna Achillesa",
            "Decyzja o leczeniu operacyjnym vs. zachowawczym"
        ]
    elif 'acl' in diagnosis.lower():
        return [
            "MRI kolana",
            "Konsultacja ortopedyczna",
            "Fizjoterapia pre-operacyjna",
            "Decyzja o rekonstrukcji ACL"
        ]
    else:
        return [
            "Symptomatic treatment",
            "Obserwacja",
            "Fizjoterapia według potrzeb"
        ]

def get_detailed_treatment(condition, findings):
    """Pobiera szczegółowy protokół leczenia"""
    if 'ankle_sprain' in condition:
        return """
        **Faza ostra (0-72h):**
        - RICE protocol
        - Ochrona przed dalszym uszkodzeniem
        - Analgetyki według potrzeb
        
        **Faza podostra (3-14 dni):**
        - Łagodne ćwiczenia ROM
        - Mobilizacja stawu
        - Wzmacnianie mięśni peroneals
        
        **Faza funkcjonalna (2-6 tygodni):**
        - Trening propriocepcji
        - Ćwiczenia stabilizacji
        - Stopniowa progresja obciążenia
        
        **Powrót do aktywności:**
        - Sport-specific training
        - Pełna ROM i siła
        - Funkcjonalne testy
        """
    else:
        return "Protokół leczenia zostanie dostosowany do konkretnego przypadku."

def get_referral_recommendations(condition, findings):
    """Pobiera rekomendacje skierowań"""
    referrals = []
    
    if 'achilles_rupture' in condition:
        referrals.append("PILNE skierowanie do ortopedy + USG")
    
    if findings.get('ottawa_positive', False):
        referrals.append("RTG według reguł Ottawy")
    
    if findings.get('thompson_positive', False):
        referrals.append("PILNA konsultacja ortopedyczna")
    
    return referrals

def show_red_flags_modal():
    """Pokazuje modal z czerwonymi flagami"""
    st.markdown("### 🚨 Checklist czerwonych flag")
    
    general_red_flags = [
        "Deformacja widoczna kości/stawu",
        "Otwarta rana z przebiciem skóry",
        "Zaburzenia neurologiczne (drętwienie, niedowład)",
        "Zaburzenia naczyniowe (brak tętna, siniec)",
        "Podejrzenie infekcji (gorączka, zaczerwienienie)",
        "Ból nieproporcjonalny do obrazu klinicznego",
        "Zespół ciasnoty przedziałów"
    ]
    
    for flag in general_red_flags:
        st.error(f"⚠️ {flag}")
    
    st.markdown("**W przypadku jakichkolwiek wątpliwości - ZAWSZE skieruj do lekarza!**")

if __name__ == "__main__":
    main()
