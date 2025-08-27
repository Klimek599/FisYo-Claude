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
        }
    ]
}
