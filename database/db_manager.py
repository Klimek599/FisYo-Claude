import sqlite3
import json
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from .models import Patient, DiagnosisSession, TestResult

class DatabaseManager:
    """Manager bazy danych SQLite"""
    
    def __init__(self, db_path: str = "fizjo_expert.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Inicjalizuje bazę danych"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela pacjentów
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    pesel TEXT UNIQUE NOT NULL,
                    birth_date DATE NOT NULL,
                    gender TEXT CHECK(gender IN ('M', 'K', 'Inna')),
                    phone TEXT,
                    email TEXT,
                    emergency_contact TEXT,
                    allergies TEXT,
                    medications TEXT,
                    medical_history TEXT,
                    notes TEXT,
                    consent_treatment BOOLEAN NOT NULL,
                    consent_data BOOLEAN NOT NULL,
                    consent_marketing BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela sesji diagnostycznych
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diagnosis_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    module_type TEXT NOT NULL,
                    session_date TIMESTAMP NOT NULL,
                    therapist_name TEXT NOT NULL,
                    primary_diagnosis TEXT,
                    confidence_level REAL,
                    treatment_plan TEXT,
                    referral_notes TEXT,
                    session_notes TEXT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            """)
            
            # Tabela wyników testów
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    test_name TEXT NOT NULL,
                    test_result TEXT NOT NULL,
                    test_score REAL,
                    test_notes TEXT,
                    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES diagnosis_sessions (id)
                )
            """)
            
            # Tabela ustawień użytkownika
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela logów systemu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module_name TEXT,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indeksy dla optymalizacji
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_pesel ON patients(pesel)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_patient ON diagnosis_sessions(patient_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON diagnosis_sessions(session_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tests_session ON test_results(session_id)")
            
            conn.commit()
    
    # === OPERACJE NA PACJENTACH ===
    
    def add_patient(self, patient: Patient) -> int:
        """Dodaje nowego pacjenta"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO patients (
                    first_name, last_name, pesel, birth_date, gender,
                    phone, email, emergency_contact, allergies, medications,
                    medical_history, notes, consent_treatment, consent_data, consent_marketing
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient.first_name, patient.last_name, patient.pesel, patient.birth_date,
                patient.gender, patient.phone, patient.email, patient.emergency_contact,
                patient.allergies, patient.medications, patient.medical_history, patient.notes,
                patient.consent_treatment, patient.consent_data, patient.consent_marketing
            ))
            
            patient_id = cursor.lastrowid
            conn.commit()
            
            self.log_action("INFO", f"Dodano nowego pacjenta: {patient.first_name} {patient.last_name}", "patient_management")
            
            return patient_id
    
    def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Pobiera pacjenta po ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            
            if row:
                return Patient.from_dict(dict(row))
            return None
    
    def search_patients(self, search_term: str) -> List[Patient]:
        """Wyszukuje pacjentów"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT * FROM patients 
                WHERE first_name LIKE ? OR last_name LIKE ? OR pesel LIKE ?
                ORDER BY last_name, first_name
            """, (search_pattern, search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [Patient.from_dict(dict(row)) for row in rows]
    
    def get_all_patients(self, active_only: bool = True) -> List[Patient]:
        """Pobiera wszystkich pacjentów"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute("SELECT * FROM patients WHERE is_active = 1 ORDER BY last_name, first_name")
            else:
                cursor.execute("SELECT * FROM patients ORDER BY last_name, first_name")
            
            rows = cursor.fetchall()
            return [Patient.from_dict(dict(row)) for row in rows]
    
    def patient_exists(self, pesel: str) -> bool:
        """Sprawdza czy pacjent istnieje"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM patients WHERE pesel = ?", (pesel,))
            return cursor.fetchone() is not None
    
    def update_patient(self, patient: Patient):
        """Aktualizuje dane pacjenta"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE patients SET
                    first_name = ?, last_name = ?, phone = ?, email = ?,
                    emergency_contact = ?, allergies = ?, medications = ?,
                    medical_history = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                patient.first_name, patient.last_name, patient.phone, patient.email,
                patient.emergency_contact, patient.allergies, patient.medications,
                patient.medical_history, patient.notes, patient.id
            ))
            
            conn.commit()
            self.log_action("INFO", f"Zaktualizowano dane pacjenta ID: {patient.id}", "patient_management")
    
    # === OPERACJE NA SESJACH DIAGNOSTYCZNYCH ===
    
    def add_diagnosis_session(self, session: DiagnosisSession) -> int:
        """Dodaje nową sesję diagnostyczną"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO diagnosis_sessions (
                    patient_id, module_type, session_date, therapist_name
                ) VALUES (?, ?, ?, ?)
            """, (session.patient_id, session.module_type, session.session_date, session.therapist_name))
            
            session_id = cursor.lastrowid
            conn.commit()
            
            return session_id
    
    def update_diagnosis_session(self, session: DiagnosisSession):
        """Aktualizuje sesję diagnostyczną"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE diagnosis_sessions SET
                    primary_diagnosis = ?, confidence_level = ?, treatment_plan = ?,
                    referral_notes = ?, session_notes = ?, is_completed = ?
                WHERE id = ?
            """, (
                session.primary_diagnosis, session.confidence_level, session.treatment_plan,
                session.referral_notes, session.session_notes, session.is_completed, session.id
            ))
            
            conn.commit()
    
    def get_patient_history(self, patient_id: int) -> List[DiagnosisSession]:
        """Pobiera historię sesji pacjenta"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM diagnosis_sessions 
                WHERE patient_id = ? 
                ORDER BY session_date DESC
            """, (patient_id,))
            
            rows = cursor.fetchall()
            return [DiagnosisSession.from_dict(dict(row)) for row in rows]
    
    def get_last_session(self, patient_id: int) -> Optional[DiagnosisSession]:
        """Pobiera ostatnią sesję pacjenta"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM diagnosis_sessions 
                WHERE patient_id = ? 
                ORDER BY session_date DESC 
                LIMIT 1
            """, (patient_id,))
            
            row = cursor.fetchone()
            if row:
                return DiagnosisSession.from_dict(dict(row))
            return None
    
    # === OPERACJE NA WYNIKACH TESTÓW ===
    
    def add_test_result(self, test_result: TestResult) -> int:
        """Dodaje wynik testu"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO test_results (
                    session_id, test_name, test_result, test_score, test_notes
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                test_result.session_id, test_result.test_name, test_result.test_result,
                test_result.test_score, test_result.test_notes
            ))
            
            test_id = cursor.lastrowid
            conn.commit()
            
            return test_id
    
    def get_session_test_results(self, session_id: int) -> List[TestResult]:
        """Pobiera wyniki testów dla sesji"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM test_results 
                WHERE session_id = ? 
                ORDER BY performed_at
            """, (session_id,))
            
            rows = cursor.fetchall()
            return [TestResult.from_dict(dict(row)) for row in rows]
    
    # === STATYSTYKI I ANALITYKA ===
    
    def get_patient_stats(self, patient_id: int) -> Dict[str, Any]:
        """Pobiera statystyki pacjenta"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Liczba wizyt
            cursor.execute("SELECT COUNT(*) FROM diagnosis_sessions WHERE patient_id = ?", (patient_id,))
            total_visits = cursor.fetchone()[0]
            
            # Liczba diagnoz
            cursor.execute("SELECT COUNT(*) FROM diagnosis_sessions WHERE patient_id = ? AND is_completed = 1", (patient_id,))
            total_diagnoses = cursor.fetchone()[0]
            
            # Ostatnia wizyta
            cursor.execute("SELECT MAX(session_date) FROM diagnosis_sessions WHERE patient_id = ?", (patient_id,))
            last_visit_result = cursor.fetchone()[0]
            last_visit = "Brak" if not last_visit_result else datetime.fromisoformat(last_visit_result).strftime("%d.%m.%Y")
            
            # Średnia skuteczność (przykładowa metryka)
            cursor.execute("SELECT AVG(confidence_level) FROM diagnosis_sessions WHERE patient_id = ? AND confidence_level IS NOT NULL", (patient_id,))
            avg_confidence = cursor.fetchone()[0]
            success_rate = int(avg_confidence) if avg_confidence else 0
            
            return {
                'total_visits': total_visits,
                'total_diagnoses': total_diagnoses,
                'last_visit': last_visit,
                'success_rate': success_rate
            }
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Pobiera dane analityczne"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Podstawowe statystyki
            cursor.execute("SELECT COUNT(*) FROM patients WHERE is_active = 1")
            total_patients = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM diagnosis_sessions WHERE session_date >= date('now', '-30 days')")
            diagnoses_this_month = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(confidence_level) FROM diagnosis_sessions WHERE confidence_level IS NOT NULL")
            avg_confidence_result = cursor.fetchone()[0]
            avg_confidence = avg_confidence_result if avg_confidence_result else 0
            
            cursor.execute("""
                SELECT module_type, COUNT(*) as count 
                FROM diagnosis_sessions 
                GROUP BY module_type 
                ORDER BY count DESC 
                LIMIT 1
            """)
            most_used_result = cursor.fetchone()
            most_used_module = most_used_result[0] if most_used_result else "Brak"
            
            # Diagnozy w czasie (ostatnie 30 dni)
            cursor.execute("""
                SELECT DATE(session_date) as data, COUNT(*) as liczba_diagnoz
                FROM diagnosis_sessions 
                WHERE session_date >= date('now', '-30 days')
                GROUP BY DATE(session_date)
                ORDER BY data
            """)
            diagnoses_over_time = [{'data': row[0], 'liczba_diagnoz': row[1]} for row in cursor.fetchall()]
            
            # Użycie modułów
            cursor.execute("""
                SELECT module_type as modul, COUNT(*) as liczba
                FROM diagnosis_sessions 
                GROUP BY module_type
            """)
            module_usage = [{'modul': row[0], 'liczba': row[1]} for row in cursor.fetchall()]
            
            # Najczęstsze diagnozy
            cursor.execute("""
                SELECT primary_diagnosis, COUNT(*) as liczba
                FROM diagnosis_sessions 
                WHERE primary_diagnosis IS NOT NULL
                GROUP BY primary_diagnosis
                ORDER BY liczba DESC
                LIMIT 10
            """)
            top_diagnoses = [{'diagnoza': row[0], 'liczba': row[1]} for row in cursor.fetchall()]
            
            # Rozkład pewności
            cursor.execute("SELECT confidence_level FROM diagnosis_sessions WHERE confidence_level IS NOT NULL")
            confidence_distribution = [{'confidence_level': row[0]} for row in cursor.fetchall()]
            
            # Efektywność terapeutów
            cursor.execute("""
                SELECT therapist_name as terapeuta, AVG(confidence_level) as srednia_pewnosc
                FROM diagnosis_sessions 
                WHERE confidence_level IS NOT NULL
                GROUP BY therapist_name
                HAVING COUNT(*) >= 5
            """)
            therapist_effectiveness = [{'terapeuta': row[0], 'srednia_pewnosc': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_patients': total_patients,
                'diagnoses_this_month': diagnoses_this_month,
                'avg_confidence': avg_confidence,
                'most_used_module': most_used_module,
                'diagnoses_over_time': diagnoses_over_time,
                'module_usage': module_usage,
                'top_diagnoses': top_diagnoses,
                'confidence_distribution': confidence_distribution,
                'therapist_effectiveness': therapist_effectiveness
            }
    
    # === SYSTEM LOGÓW ===
    
    def log_action(self, level: str, message: str, module_name: str = None, user_id: str = None):
        """Loguje akcję w systemie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_logs (log_level, message, module_name, user_id)
                VALUES (?, ?, ?, ?)
            """, (level, message, module_name, user_id))
            
            conn.commit()
    
    def get_logs(self, limit: int = 100, level: str = None) -> List[Dict]:
        """Pobiera logi systemu"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if level:
                cursor.execute("""
                    SELECT * FROM system_logs 
                    WHERE log_level = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (level, limit))
            else:
                cursor.execute("""
                    SELECT * FROM system_logs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # === USTAWIENIA ===
    
    def get_setting(self, key: str, default_value: str = None) -> str:
        """Pobiera ustawienie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT setting_value FROM user_settings WHERE setting_key = ?", (key,))
            result = cursor.fetchone()
            
            return result[0] if result else default_value
    
    def set_setting(self, key: str, value: str):
        """Ustawia wartość ustawienia"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            
            conn.commit()
