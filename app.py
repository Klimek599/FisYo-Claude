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

# Imports modułów
from database.db_manager import DatabaseManager
from database.models import Patient, DiagnosisSession, TestResult
from modules.ankle import AnkleModule
from modules.knee import KneeModule
from modules.shoulder import ShoulderModule
from modules.spine import SpineModule
from components.anatomy_3d import create_3d_anatomy_model
from components.visualizations import create_advanced_charts
from components.ui_components import render_ui_components

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
    /* Import Google Fonts */
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

    .module-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(33, 150, 243, 0.1), transparent);
        transition: left 0.5s;
    }

    .module-card:hover::before {
        left: 100%;
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

    /* Animations */
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

# ===== INICJALIZACJA =====
def initialize_app():
    """Inicjalizacja aplikacji"""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    if 'current_patient' not in st.session_state:
        st.session_state.current_patient = None
    
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    
    if 'selected_module' not in st.session_state:
        st.session_state.selected_module = None
    
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 'patient_selection'
    
    if 'diagnosis_history' not in st.session_state:
        st.session_state.diagnosis_history = []

# ===== GŁÓWNE MODUŁY =====
class ModuleRegistry:
    """Rejestr wszystkich modułów diagnostycznych"""
    
    def __init__(self):
        self.modules = {
            'ankle': AnkleModule(),
            'knee': KneeModule(), 
            'shoulder': ShoulderModule(),
            'spine': SpineModule()
        }
    
    def get_module(self, module_id: str):
        return self.modules.get(module_id)
    
    def get_all_modules(self):
        return self.modules
    
    def get_module_info(self):
        return {
            'ankle': {
                'name': 'Staw skokowy',
                'icon': '🦶',
                'description': 'Skręcenia, złamania, tendinopatie',
                'color': '#FF6B6B',
                'specialties': ['Kostka boczna/przyśrodkowa', 'Ścięgno Achillesa', 'Powięź podeszwowa']
            },
            'knee': {
                'name': 'Kolano', 
                'icon': '🦵',
                'description': 'Więzadła, łąkotki, nadgubierek',
                'color': '#4ECDC4',
                'specialties': ['ACL/PCL/MCL/LCL', 'Meniscus', 'Patellofemoral']
            },
            'shoulder': {
                'name': 'Bark',
                'icon': '💪',
                'description': 'Stożek rotatorów, impingement',
                'color': '#45B7D1',
                'specialties': ['Rotator cuff', 'Impingement', 'Niestabilność']
            },
            'spine': {
                'name': 'Kręgosłup',
                'icon': '🦴', 
                'description': 'Kręgi, dyski, korzonki',
                'color': '#96CEB4',
                'specialties': ['Szyjny', 'Piersiowy', 'Lędźwiowy']
            }
        }

# ===== FUNKCJE GŁÓWNE =====
def main():
    initialize_app()
    
    # Header
    render_main_header()
    
    # Sidebar
    render_sidebar()
    
    # Main workflow
    if st.session_state.workflow_step == 'patient_selection':
        show_patient_selection()
    elif st.session_state.workflow_step == 'module_selection':
        show_module_selection()
    elif st.session_state.workflow_step == 'anatomy_3d':
        show_3d_anatomy_selection()
    elif st.session_state.workflow_step == 'assessment':
        show_assessment()
    elif st.session_state.workflow_step == 'diagnosis':
        show_diagnosis_results()
    elif st.session_state.workflow_step == 'history':
        show_patient_history()
    elif st.session_state.workflow_step == 'analytics':
        show_analytics_dashboard()
    
    # Floating action button
    render_floating_button()

def render_main_header():
    """Renderuje główny nagłówek"""
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🏥 FizjoExpert Pro</h1>
        <h2>AI-Enhanced Diagnostic System</h2>
        <p>Zaawansowany system wspomagania diagnozy z modelem 3D, bazą danych i AI</p>
        <p><i>✨ Integracja GPT Logic + Machine Learning + 3D Anatomy</i></p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderuje sidebar z nawigacją"""
    with st.sidebar:
        # Logo
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
        
        nav_options = {
            'patient_selection': '👤 Wybór pacjenta',
            'module_selection': '🎯 Wybór modułu', 
            'anatomy_3d': '🔬 Model 3D',
            'assessment': '📋 Ocena',
            'diagnosis': '💡 Diagnoza',
            'history': '📚 Historia',
            'analytics': '📊 Analityka'
        }
        
        for step, label in nav_options.items():
            if st.button(label, key=f"nav_{step}", use_container_width=True):
                st.session_state.workflow_step = step
                st.rerun()
        
        st.markdown("---")
        
        # Quick stats
        if st.session_state.current_patient:
            stats = get_patient_stats(st.session_state.current_patient.id)
            st.markdown("### 📊 Statystyki pacjenta")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Wizyty", stats['total_visits'])
                st.metric("Diagnozy", stats['total_diagnoses'])
            with col2:
                st.metric("Ostatnia", stats['last_visit'])
                st.metric("Skuteczność", f"{stats['success_rate']}%")
        
        st.markdown("---")
        
        # Emergency actions
        st.markdown("### 🚨 Akcje specjalne")
        
        if st.button("🆘 Czerwone flagi", use_container_width=True, type="secondary"):
            show_red_flags_checklist()
        
        if st.button("📞 Pilne skierowanie", use_container_width=True, type="secondary"):
            show_emergency_referral()
        
        if st.button("🔄 Reset sesji", use_container_width=True):
            reset_current_session()
            st.rerun()

def show_patient_selection():
    """Ekran wyboru/dodawania pacjenta"""
    st.markdown("## 👤 Zarządzanie pacjentami")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Wyszukaj pacjenta", "➕ Nowy pacjent", "📊 Lista pacjentów"])
    
    with tab1:
        search_and_select_patient()
    
    with tab2:
        add_new_patient()
    
    with tab3:
        show_patient_list()

def search_and_select_patient():
    """Wyszukiwanie i wybór pacjenta"""
    st.markdown("### 🔍 Wyszukaj pacjenta")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "Wyszukaj po imieniu, nazwisku lub PESEL",
            placeholder="Wprowadź imię, nazwisko lub PESEL..."
        )
    
    with col2:
        if st.button("🔍 Szukaj", use_container_width=True, type="primary"):
            if search_term:
                patients = st.session_state.db_manager.search_patients(search_term)
                st.session_state.search_results = patients
    
    # Wyniki wyszukiwania
    if hasattr(st.session_state, 'search_results'):
        if st.session_state.search_results:
            st.markdown("#### 📋 Wyniki wyszukiwania")
            
            for patient in st.session_state.search_results:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **{patient.first_name} {patient.last_name}**  
                        PESEL: {patient.pesel}  
                        Wiek: {calculate_age(patient.birth_date)} lat
                        """)
                    
                    with col2:
                        last_visit = get_last_visit(patient.id)
                        st.markdown(f"""
                        Ostatnia wizyta: {last_visit}  
                        Status: {'Aktywny' if patient.is_active else 'Nieaktywny'}
                        """)
                    
                    with col3:
                        if st.button("Wybierz", key=f"select_{patient.id}", type="primary"):
                            st.session_state.current_patient = patient
                            st.session_state.workflow_step = 'module_selection'
                            st.success(f"Wybrano pacjenta: {patient.first_name} {patient.last_name}")
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.warning("Nie znaleziono pacjentów pasujących do kryteriów wyszukiwania.")

def add_new_patient():
    """Dodawanie nowego pacjenta"""
    st.markdown("### ➕ Dodaj nowego pacjenta")
    
    with st.form("new_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("Imię*", placeholder="Jan")
            last_name = st.text_input("Nazwisko*", placeholder="Kowalski")
            pesel = st.text_input("PESEL*", placeholder="80010112345", max_chars=11)
            birth_date = st.date_input("Data urodzenia*", value=date(1980, 1, 1))
        
        with col2:
            gender = st.selectbox("Płeć", ["M", "K", "Inna"])
            phone = st.text_input("Telefon", placeholder="+48 123 456 789")
            email = st.text_input("Email", placeholder="jan.kowalski@email.com")
            emergency_contact = st.text_input("Kontakt awaryjny", placeholder="Anna Kowalska, +48 987 654 321")
        
        # Dodatkowe informacje medyczne
        st.markdown("#### 🏥 Informacje medyczne")
        col1, col2 = st.columns(2)
        
        with col1:
            allergies = st.text_area("Alergie", placeholder="Brak znanych alergii")
            medications = st.text_area("Aktualne leki", placeholder="Brak stałych leków")
        
        with col2:
            medical_history = st.text_area("Historia chorób", placeholder="Brak istotnych chorób")
            notes = st.text_area("Notatki", placeholder="Dodatkowe informacje")
        
        # Zgody
        st.markdown("#### 📄 Zgody")
        consent_treatment = st.checkbox("Zgoda na leczenie*", value=False)
        consent_data = st.checkbox("Zgoda na przetwarzanie danych osobowych*", value=False)
        consent_marketing = st.checkbox("Zgoda na kontakt marketingowy", value=False)
        
        submitted = st.form_submit_button("➕ Dodaj pacjenta", type="primary", use_container_width=True)
        
        if submitted:
            # Walidacja
            errors = []
            if not all([first_name, last_name, pesel, birth_date]):
                errors.append("Wypełnij wszystkie wymagane pola (oznaczone *)")
            
            if len(pesel) != 11 or not pesel.isdigit():
                errors.append("PESEL musi składać się z 11 cyfr")
            
            if not consent_treatment or not consent_data:
                errors.append("Wymagane zgody muszą być zaznaczone")
            
            # Sprawdź czy PESEL już istnieje
            if st.session_state.db_manager.patient_exists(pesel):
                errors.append("Pacjent z tym numerem PESEL już istnieje w bazie")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Utwórz pacjenta
                patient = Patient(
                    first_name=first_name,
                    last_name=last_name,
                    pesel=pesel,
                    birth_date=birth_date,
                    gender=gender,
                    phone=phone,
                    email=email,
                    emergency_contact=emergency_contact,
                    allergies=allergies,
                    medications=medications,
                    medical_history=medical_history,
                    notes=notes,
                    consent_treatment=consent_treatment,
                    consent_data=consent_data,
                    consent_marketing=consent_marketing
                )
                
                patient_id = st.session_state.db_manager.add_patient(patient)
                patient.id = patient_id
                
                st.session_state.current_patient = patient
                st.success(f"✅ Dodano pacjenta: {first_name} {last_name}")
                st.balloons()
                
                # Automatyczne przejście do wyboru modułu
                st.session_state.workflow_step = 'module_selection'
                st.rerun()

def show_patient_list():
    """Lista wszystkich pacjentów"""
    st.markdown("### 📊 Lista pacjentów")
    
    patients = st.session_state.db_manager.get_all_patients()
    
    if patients:
        # Filtry
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Status", ["Wszyscy", "Aktywni", "Nieaktywni"])
        
        with col2:
            gender_filter = st.selectbox("Płeć", ["Wszystkie", "M", "K", "Inna"])
        
        with col3:
            sort_by = st.selectbox("Sortuj według", ["Nazwisko", "Imię", "Data urodzenia", "Ostatnia wizyta"])
        
        # Zastosuj filtry
        filtered_patients = filter_patients(patients, status_filter, gender_filter)
        sorted_patients = sort_patients(filtered_patients, sort_by)
        
        # Wyświetl tabelę
        df_patients = pd.DataFrame([
            {
                'Imię': p.first_name,
                'Nazwisko': p.last_name,
                'PESEL': p.pesel,
                'Wiek': calculate_age(p.birth_date),
                'Płeć': p.gender,
                'Telefon': p.phone or 'Brak',
                'Ostatnia wizyta': get_last_visit(p.id),
                'Status': 'Aktywny' if p.is_active else 'Nieaktywny',
                'ID': p.id
            }
            for p in sorted_patients
        ])
        
        # Interaktywna tabela z możliwością wyboru
        selected_patients = st.dataframe(
            df_patients.drop(columns=['ID']),
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Akcje dla wybranego pacjenta
        if selected_patients and 'selection' in selected_patients:
            if selected_patients['selection']['rows']:
                selected_idx = selected_patients['selection']['rows'][0]
                selected_patient_id = df_patients.iloc[selected_idx]['ID']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("👤 Wybierz pacjenta", type="primary"):
                        patient = st.session_state.db_manager.get_patient(selected_patient_id)
                        st.session_state.current_patient = patient
                        st.session_state.workflow_step = 'module_selection'
                        st.rerun()
                
                with col2:
                    if st.button("📚 Zobacz historię"):
                        patient = st.session_state.db_manager.get_patient(selected_patient_id)
                        st.session_state.current_patient = patient
                        st.session_state.workflow_step = 'history'
                        st.rerun()
                
                with col3:
                    if st.button("✏️ Edytuj dane"):
                        show_edit_patient_modal(selected_patient_id)
    else:
        st.info("Brak pacjentów w bazie danych. Dodaj pierwszego pacjenta.")

def show_module_selection():
    """Wybór modułu diagnostycznego"""
    st.markdown("## 🎯 Wybór obszaru diagnostycznego")
    
    if not st.session_state.current_patient:
        st.error("Najpierw wybierz pacjenta!")
        return
    
    registry = ModuleRegistry()
    modules_info = registry.get_module_info()
    
    # Szybki dostęp do modelu 3D
    st.markdown("### 🔬 Model 3D - Wybór interaktywny")
    if st.button("🚀 Przejdź do modelu 3D anatomii", type="primary", use_container_width=True):
        st.session_state.workflow_step = 'anatomy_3d'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Lub wybierz moduł bezpośrednio")
    
    # Grid modułów
    cols = st.columns(2)
    
    for i, (module_id, info) in enumerate(modules_info.items()):
        col = cols[i % 2]
        
        with col:
            st.markdown(f"""
            <div class="module-card scale-in" style="border-left: 5px solid {info['color']}">
                <h3>{info['icon']} {info['name']}</h3>
                <p>{info['description']}</p>
                <strong>Specjalizacje:</strong>
                <ul>
            """, unsafe_allow_html=True)
            
            for specialty in info['specialties']:
                st.markdown(f"<li>{specialty}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)
            
            if st.button(f"Wybierz {info['name']}", key=f"module_{module_id}", use_container_width=True):
                st.session_state.selected_module = module_id
                st.session_state.workflow_step = 'assessment'
                
                # Utwórz nową sesję diagnostyczną
                session = DiagnosisSession(
                    patient_id=st.session_state.current_patient.id,
                    module_type=module_id,
                    therapist_name="Current User",  # TODO: Add user management
                    session_date=datetime.now()
                )
                session_id = st.session_state.db_manager.add_diagnosis_session(session)
                session.id = session_id
                st.session_state.current_session = session
                
                st.success(f"Wybrano moduł: {info['name']}")
                st.rerun()

def show_3d_anatomy_selection():
    """Model 3D do wyboru obszaru anatomicznego"""
    st.markdown("## 🔬 Model 3D - Interaktywny wybór obszaru")
    
    if not st.session_state.current_patient:
        st.error("Najpierw wybierz pacjenta!")
        return
    
    # Model 3D
    st.markdown("""
    <div class="anatomy-3d-container fade-in">
        <h3>🎯 Kliknij na model 3D aby wybrać obszar do diagnozy</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Three.js 3D Model
    model_html = create_3d_anatomy_model()
    st.components.v1.html(model_html, height=600)
    
    # Fallback - przyciski wyboru
    st.markdown("### 🖱️ Lub wybierz z listy:")
    
    col1, col2 = st.columns(2)
    
    anatomy_regions = {
        'head_neck': {'name': 'Głowa i szyja', 'icon': '🧠', 'modules': ['spine']},
        'upper_limb': {'name': 'Kończyna górna', 'icon': '💪', 'modules': ['shoulder']},
        'spine': {'name': 'Kręgosłup', 'icon': '🦴', 'modules': ['spine']},
        'lower_limb_hip': {'name': 'Biodro', 'icon': '🦵', 'modules': ['knee']},
        'lower_limb_knee': {'name': 'Kolano', 'icon': '🦵', 'modules': ['knee']},
        'lower_limb_ankle': {'name': 'Staw skokowy', 'icon': '🦶', 'modules': ['ankle']}
    }
    
    for i, (region_id, info) in enumerate(anatomy_regions.items()):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            if st.button(f"{info['icon']} {info['name']}", key=f"region_{region_id}", use_container_width=True):
                # Automatycznie wybierz odpowiedni moduł
                module_id = info['modules'][0]  # Pierwszy dostępny moduł
                st.session_state.selected_module = module_id
                st.session_state.workflow_step = 'assessment'
                
                # Utwórz sesję
                session = DiagnosisSession(
                    patient_id=st.session_state.current_patient.id,
                    module_type=module_id,
                    therapist_name="Current User",
                    session_date=datetime.now()
                )
                session_id = st.session_state.db_manager.add_diagnosis_session(session)
                session.id = session_id
                st.session_state.current_session = session
                
                st.success(f"Wybrano obszar: {info['name']}")
                st.rerun()
    
    # Instrukcje użytkowania
    with st.expander("📖 Instrukcja użytkowania modelu 3D"):
        st.markdown("""
        ### Jak korzystać z modelu 3D:
        
        1. **Obracanie**: Kliknij i przeciągnij lewym przyciskiem myszy
        2. **Zoom**: Użyj rolki myszy lub gestów na touchpadzie
        3. **Przesuwanie**: Kliknij i przeciągnij prawym przyciskiem myszy
        4. **Wybór obszaru**: Kliknij na interesujący Cię obszar anatomiczny
        5. **Reset widoku**: Naciśnij klawisz 'R' lub użyj przycisku Reset
        
        ### Dostępne modele:
        - 🧠 **Głowa i szyja**: Kręgi szyjne, mięśnie szyi
        - 💪 **Bark**: Stożek rotatorów, stawy ramienno-łopatkowy
        - 🦴 **Kręgosłup**: Odcinki: szyjny, piersiowy, lędźwiowy
        - 🦵 **Kolano**: Więzadła krzyżowe, łąkotki, rzepka
        - 🦶 **Staw skokowy**: Kostki, ścięgno Achillesa, więzadła
        """)

def show_assessment():
    """Przeprowadzenie oceny diagnostycznej"""
    if not st.session_state.selected_module or not st.session_state.current_patient:
        st.error("Brak wybranego modułu lub pacjenta!")
        return
    
    registry = ModuleRegistry()
    module = registry.get_module(st.session_state.selected_module)
    
    if not module:
        st.error(f"Nie znaleziono modułu: {st.session_state.selected_module}")
        return
    
    module_info = registry.get_module_info()[st.session_state.selected_module]
    
    st.markdown(f"## 📋 Ocena diagnostyczna - {module_info['icon']} {module_info['name']}")
    
    # Progress tracking
    if 'assessment_progress' not in st.session_state:
        st.session_state.assessment_progress = {
            'interview_completed': False,
            'tests_completed': False,
            'red_flags_checked': False
        }
    
    progress = sum(st.session_state.assessment_progress.values()) / len(st.session_state.assessment_progress)
    
    st.markdown(f"""
    <div class="progress-container">
        <h4>📊 Postęp oceny: {progress*100:.0f}%</h4>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress)
    
    # Wykonaj ocenę przez moduł
    results = module.run_assessment(
        patient=st.session_state.current_patient,
        session=st.session_state.current_session,
        mode="specialist"  # TODO: Add mode selection
    )
    
    if results:
        # Zapisz wyniki do sesji
        st.session_state.assessment_results = results
        
        # Przycisk do diagnozy
        if st.button("🎯 Przejdź do analizy diagnostycznej", type="primary", use_container_width=True):
            st.session_state.workflow_step = 'diagnosis'
            st.rerun()

def show_diagnosis_results():
    """Wyświetlenie wyników diagnozy"""
    if not hasattr(st.session_state, 'assessment_results'):
        st.error("Brak wyników oceny!")
        return
    
    st.markdown("## 💡 Wyniki diagnozy AI")
    
    results = st.session_state.assessment_results
    registry = ModuleRegistry()
    module = registry.get_module(st.session_state.selected_module)
    
    # Generuj diagnozę przez moduł
    diagnosis = module.generate_diagnosis(results)
    
    # Główna diagnoza
    st.markdown(f"""
    <div class="diagnosis-card fade-in">
        <h2>🎯 Prawdopodobna diagnoza</h2>
        <h1>{diagnosis['primary']}</h1>
        <h3>📊 Prawdopodobieństwo: {diagnosis['confidence']:.1f}%</h3>
        <h3>🎯 Poziom pewności: {diagnosis.get('certainty', 85):.1f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Wykresy i wizualizacje
    charts = create_advanced_charts(diagnosis, results)
    
    if charts:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'probability_chart' in charts:
                st.plotly_chart(charts['probability_chart'], use_container_width=True)
        
        with col2:
            if 'test_results_radar' in charts:
                st.plotly_chart(charts['test_results_radar'], use_container_width=True)
    
    # Szczegółowe wyniki
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Powody diagnostyczne")
        if 'reasons' in diagnosis:
            for i, reason in enumerate(diagnosis['reasons'], 1):
                st.markdown(f"""
                <div class="test-result-positive">
                    <strong>{i}.</strong> {reason}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🏆 Diagnoza różnicowa")
        if 'differential' in diagnosis:
            for i, diff_diag in enumerate(diagnosis['differential'][:5], 1):
                confidence_color = "#4CAF50" if diff_diag['probability'] >= 70 else "#FF9800" if diff_diag['probability'] >= 40 else "#F44336"
                st.markdown(f"""
                <div class="metric-card">
                    <strong>{i}. {diff_diag['name']}</strong><br>
                    <span style="color: {confidence_color}">
                        📊 {diff_diag['probability']:.1f}%
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    # Protokół terapeutyczny
    st.markdown("### 🎯 Protokół terapeutyczny")
    if 'treatment' in diagnosis:
        for i, treatment in enumerate(diagnosis['treatment'], 1):
            st.markdown(f"**{i}.** {treatment}")
    
    # Skierowania i followup
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏥 Skierowania")
        if diagnosis.get('referral'):
            if "PILNE" in diagnosis['referral'].upper():
                st.error(f"🚨 {diagnosis['referral']}")
            else:
                st.warning(f"⚠️ {diagnosis['referral']}")
        else:
            st.success("✅ Brak konieczności pilnych skierowań")
    
    with col2:
        st.markdown("### 📅 Plan kontroli")
        if diagnosis.get('followup'):
            for followup in diagnosis['followup']:
                st.markdown(f"• {followup}")
    
    # Zapisz diagnozę do bazy danych
    if st.button("💾 Zapisz diagnozę", type="primary", use_container_width=True):
        save_diagnosis_to_db(diagnosis, results)
        st.success("✅ Diagnoza została zapisana!")
        st.balloons()
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generuj raport PDF"):
            generate_pdf_report(diagnosis, results)
    
    with col2:
        if st.button("📧 Wyślij pacjentowi"):
            send_results_to_patient(diagnosis)
    
    with col3:
        if st.button("🔄 Nowa diagnoza"):
            reset_current_session()
            st.session_state.workflow_step = 'module_selection'
            st.rerun()

def show_patient_history():
    """Historia pacjenta"""
    if not st.session_state.current_patient:
        st.error("Brak wybranego pacjenta!")
        return
    
    patient = st.session_state.current_patient
    st.markdown(f"## 📚 Historia pacjenta - {patient.first_name} {patient.last_name}")
    
    # Pobierz historię z bazy danych
    history = st.session_state.db_manager.get_patient_history(patient.id)
    
    if not history:
        st.info("Brak historii diagnoz dla tego pacjenta.")
        return
    
    # Statystyki
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Łączne wizyty", len(history))
    
    with col2:
        modules_used = len(set(h.module_type for h in history))
        st.metric("Używane moduły", modules_used)
    
    with col3:
        last_visit = max(h.session_date for h in history) if history else "Brak"
        st.metric("Ostatnia wizyta", last_visit.strftime("%d.%m.%Y") if isinstance(last_visit, datetime) else last_visit)
    
    with col4:
        avg_confidence = sum(h.confidence_level for h in history if h.confidence_level) / len([h for h in history if h.confidence_level])
        st.metric("Średnia pewność", f"{avg_confidence:.1f}%")
    
    # Timeline wizyt
    st.markdown("### 📅 Timeline wizyt")
    
    timeline_data = []
    for session in sorted(history, key=lambda x: x.session_date, reverse=True):
        timeline_data.append({
            'Data': session.session_date.strftime("%d.%m.%Y"),
            'Moduł': session.module_type.title(),
            'Diagnoza': session.primary_diagnosis[:50] + "..." if len(session.primary_diagnosis) > 50 else session.primary_diagnosis,
            'Pewność': f"{session.confidence_level:.1f}%" if session.confidence_level else "N/A",
            'Terapeuta': session.therapist_name
        })
    
    df_timeline = pd.DataFrame(timeline_data)
    st.dataframe(df_timeline, use_container_width=True)
    
    # Szczegółowa historia - expandable
    st.markdown("### 🔍 Szczegółowa historia")
    
    for i, session in enumerate(sorted(history, key=lambda x: x.session_date, reverse=True)):
        with st.expander(f"📋 Wizyta {session.session_date.strftime('%d.%m.%Y')} - {session.module_type.title()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Diagnoza główna:** {session.primary_diagnosis}
                
                **Pewność:** {session.confidence_level:.1f}% 
                
                **Terapeuta:** {session.therapist_name}
                
                **Data:** {session.session_date.strftime('%d.%m.%Y %H:%M')}
                """)
            
            with col2:
                if session.treatment_plan:
                    st.markdown("**Plan leczenia:**")
                    st.markdown(session.treatment_plan)
                
                if session.notes:
                    st.markdown("**Notatki:**")
                    st.markdown(session.notes)
    
    # Analiza trendów
    if len(history) > 1:
        st.markdown("### 📊 Analiza trendów")
        
        # Wykres pewności w czasie
        confidence_data = [(h.session_date, h.confidence_level) for h in history if h.confidence_level]
        
        if confidence_data:
            df_confidence = pd.DataFrame(confidence_data, columns=['Data', 'Pewność'])
            
            fig_confidence = px.line(
                df_confidence, 
                x='Data', 
                y='Pewność',
                title='Trend pewności diagnoz w czasie',
                markers=True
            )
            st.plotly_chart(fig_confidence, use_container_width=True)
        
        # Rozkład modułów
        module_counts = {}
        for session in history:
            module_counts[session.module_type] = module_counts.get(session.module_type, 0) + 1
        
        fig_modules = px.pie(
            values=list(module_counts.values()),
            names=list(module_counts.keys()),
            title='Rozkład używanych modułów'
        )
        st.plotly_chart(fig_modules, use_container_width=True)

def show_analytics_dashboard():
    """Dashboard analityczny"""
    st.markdown("## 📊 Dashboard analityczny")
    
    # Sprawdź uprawnienia (TODO: Add user roles)
    # if not check_admin_permissions():
    #     st.error("Brak uprawnień do przeglądania analityki!")
    #     return
    
    # Pobierz dane analityczne
    analytics_data = st.session_state.db_manager.get_analytics_data()
    
    if not analytics_data:
        st.info("Brak danych do analizy.")
        return
    
    # KPI Cards
    st.markdown("### 📈 Kluczowe wskaźniki")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Pacjenci</h3>
            <h2>{}</h2>
            <p>Łączna liczba</p>
        </div>
        """.format(analytics_data['total_patients']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📋 Diagnozy</h3>
            <h2>{}</h2>
            <p>W tym miesiącu</p>
        </div>
        """.format(analytics_data['diagnoses_this_month']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Średnia pewność</h3>
            <h2>{:.1f}%</h2>
            <p>Wszystkich diagnoz</p>
        </div>
        """.format(analytics_data['avg_confidence']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Najczęstszy moduł</h3>
            <h2>{}</h2>
            <p>W tym okresie</p>
        </div>
        """.format(analytics_data['most_used_module']), unsafe_allow_html=True)
    
    # Wykresy analityczne
    col1, col2 = st.columns(2)
    
    with col1:
        # Wykres diagnoz w czasie
        if analytics_data['diagnoses_over_time']:
            fig_time = px.line(
                analytics_data['diagnoses_over_time'],
                x='data',
                y='liczba_diagnoz',
                title='Liczba diagnoz w czasie'
            )
            st.plotly_chart(fig_time, use_container_width=True)
    
    with col2:
        # Rozkład modułów
        if analytics_data['module_usage']:
            fig_modules = px.pie(
                analytics_data['module_usage'],
                values='liczba',
                names='modul',
                title='Popularność modułów'
            )
            st.plotly_chart(fig_modules, use_container_width=True)
    
    # Tabela najczęstszych diagnoz
    st.markdown("### 🏆 Najczęstsze diagnozy")
    
    if analytics_data['top_diagnoses']:
        df_diagnoses = pd.DataFrame(analytics_data['top_diagnoses'])
        st.dataframe(df_diagnoses, use_container_width=True)
    
    # Analiza skuteczności
    st.markdown("### 📊 Analiza skuteczności")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rozkład pewności diagnoz
        if analytics_data['confidence_distribution']:
            fig_confidence = px.histogram(
                analytics_data['confidence_distribution'],
                x='confidence_level',
                title='Rozkład poziomów pewności diagnoz',
                nbins=20
            )
            st.plotly_chart(fig_confidence, use_container_width=True)
    
    with col2:
        # Efektywność terapeutów
        if analytics_data['therapist_effectiveness']:
            fig_therapists = px.bar(
                analytics_data['therapist_effectiveness'],
                x='terapeuta',
                y='srednia_pewnosc',
                title='Średnia pewność diagnoz według terapeutów'
            )
            st.plotly_chart(fig_therapists, use_container_width=True)

# ===== HELPER FUNCTIONS =====

def calculate_age(birth_date):
    """Oblicza wiek na podstawie daty urodzenia"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_last_visit(patient_id):
    """Pobiera datę ostatniej wizyty pacjenta"""
    last_session = st.session_state.db_manager.get_last_session(patient_id)
    if last_session:
        return last_session.session_date.strftime("%d.%m.%Y")
    return "Brak wizyt"

def get_patient_stats(patient_id):
    """Pobiera statystyki pacjenta"""
    return st.session_state.db_manager.get_patient_stats(patient_id)

def filter_patients(patients, status_filter, gender_filter):
    """Filtruje listę pacjentów"""
    filtered = patients
    
    if status_filter == "Aktywni":
        filtered = [p for p in filtered if p.is_active]
    elif status_filter == "Nieaktywni":
        filtered = [p for p in filtered if not p.is_active]
    
    if gender_filter != "Wszystkie":
        filtered = [p for p in filtered if p.gender == gender_filter]
    
    return filtered

def sort_patients(patients, sort_by):
    """Sortuje listę pacjentów"""
    if sort_by == "Nazwisko":
        return sorted(patients, key=lambda p: p.last_name)
    elif sort_by == "Imię":
        return sorted(patients, key=lambda p: p.first_name)
    elif sort_by == "Data urodzenia":
        return sorted(patients, key=lambda p: p.birth_date)
    # TODO: Add sorting by last visit
    return patients

def save_diagnosis_to_db(diagnosis, results):
    """Zapisuje diagnozę do bazy danych"""
    if st.session_state.current_session:
        session = st.session_state.current_session
        session.primary_diagnosis = diagnosis['primary']
        session.confidence_level = diagnosis['confidence']
        session.treatment_plan = '\n'.join(diagnosis.get('treatment', []))
        session.session_notes = json.dumps(results)
        
        st.session_state.db_manager.update_diagnosis_session(session)

def generate_pdf_report(diagnosis, results):
    """Generuje raport PDF"""
    st.info("Funkcja generowania PDF będzie dostępna w przyszłej wersji")

def send_results_to_patient(diagnosis):
    """Wysyła wyniki do pacjenta"""
    st.info("Funkcja wysyłania wyników będzie dostępna w przyszłej wersji")

def reset_current_session():
    """Resetuje bieżącą sesję"""
    keys_to_reset = [
        'current_session', 'assessment_results', 'assessment_progress',
        'selected_module', 'search_results'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def show_red_flags_checklist():
    """Pokazuje checklist czerwonych flag"""
    st.markdown("### 🚨 Checklist czerwonych flag")
    
    red_flags = [
        "Widoczna deformacja kości/stawu",
        "Otwarta rana z przebiciem skóry",
        "Bladość, zimno lub siniec stopy/ręki",
        "Brak tętna obwodowego",
        "Drętwienie/niedowład całej kończyny",
        "Niemożność poruszenia palcami",
        "Silny ból (9-10/10) oporny na leki",
        "Szybko narastający obrzęk całej kończyny",
        "Gorączka >38°C z objawami infekcji",
        "Podejrzenie zespołu ciasnoty"
    ]
    
    detected_flags = []
    
    for flag in red_flags:
        if st.checkbox(flag, key=f"emergency_flag_{flag}"):
            detected_flags.append(flag)
    
    if detected_flags:
        st.error("🚨 CZERWONE FLAGI WYKRYTE! Konieczna pilna interwencja medyczna!")
        for flag in detected_flags:
            st.error(f"⚠️ {flag}")

def show_emergency_referral():
    """Pokazuje opcje pilnego skierowania"""
    st.markdown("### 📞 Pilne skierowanie")
    
    referral_options = {
        "SOR": "Szpitalny Oddział Ratunkowy",
        "Ortopeda": "Pilna konsultacja ortopedyczna",
        "Neurolog": "Pilna konsultacja neurologiczna",
        "Chirurg naczyniowy": "Podejrzenie problemów naczyniowych"
    }
    
    selected_referral = st.selectbox("Wybierz typ skierowania", list(referral_options.keys()))
    
    urgency = st.radio("Pilność", ["Natychmiastowa", "W ciągu godziny", "W ciągu dnia"])
    
    reason = st.text_area("Przyczyna skierowania", placeholder="Opisz objawy i podejrzenia...")
    
    if st.button("📞 Generuj skierowanie", type="primary"):
        generate_emergency_referral(selected_referral, urgency, reason)

def generate_emergency_referral(referral_type, urgency, reason):
    """Generuje pilne skierowanie"""
    patient = st.session_state.current_patient
    
    referral_text = f"""
    🚨 PILNE SKIEROWANIE
    
    Pacjent: {patient.first_name} {patient.last_name}
    PESEL: {patient.pesel}
    Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    
    Skierowanie do: {referral_type}
    Pilność: {urgency}
    
    Przyczyna:
    {reason}
    
    Fizjoterapeuta: Current User
    """
    
    st.code(referral_text)
    st.success("Skierowanie zostało wygenerowane!")

def render_floating_button():
    """Renderuje floating action button"""
    st.markdown("""
    <div class="floating-button" onclick="scrollToTop()">
        ⬆️
    </div>
    
    <script>
    function scrollToTop() {
        window.scrollTo({top: 0, behavior: 'smooth'});
    }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
