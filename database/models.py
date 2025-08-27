from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List, Any
import json

@dataclass
class Patient:
    """Model pacjenta"""
    first_name: str
    last_name: str
    pesel: str
    birth_date: date
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None
    consent_treatment: bool = False
    consent_data: bool = False
    consent_marketing: bool = False
    is_active: bool = True
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """Tworzy obiekt Patient z słownika"""
        # Konwertuj stringi dat na obiekty date/datetime
        if isinstance(data.get('birth_date'), str):
            data['birth_date'] = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje obiekt do słownika"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    def get_full_name(self) -> str:
        """Zwraca pełne imię i nazwisko"""
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self) -> int:
        """Oblicza wiek pacjenta"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def has_allergies(self) -> bool:
        """Sprawdza czy pacjent ma alergie"""
        return bool(self.allergies and self.allergies.strip() and self.allergies.lower() != 'brak')
    
    def has_medications(self) -> bool:
        """Sprawdza czy pacjent przyjmuje leki"""
        return bool(self.medications and self.medications.strip() and self.medications.lower() != 'brak')

@dataclass
class DiagnosisSession:
    """Model sesji diagnostycznej"""
    patient_id: int
    module_type: str
    session_date: datetime
    therapist_name: str
    primary_diagnosis: Optional[str] = None
    confidence_level: Optional[float] = None
    treatment_plan: Optional[str] = None
    referral_notes: Optional[str] = None
    session_notes: Optional[str] = None
    is_completed: bool = False
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosisSession':
        """Tworzy obiekt DiagnosisSession z słownika"""
        # Konwertuj stringi dat na obiekty datetime
        if isinstance(data.get('session_date'), str):
            data['session_date'] = datetime.fromisoformat(data['session_date'])
        
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje obiekt do słownika"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    def get_session_notes_dict(self) -> Dict[str, Any]:
        """Parsuje session_notes z JSON"""
        if self.session_notes:
            try:
                return json.loads(self.session_notes)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_session_notes_dict(self, notes_dict: Dict[str, Any]):
        """Ustawia session_notes jako JSON"""
        self.session_notes = json.dumps(notes_dict, ensure_ascii=False, indent=2)
    
    def get_duration_minutes(self) -> int:
        """Oblicza czas trwania sesji w minutach (przykładowa logika)"""
        if self.created_at and self.session_date:
            delta = self.created_at - self.session_date
            return max(1, int(delta.total_seconds() / 60))
        return 30  # domyślnie 30 minut

@dataclass
class TestResult:
    """Model wyniku testu diagnostycznego"""
    session_id: int
    test_name: str
    test_result: str
    test_score: Optional[float] = None
    test_notes: Optional[str] = None
    performed_at: Optional[datetime] = None
    id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Tworzy obiekt TestResult z słownika"""
        if isinstance(data.get('performed_at'), str):
            data['performed_at'] = datetime.fromisoformat(data['performed_at'])
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje obiekt do słownika"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    def is_positive(self) -> bool:
        """Sprawdza czy test jest pozytywny"""
        positive_indicators = ['positive', 'pozytywny', 'dodatni', 'tak', 'yes', '1', 'true']
        return self.test_result.lower() in positive_indicators

@dataclass
class DiagnosticTest:
    """Model testu diagnostycznego"""
    name: str
    description: str
    procedure: str
    interpretation: Dict[str, str]
    sensitivity: float
    specificity: float
    module_type: str
    test_category: str = "physical"  # physical, imaging, laboratory
    video_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    equipment_needed: List[str] = field(default_factory=list)
    
    def get_positive_predictive_value(self, prevalence: float) -> float:
        """Oblicza dodatnią wartość predykcyjną"""
        if prevalence <= 0 or prevalence >= 1:
            raise ValueError("Prevalence must be between 0 and 1")
        
        ppv = (self.sensitivity * prevalence) / (
            self.sensitivity * prevalence + (1 - self.specificity) * (1 - prevalence)
        )
        return ppv
    
    def get_negative_predictive_value(self, prevalence: float) -> float:
        """Oblicza ujemną wartość predykcyjną"""
        if prevalence <= 0 or prevalence >= 1:
            raise ValueError("Prevalence must be between 0 and 1")
        
        npv = (self.specificity * (1 - prevalence)) / (
            self.specificity * (1 - prevalence) + (1 - self.sensitivity) * prevalence
        )
        return npv

@dataclass
class Diagnosis:
    """Model diagnozy"""
    name: str
    icd10_code: Optional[str] = None
    confidence: float = 0.0
    evidence_level: str = "low"  # low, moderate, high
    differential_diagnoses: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    treatment_options: List[str] = field(default_factory=list)
    referral_recommendations: List[str] = field(default_factory=list)
    prognosis: Optional[str] = None
    
    def get_confidence_level(self) -> str:
        """Zwraca poziom pewności jako tekst"""
        if self.confidence >= 90:
            return "Bardzo wysoka"
        elif self.confidence >= 70:
            return "Wysoka"
        elif self.confidence >= 50:
            return "Umiarkowana"
        else:
            return "Niska"
    
    def requires_urgent_referral(self) -> bool:
        """Sprawdza czy wymagane jest pilne skierowanie"""
        urgent_keywords = ['pilne', 'natychmiast', 'sor', 'emergency', 'urgent']
        return any(keyword in ref.lower() for ref in self.referral_recommendations for keyword in urgent_keywords)

@dataclass
class TreatmentProtocol:
    """Model protokołu leczenia"""
    name: str
    diagnosis_codes: List[str]
    phases: List[Dict[str, Any]]
    contraindications: List[str] = field(default_factory=list)
    expected_duration_weeks: Optional[int] = None
    success_criteria: List[str] = field(default_factory=list)
    
    def get_phase(self, phase_number: int) -> Optional[Dict[str, Any]]:
        """Pobiera konkretną fazę leczenia"""
        if 0 <= phase_number < len(self.phases):
            return self.phases[phase_number]
        return None
    
    def get_current_phase(self, weeks_since_start: int) -> Optional[Dict[str, Any]]:
        """Pobiera aktualną fazę na podstawie czasu leczenia"""
        cumulative_weeks = 0
        for phase in self.phases:
            phase_duration = phase.get('duration_weeks', 2)
            cumulative_weeks += phase_duration
            if weeks_since_start <= cumulative_weeks:
                return phase
        return self.phases[-1] if self.phases else None

@dataclass
class ClinicalRule:
    """Model reguły klinicznej (np. Ottawa Rules)"""
    name: str
    description: str
    criteria: List[Dict[str, Any]]
    outcome_positive: str
    outcome_negative: str
    sensitivity: float
    specificity: float
    validation_studies: List[str] = field(default_factory=list)
    
    def evaluate(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ewaluuje regułę dla danych pacjenta"""
        positive_criteria = 0
        total_criteria = len(self.criteria)
        met_criteria = []
        
        for criterion in self.criteria:
            criterion_met = self._evaluate_criterion(criterion, patient_data)
            if criterion_met:
                positive_criteria += 1
                met_criteria.append(criterion['description'])
        
        # Logika może być różna dla różnych reguł
        # Dla Ottawa Rules - wystarczy 1 kryterium
        if self.name.lower().startswith('ottawa'):
            is_positive = positive_criteria > 0
        else:
            # Dla innych reguł może być wymagana większość kryteriów
            is_positive = positive_criteria >= (total_criteria / 2)
        
        return {
            'is_positive': is_positive,
            'score': positive_criteria,
            'max_score': total_criteria,
            'percentage': (positive_criteria / total_criteria) * 100,
            'met_criteria': met_criteria,
            'recommendation': self.outcome_positive if is_positive else self.outcome_negative
        }
    
    def _evaluate_criterion(self, criterion: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Ewaluuje pojedyncze kryterium"""
        field_name = criterion.get('field')
        expected_value = criterion.get('value')
        comparison = criterion.get('comparison', 'equals')
        
        if field_name not in patient_data:
            return False
        
        actual_value = patient_data[field_name]
        
        if comparison == 'equals':
            return actual_value == expected_value
        elif comparison == 'greater_than':
            return actual_value > expected_value
        elif comparison == 'less_than':
            return actual_value < expected_value
        elif comparison == 'contains':
            return expected_value in str(actual_value).lower()
        elif comparison == 'boolean_true':
            return bool(actual_value)
        
        return False

@dataclass
class AnatomicalRegion:
    """Model regionu anatomicznego"""
    name: str
    anatomical_system: str  # musculoskeletal, neurological, cardiovascular
    coordinates_3d: Dict[str, float]  # x, y, z dla modelu 3D
    related_structures: List[str] = field(default_factory=list)
    common_conditions: List[str] = field(default_factory=list)
    examination_tests: List[str] = field(default_factory=list)
    
    def get_distance_to(self, other_region: 'AnatomicalRegion') -> float:
        """Oblicza odległość 3D do innego regionu"""
        x_diff = self.coordinates_3d['x'] - other_region.coordinates_3d['x']
        y_diff = self.coordinates_3d['y'] - other_region.coordinates_3d['y']
        z_diff = self.coordinates_3d['z'] - other_region.coordinates_3d['z']
        
        return (x_diff**2 + y_diff**2 + z_diff**2)**0.5

@dataclass
class UserSession:
    """Model sesji użytkownika"""
    user_id: str
    session_token: str
    login_time: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    
    def is_expired(self, timeout_hours: int = 8) -> bool:
        """Sprawdza czy sesja wygasła"""
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > (timeout_hours * 3600)
    
    def update_activity(self):
        """Aktualizuje czas ostatniej aktywności"""
        self.last_activity = datetime.now()

@dataclass
class SystemConfiguration:
    """Model konfiguracji systemu"""
    ai_model_version: str = "1.0"
    confidence_threshold: float = 0.7
    max_differential_diagnoses: int = 5
    session_timeout_hours: int = 8
    enable_ai_suggestions: bool = True
    enable_3d_model: bool = True
    default_language: str = "pl"
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do słownika"""
        return {
            'ai_model_version': self.ai_model_version,
            'confidence_threshold': self.confidence_threshold,
            'max_differential_diagnoses': self.max_differential_diagnoses,
            'session_timeout_hours': self.session_timeout_hours,
            'enable_ai_suggestions': self.enable_ai_suggestions,
            'enable_3d_model': self.enable_3d_model,
            'default_language': self.default_language,
            'log_level': self.log_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemConfiguration':
        """Tworzy konfigurację ze słownika"""
        return cls(**data)
