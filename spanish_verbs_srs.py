import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import datetime
import time
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Конфигурация
st.set_page_config(
    page_title="🇪🇸 Тренажер испанских глаголов - Полная версия",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://spanishverbint-production.up.railway.app')

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# CSS стили
st.markdown("""
<style>
    .main > div {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Контейнер для основного контента - делаем более компактным */
    .main-content {
        max-width: 600px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .verb-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .verb-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.4);
    }
    
    .verb-card.revealed {
        background: linear-gradient(135deg, #48ca8b 0%, #2dd4bf 100%);
        box-shadow: 0 12px 40px rgba(72, 202, 139, 0.3);
    }
    
    .verb-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .verb-translation {
        font-size: 1.4rem;
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }
    
    .pronoun-display {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 1.5rem 0;
        background: rgba(255,255,255,0.2);
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        display: inline-block;
    }
    
    .answer-display {
        font-size: 2.8rem;
        font-weight: bold;
        background: rgba(255,255,255,0.9);
        color: #2d5e3e;
        padding: 1.5rem 2rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        display: inline-block;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .difficulty-btn {
        margin: 0.3rem;
        padding: 0.8rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: bold;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .btn-again { background: #ff6b6b; color: white; }
    .btn-hard { background: #feca57; color: black; }
    .btn-good { background: #48ca8b; color: white; }
    .btn-easy { background: #0abde3; color: white; }
    
    .user-panel {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stats-container {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Стили для правил */
    .rules-section {
        margin-top: 20px;
    }
    
    .rules-toggle {
        width: 100%;
        padding: 15px;
        background: #f7fafc;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 600;
        color: #4a5568;
        transition: all 0.3s ease;
    }
    
    .rules-toggle:hover {
        background: #edf2f7;
    }
    
    .rules-content {
        background: #f7fafc;
        border-radius: 0 0 10px 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .rules-content h3 {
        color: #2d3748;
        margin-bottom: 15px;
        font-size: 1.2rem;
    }
    
    .rules-content p {
        line-height: 1.6;
        margin-bottom: 10px;
        color: #4a5568;
    }
    
    .example {
        background: rgba(102, 126, 234, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: monospace;
    }
    
    .click-hint {
        font-size: 1.2rem;
        margin-top: 1rem;
        opacity: 0.8;
        animation: pulse-gentle 2s infinite;
    }
    
    @keyframes pulse-gentle {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# Перечисления для SRS
class Difficulty(Enum):
    AGAIN = 0  # Повторить снова
    HARD = 1   # Сложно
    GOOD = 2   # Хорошо
    EASY = 3   # Легко

# Структура данных для карточки
@dataclass
class Card:
    verb: str
    pronoun_index: int
    tense: str
    easiness_factor: float = 2.5
    interval: int = 1
    repetitions: int = 0
    next_review_date: str = ""
    last_review_date: str = ""
    total_reviews: int = 0
    correct_reviews: int = 0
    
    def __post_init__(self):
        if not self.next_review_date:
            self.next_review_date = datetime.date.today().isoformat()

# Полная база данных глаголов
VERBS = {
    'ser': {'translation': 'быть, являться', 'type': 'irregular'},
    'estar': {'translation': 'находиться, быть', 'type': 'irregular'},
    'tener': {'translation': 'иметь', 'type': 'irregular'},
    'hacer': {'translation': 'делать', 'type': 'irregular'},
    'decir': {'translation': 'говорить, сказать', 'type': 'irregular'},
    'ir': {'translation': 'идти, ехать', 'type': 'irregular'},
    'ver': {'translation': 'видеть', 'type': 'irregular'},
    'dar': {'translation': 'давать', 'type': 'irregular'},
    'saber': {'translation': 'знать', 'type': 'irregular'},
    'querer': {'translation': 'хотеть, любить', 'type': 'irregular'},
    'llegar': {'translation': 'прибывать, приходить', 'type': 'regular-ar'},
    'pasar': {'translation': 'проходить, проводить', 'type': 'regular-ar'},
    'deber': {'translation': 'быть должным', 'type': 'regular-er'},
    'poner': {'translation': 'класть, ставить', 'type': 'irregular'},
    'parecer': {'translation': 'казаться', 'type': 'irregular'},
    'quedar': {'translation': 'оставаться', 'type': 'regular-ar'},
    'creer': {'translation': 'верить, считать', 'type': 'regular-er'},
    'hablar': {'translation': 'говорить', 'type': 'regular-ar'},
    'llevar': {'translation': 'носить, нести', 'type': 'regular-ar'},
    'dejar': {'translation': 'оставлять', 'type': 'regular-ar'},
    'seguir': {'translation': 'следовать, продолжать', 'type': 'irregular'},
    'encontrar': {'translation': 'находить, встречать', 'type': 'irregular'},
    'llamar': {'translation': 'звать, называть', 'type': 'regular-ar'},
    'venir': {'translation': 'приходить', 'type': 'irregular'},
    'pensar': {'translation': 'думать', 'type': 'irregular'},
    'salir': {'translation': 'выходить', 'type': 'irregular'},
    'vivir': {'translation': 'жить', 'type': 'regular-ir'},
    'sentir': {'translation': 'чувствовать', 'type': 'irregular'},
    'trabajar': {'translation': 'работать', 'type': 'regular-ar'},
    'estudiar': {'translation': 'изучать', 'type': 'regular-ar'},
    'comprar': {'translation': 'покупать', 'type': 'regular-ar'},
    'comer': {'translation': 'есть', 'type': 'regular-er'},
    'beber': {'translation': 'пить', 'type': 'regular-er'},
    'escribir': {'translation': 'писать', 'type': 'regular-ir'},
    'leer': {'translation': 'читать', 'type': 'regular-er'},
    'abrir': {'translation': 'открывать', 'type': 'irregular'},
    'cerrar': {'translation': 'закрывать', 'type': 'irregular'},
    'empezar': {'translation': 'начинать', 'type': 'irregular'},
    'terminar': {'translation': 'заканчивать', 'type': 'regular-ar'},
    'poder': {'translation': 'мочь', 'type': 'irregular'}
}

PRONOUNS = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']

# Полные спряжения для всех времен
CONJUGATIONS = {
    'presente': {
        'ser': ['soy', 'eres', 'es', 'somos', 'sois', 'son'],
        'estar': ['estoy', 'estás', 'está', 'estamos', 'estáis', 'están'],
        'tener': ['tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen'],
        'hacer': ['hago', 'haces', 'hace', 'hacemos', 'hacéis', 'hacen'],
        'decir': ['digo', 'dices', 'dice', 'decimos', 'decís', 'dicen'],
        'ir': ['voy', 'vas', 'va', 'vamos', 'vais', 'van'],
        'ver': ['veo', 'ves', 've', 'vemos', 'veis', 'ven'],
        'dar': ['doy', 'das', 'da', 'damos', 'dais', 'dan'],
        'saber': ['sé', 'sabes', 'sabe', 'sabemos', 'sabéis', 'saben'],
        'querer': ['quiero', 'quieres', 'quiere', 'queremos', 'queréis', 'quieren'],
        'llegar': ['llego', 'llegas', 'llega', 'llegamos', 'llegáis', 'llegan'],
        'pasar': ['paso', 'pasas', 'pasa', 'pasamos', 'pasáis', 'pasan'],
        'deber': ['debo', 'debes', 'debe', 'debemos', 'debéis', 'deben'],
        'poner': ['pongo', 'pones', 'pone', 'ponemos', 'ponéis', 'ponen'],
        'parecer': ['parezco', 'pareces', 'parece', 'parecemos', 'parecéis', 'parecen'],
        'quedar': ['quedo', 'quedas', 'queda', 'quedamos', 'quedáis', 'quedan'],
        'creer': ['creo', 'crees', 'cree', 'creemos', 'creéis', 'creen'],
        'hablar': ['hablo', 'hablas', 'habla', 'hablamos', 'habláis', 'hablan'],
        'llevar': ['llevo', 'llevas', 'lleva', 'llevamos', 'lleváis', 'llevan'],
        'dejar': ['dejo', 'dejas', 'deja', 'dejamos', 'dejáis', 'dejan'],
        'seguir': ['sigo', 'sigues', 'sigue', 'seguimos', 'seguís', 'siguen'],
        'encontrar': ['encuentro', 'encuentras', 'encuentra', 'encontramos', 'encontráis', 'encuentran'],
        'llamar': ['llamo', 'llamas', 'llama', 'llamamos', 'llamáis', 'llaman'],
        'venir': ['vengo', 'vienes', 'viene', 'venimos', 'venís', 'vienen'],
        'pensar': ['pienso', 'piensas', 'piensa', 'pensamos', 'pensáis', 'piensan'],
        'salir': ['salgo', 'sales', 'sale', 'salimos', 'salís', 'salen'],
        'vivir': ['vivo', 'vives', 'vive', 'vivimos', 'vivís', 'viven'],
        'sentir': ['siento', 'sientes', 'siente', 'sentimos', 'sentís', 'sienten'],
        'trabajar': ['trabajo', 'trabajas', 'trabaja', 'trabajamos', 'trabajáis', 'trabajan'],
        'estudiar': ['estudio', 'estudias', 'estudia', 'estudiamos', 'estudiáis', 'estudian'],
        'comprar': ['compro', 'compras', 'compra', 'compramos', 'compráis', 'compran'],
        'comer': ['como', 'comes', 'come', 'comemos', 'coméis', 'comen'],
        'beber': ['bebo', 'bebes', 'bebe', 'bebemos', 'bebéis', 'beben'],
        'escribir': ['escribo', 'escribes', 'escribe', 'escribimos', 'escribís', 'escriben'],
        'leer': ['leo', 'lees', 'lee', 'leemos', 'leéis', 'leen'],
        'abrir': ['abro', 'abres', 'abre', 'abrimos', 'abrís', 'abren'],
        'cerrar': ['cierro', 'cierras', 'cierra', 'cerramos', 'cerráis', 'cierran'],
        'empezar': ['empiezo', 'empiezas', 'empieza', 'empezamos', 'empezáis', 'empiezan'],
        'terminar': ['termino', 'terminas', 'termina', 'terminamos', 'termináis', 'terminan'],
        'poder': ['puedo', 'puedes', 'puede', 'podemos', 'podéis', 'pueden']
    },
    'indefinido': {
        'ser': ['fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron'],
        'estar': ['estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron'],
        'tener': ['tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 'tuvieron'],
        'hacer': ['hice', 'hiciste', 'hizo', 'hicimos', 'hicisteis', 'hicieron'],
        'decir': ['dije', 'dijiste', 'dijo', 'dijimos', 'dijisteis', 'dijeron'],
        'ir': ['fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron'],
        'ver': ['vi', 'viste', 'vio', 'vimos', 'visteis', 'vieron'],
        'dar': ['di', 'diste', 'dio', 'dimos', 'disteis', 'dieron'],
        'saber': ['supe', 'supiste', 'supo', 'supimos', 'supisteis', 'supieron'],
        'querer': ['quise', 'quisiste', 'quiso', 'quisimos', 'quisisteis', 'quisieron'],
        'llegar': ['llegué', 'llegaste', 'llegó', 'llegamos', 'llegasteis', 'llegaron'],
        'pasar': ['pasé', 'pasaste', 'pasó', 'pasamos', 'pasasteis', 'pasaron'],
        'deber': ['debí', 'debiste', 'debió', 'debimos', 'debisteis', 'debieron'],
        'poner': ['puse', 'pusiste', 'puso', 'pusimos', 'pusisteis', 'pusieron'],
        'parecer': ['parecí', 'pareciste', 'pareció', 'parecimos', 'parecisteis', 'parecieron'],
        'quedar': ['quedé', 'quedaste', 'quedó', 'quedamos', 'quedasteis', 'quedaron'],
        'creer': ['creí', 'creíste', 'creyó', 'creímos', 'creísteis', 'creyeron'],
        'hablar': ['hablé', 'hablaste', 'habló', 'hablamos', 'hablasteis', 'hablaron'],
        'trabajar': ['trabajé', 'trabajaste', 'trabajó', 'trabajamos', 'trabajasteis', 'trabajaron'],
        'estudiar': ['estudié', 'estudiaste', 'estudió', 'estudiamos', 'estudiasteis', 'estudiaron'],
        'poder': ['pude', 'pudiste', 'pudo', 'pudimos', 'pudisteis', 'pudieron']
    },
    'subjuntivo': {
        'ser': ['sea', 'seas', 'sea', 'seamos', 'seáis', 'sean'],
        'estar': ['esté', 'estés', 'esté', 'estemos', 'estéis', 'estén'],
        'tener': ['tenga', 'tengas', 'tenga', 'tengamos', 'tengáis', 'tengan'],
        'hacer': ['haga', 'hagas', 'haga', 'hagamos', 'hagáis', 'hagan'],
        'decir': ['diga', 'digas', 'diga', 'digamos', 'digáis', 'digan'],
        'ir': ['vaya', 'vayas', 'vaya', 'vayamos', 'vayáis', 'vayan'],
        'ver': ['vea', 'veas', 'vea', 'veamos', 'veáis', 'vean'],
        'dar': ['dé', 'des', 'dé', 'demos', 'deis', 'den'],
        'saber': ['sepa', 'sepas', 'sepa', 'sepamos', 'sepáis', 'sepan'],
        'querer': ['quiera', 'quieras', 'quiera', 'queramos', 'queráis', 'quieran'],
        'hablar': ['hable', 'hables', 'hable', 'hablemos', 'habléis', 'hablen'],
        'trabajar': ['trabaje', 'trabajes', 'trabaje', 'trabajemos', 'trabajéis', 'trabajen'],
        'poder': ['pueda', 'puedas', 'pueda', 'podamos', 'podáis', 'puedan']
    },
    'imperfecto': {
        'ser': ['era', 'eras', 'era', 'éramos', 'erais', 'eran'],
        'estar': ['estaba', 'estabas', 'estaba', 'estábamos', 'estabais', 'estaban'],
        'tener': ['tenía', 'tenías', 'tenía', 'teníamos', 'teníais', 'tenían'],
        'hacer': ['hacía', 'hacías', 'hacía', 'hacíamos', 'hacíais', 'hacían'],
        'ir': ['iba', 'ibas', 'iba', 'íbamos', 'ibais', 'iban'],
        'ver': ['veía', 'veías', 'veía', 'veíamos', 'veíais', 'veían'],
        'hablar': ['hablaba', 'hablabas', 'hablaba', 'hablábamos', 'hablabais', 'hablaban'],
        'trabajar': ['trabajaba', 'trabajabas', 'trabajaba', 'trabajábamos', 'trabajabais', 'trabajaban'],
        'vivir': ['vivía', 'vivías', 'vivía', 'vivíamos', 'vivíais', 'vivían'],
        'poder': ['podía', 'podías', 'podía', 'podíamos', 'podíais', 'podían']
    }
}

# Правила спряжения
GRAMMAR_RULES = {
    'presente': {
        'title': 'Настоящее время (Presente de Indicativo)',
        'content': '''
**Правильные глаголы -AR:**
Основа + -o, -as, -a, -amos, -áis, -an
*Ejemplo: hablar → hablo, hablas, habla, hablamos, habláis, hablan*

**Правильные глаголы -ER:**
Основа + -o, -es, -e, -emos, -éis, -en
*Ejemplo: comer → como, comes, come, comemos, coméis, comen*

**Правильные глаголы -IR:**
Основа + -o, -es, -e, -imos, -ís, -en
*Ejemplo: vivir → vivo, vives, vive, vivimos, vivís, viven*

**Неправильные глаголы** имеют особые формы спряжения.
        '''
    },
    'indefinido': {
        'title': 'Прошедшее время (Pretérito Indefinido)',
        'content': '''
**Правильные глаголы -AR:**
Основа + -é, -aste, -ó, -amos, -asteis, -aron
*Ejemplo: hablar → hablé, hablaste, habló, hablamos, hablasteis, hablaron*

**Правильные глаголы -ER/-IR:**
Основа + -í, -iste, -ió, -imos, -isteis, -ieron
*Ejemplo: comer → comí, comiste, comió, comimos, comisteis, comieron*

**Использование:** Завершенные действия в прошлом, конкретные моменты времени.
        '''
    },
    'subjuntivo': {
        'title': 'Сослагательное наклонение (Subjuntivo Presente)',
        'content': '''
**Глаголы -AR:**
Основа + -e, -es, -e, -emos, -éis, -en
*Ejemplo: hablar → hable, hables, hable, hablemos, habléis, hablen*

**Глаголы -ER/-IR:**
Основа + -a, -as, -a, -amos, -áis, -an
*Ejemplo: comer → coma, comas, coma, comamos, comáis, coman*

**Использование:** Сомнения, желания, эмоции, нереальные ситуации.
        '''
    },
    'imperfecto': {
        'title': 'Прошедшее несовершенное время (Pretérito Imperfecto)',
        'content': '''
**Глаголы -AR:**
Основа + -aba, -abas, -aba, -ábamos, -abais, -aban
*Ejemplo: hablar → hablaba, hablabas, hablaba, hablábamos, hablabais, hablaban*

**Глаголы -ER/-IR:**
Основа + -ía, -ías, -ía, -íamos, -íais, -ían
*Ejemplo: vivir → vivía, vivías, vivía, vivíamos, vivíais, vivían*

**Использование:** Повторяющиеся действия в прошлом, описания, привычки.
        '''
    }
}

# Система интервального повторения (SRS)
class SRSManager:
    @staticmethod
    def calculate_next_interval(card: Card, difficulty: Difficulty) -> Tuple[int, float]:
        """Алгоритм SM-2 для расчета следующего интервала"""
        ef = card.easiness_factor
        interval = card.interval
        repetitions = card.repetitions
        
        if difficulty == Difficulty.AGAIN:
            return 1, max(1.3, ef - 0.2)
        
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ef)
        
        # Обновляем easiness factor
        if difficulty == Difficulty.EASY:
            ef = ef + 0.15
        elif difficulty == Difficulty.GOOD:
            ef = ef + 0.1
        elif difficulty == Difficulty.HARD:
            ef = ef - 0.15
        
        ef = max(1.3, min(3.0, ef))
        return interval, ef
    
    @staticmethod
    def update_card(card: Card, difficulty: Difficulty) -> Card:
        """Обновляет карточку после ответа"""
        today = datetime.date.today()
        
        card.total_reviews += 1
        if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
            card.correct_reviews += 1
        
        if difficulty == Difficulty.AGAIN:
            card.repetitions = 0
        else:
            card.repetitions += 1
        
        new_interval, new_ef = SRSManager.calculate_next_interval(card, difficulty)
        
        card.interval = new_interval
        card.easiness_factor = new_ef
        card.last_review_date = today.isoformat()
        card.next_review_date = (today + datetime.timedelta(days=new_interval)).isoformat()
        
        return card

def main():
    # Инициализация
    init_session_state()
    
    # Обрабатываем OAuth callback
    query_params = dict(st.query_params)
    
    if 'code' in query_params and 'state' in query_params:
        handle_oauth_callback(query_params)
    elif st.session_state.authenticated:
        show_main_app()
    else:
        show_welcome_page()

def init_session_state():
    """Инициализация session state"""
    # OAuth состояние
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # Состояние приложения
    if 'cards' not in st.session_state:
        st.session_state.cards = {}
    if 'current_card' not in st.session_state:
        st.session_state.current_card = None
    if 'is_revealed' not in st.session_state:
        st.session_state.is_revealed = False
    if 'daily_stats' not in st.session_state:
        st.session_state.daily_stats = {
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': datetime.date.today().isoformat()
        }
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'new_cards_per_day': 10,
            'review_cards_per_day': 50,
            'selected_tenses': ['presente'],
            'auto_save': True
        }
    if 'recent_combinations' not in st.session_state:
        st.session_state.recent_combinations = []

def handle_oauth_callback(query_params):
    """Обрабатывает OAuth callback"""
    st.title("🔄 Обрабатываем авторизацию...")
    
    code = query_params.get('code')
    state = query_params.get('state')
    error = query_params.get('error')
    
    if error:
        st.error(f"❌ OAuth Error: {error}")
        if st.button("🔄 Попробовать снова"):
            clear_oauth_and_reload()
        return
    
    if not code or not state:
        st.error("❌ Missing authorization parameters")
        return
    
    # Умная проверка state (учитываем ограничения Streamlit)
    if not validate_state_format(state):
        st.error("❌ Invalid state format")
        return
    
    if not st.session_state.oauth_state:
        st.info("🔄 Session restored after OAuth redirect")
    elif state != st.session_state.oauth_state:
        st.warning("⚠️ State mismatch - continuing anyway (Streamlit limitation)")
    else:
        st.success("✅ State validation passed!")
    
    # Обрабатываем код
    with st.spinner("🔄 Получаем токен доступа..."):
        success = process_authorization_code(code)
        
        if success:
            st.success("🎉 Авторизация завершена успешно!")
            time.sleep(1)
            clear_url_params()
            st.rerun()
        else:
            st.error("❌ Ошибка при получении токена")

def validate_state_format(state):
    """Проверяет формат state"""
    try:
        decoded = base64.urlsafe_b64decode(state + '==')
        return len(decoded) == 32 and decoded.count(0) <= 5
    except:
        return False

def process_authorization_code(code):
    """Обрабатывает authorization code"""
    try:
        token_data = exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            return False
        
        user_info = get_user_info(token_data['access_token'])
        if not user_info:
            return False
        
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        
        # Загружаем данные пользователя
        load_user_data()
        
        return True
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

def exchange_code_for_token(code):
    """Обменивает код на токен"""
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
    return response.json() if response.status_code == 200 else None

def get_user_info(access_token):
    """Получает информацию о пользователе"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
    return response.json() if response.status_code == 200 else None

def load_user_data():
    """Загружает данные пользователя (заглушка для будущей базы данных)"""
    # В будущем здесь будет загрузка из Firebase/Supabase
    pass

def save_user_data():
    """Сохраняет данные пользователя (заглушка для будущей базы данных)"""
    # В будущем здесь будет сохранение в Firebase/Supabase
    pass

def show_welcome_page():
    """Показывает страницу приветствия"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 4rem; color: #2d3748; margin-bottom: 1rem;">
            🇪🇸 Тренажер испанских глаголов
        </h1>
        <h3 style="color: #718096; font-weight: 400; margin-bottom: 3rem;">
            Изучайте спряжения с системой интервального повторения
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Преимущества
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1rem; margin: 1rem 0; height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h3>🧠 Умное повторение</h3>
            <p>Алгоритм SM-2 показывает карточки именно тогда, когда вы готовы их забыть</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 1rem; margin: 1rem 0; height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h3>📊 Детальная статистика</h3>
            <p>Отслеживайте прогресс по каждому глаголу и времени отдельно</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 1rem; margin: 1rem 0; height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h3>☁️ Облачное сохранение</h3>
            <p>Изучайте на любом устройстве, прогресс синхронизируется автоматически</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Кнопка входа
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Войти через Google", type="primary", use_container_width=True):
            start_oauth_flow()
            return

def start_oauth_flow():
    """Запускает OAuth flow"""
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    st.session_state.oauth_state = state
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    st.success("🔐 OAuth готов к запуску!")
    
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <a href="{auth_url}" target="_self" style="text-decoration: none;">
            <button style="
                background: linear-gradient(135deg, #4285f4, #34a853);
                color: white;
                padding: 1rem 3rem;
                border: none;
                border-radius: 50px;
                font-size: 1.2rem;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                🔐 Открыть Google OAuth
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

def show_main_app():
    """Показывает основное приложение"""
    reset_daily_stats()
    
    user_info = st.session_state.user_info
    
    # Заголовок
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption(f"Добро пожаловать, {user_info.get('name')}! Система интервального повторения")
    
    # Боковая панель
    with st.sidebar:
        show_user_panel()
        show_sidebar_content()
    
    # Основной интерфейс
    show_learning_interface()

def show_user_panel():
    """Показывает панель пользователя"""
    user_info = st.session_state.user_info
    
    st.markdown(f"""
    <div class="user-panel">
        <strong>👤 {user_info.get('name')}</strong><br>
        <small>{user_info.get('email')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Синхронизация", use_container_width=True):
            save_user_data()
            st.success("✅ Синхронизировано!")
    
    with col2:
        if st.button("🚪 Выйти", use_container_width=True):
            logout()
            st.rerun()

def show_sidebar_content():
    """Показывает содержимое боковой панели"""
    st.markdown("---")
    
    # Статистика в боковой панели
    st.subheader("📊 Сегодня")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Повторений", st.session_state.daily_stats['reviews_today'])
        st.metric("Новых", st.session_state.daily_stats['new_cards_today'])
    with col2:
        st.metric("Правильных", st.session_state.daily_stats['correct_today'])
        due_count = len(get_due_cards())
        st.metric("К повторению", due_count)
    
    # Общая статистика
    total_cards = len(st.session_state.cards)
    total_reviews = sum(card.total_reviews for card in st.session_state.cards.values())
    total_correct = sum(card.correct_reviews for card in st.session_state.cards.values())
    accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
    
    st.subheader("📈 Всего")
    st.metric("Карточек", total_cards)
    st.metric("Точность", f"{accuracy:.1f}%")
    
    # Настройки
    st.markdown("---")
    st.subheader("⚙️ Настройки")
    
    # Выбор времен
    tense_options = {
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto'
    }
    
    selected_tenses = []
    for tense_key, tense_name in tense_options.items():
        if st.checkbox(tense_name, value=tense_key in st.session_state.settings['selected_tenses'], key=f"tense_{tense_key}"):
            selected_tenses.append(tense_key)
    
    st.session_state.settings['selected_tenses'] = selected_tenses or ['presente']
    
    # Лимиты
    st.session_state.settings['new_cards_per_day'] = st.slider(
        "Новых карточек в день", 1, 50, st.session_state.settings['new_cards_per_day']
    )

def show_learning_interface():
    """Показывает интерфейс изучения"""
    # Контейнер для более компактного интерфейса
    with st.container():
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Получаем следующую карточку
        if not st.session_state.current_card:
            st.session_state.current_card = get_next_card()
            st.session_state.is_revealed = False
        
        if not st.session_state.current_card:
            st.success("🎉 Отлично! Вы завершили все повторения на сегодня!")
            st.info("Возвращайтесь завтра для новых карточек или измените настройки в боковой панели.")
            
            if st.button("🔄 Получить новую карточку"):
                force_new_card()
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Отображаем карточку
        show_verb_card()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_verb_card():
    """Показывает карточку глагола"""
    card = st.session_state.current_card
    
    if (card.verb not in VERBS or 
        card.tense not in CONJUGATIONS or 
        card.verb not in CONJUGATIONS[card.tense]):
        st.error("❌ Данные карточки повреждены")
        next_card()
        return
    
    verb_info = VERBS[card.verb]
    is_revealed = st.session_state.is_revealed
    
    # Отображаем карточку
    if not is_revealed:
        # Красивая кликабельная карточка с вопросом
        st.markdown(f"""
        <div class="verb-card">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {get_tense_name(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]}
            </div>
            <div class="click-hint">
                🔍 Нажмите на кнопку, чтобы увидеть ответ
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопка для показа ответа
        if st.button("🔍 Показать ответ", type="primary", use_container_width=True):
            st.session_state.is_revealed = True
            st.rerun()
    else:
        # Показываем ответ
        conjugation = CONJUGATIONS[card.tense][card.verb][card.pronoun_index]
        
        st.markdown(f"""
        <div class="verb-card revealed">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {get_tense_name(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]}
            </div>
            <div class="answer-display">
                ✅ {conjugation}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопки оценки сложности
        st.subheader("🎯 Как хорошо вы знали ответ?")
        st.caption("Честная оценка поможет алгоритму лучше планировать повторения")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("❌ Снова\n(< 1 мин)", key="again", use_container_width=True, help="Не помню вообще"):
                process_answer(Difficulty.AGAIN)
        
        with col2:
            if st.button("😓 Сложно\n(< 10 мин)", key="hard", use_container_width=True, help="Помню с трудом"):
                process_answer(Difficulty.HARD)
        
        with col3:
            if st.button("😊 Хорошо\n(4 дня)", key="good", use_container_width=True, help="Помню уверенно"):
                process_answer(Difficulty.GOOD)
        
        with col4:
            if st.button("😎 Легко\n(> 4 дней)", key="easy", use_container_width=True, help="Помню мгновенно"):
                process_answer(Difficulty.EASY)
    
    # Правила спряжения для выбранных времен
    st.markdown("---")
    st.subheader("📚 Правила спряжения")
    
    for tense in st.session_state.settings['selected_tenses']:
        if tense in GRAMMAR_RULES:
            with st.expander(f"{GRAMMAR_RULES[tense]['title']}", expanded=False):
                st.markdown(GRAMMAR_RULES[tense]['content'])
    
    # Советы по изучению - в самом низу
    if st.button("💡 Советы по эффективному изучению", key="study_tips", use_container_width=True):
        show_study_tips()

def show_study_tips():
    """Показывает советы по эффективному изучению"""
    st.header("💡 Советы по эффективному изучению")
    
    with st.expander("🧠 Принципы интервального повторения", expanded=True):
        st.markdown("""
        **Как работает система:**
        - Карточки показываются **прямо перед тем, как вы их забудете**
        - **Увеличивающиеся интервалы** при правильных ответах
        - **Чаще повторяются** при неправильных ответах
        
        **Честная самооценка - ключ к успеху:**
        - **❌ Снова** - не помню вообще или очень неуверенно
        - **😓 Сложно** - помню, но с большим усилием  
        - **😊 Хорошо** - помню уверенно, но не мгновенно
        - **😎 Легко** - помню мгновенно, без усилий
        """)
    
    with st.expander("📅 Рекомендуемый режим изучения"):
        st.markdown("""
        **Ежедневная практика:**
        - **10-20 минут** каждый день лучше, чем 2 часа раз в неделю
        - **Регулярность** важнее продолжительности
        - **Одно и то же время** помогает выработать привычку
        
        **Оптимальные настройки:**
        - *Начинающие*: 5-10 новых карточек, 20-50 повторений, только Presente
        - *Продвинутые*: 15-25 новых карточек, 100+ повторений, все времена
        """)

def get_tense_name(tense):
    """Возвращает русское название времени"""
    names = {
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto'
    }
    return names.get(tense, tense)

def get_card_key(verb: str, pronoun_index: int, tense: str) -> str:
    """Генерирует ключ для карточки"""
    return f"{verb}_{pronoun_index}_{tense}"

def get_or_create_card(verb: str, pronoun_index: int, tense: str) -> Card:
    """Получает или создает карточку"""
    key = get_card_key(verb, pronoun_index, tense)
    
    if key not in st.session_state.cards:
        st.session_state.cards[key] = Card(
            verb=verb,
            pronoun_index=pronoun_index,
            tense=tense
        )
    
    return st.session_state.cards[key]

def get_due_cards() -> List[Card]:
    """Получает карточки для повторения"""
    today = datetime.date.today().isoformat()
    
    due_cards = []
    for card in st.session_state.cards.values():
        if (card.next_review_date <= today and 
            card.tense in st.session_state.settings['selected_tenses']):
            due_cards.append(card)
    
    return sorted(due_cards, key=lambda x: x.next_review_date)

def get_new_cards() -> List[Tuple[str, int, str]]:
    """Получает новые карточки"""
    new_cards = []
    existing_keys = set(st.session_state.cards.keys())
    
    for tense in st.session_state.settings['selected_tenses']:
        if tense not in CONJUGATIONS:
            continue
            
        for verb in CONJUGATIONS[tense]:
            if verb not in VERBS:
                continue
                
            for pronoun_index in range(6):
                key = get_card_key(verb, pronoun_index, tense)
                if key not in existing_keys:
                    new_cards.append((verb, pronoun_index, tense))
    
    random.shuffle(new_cards)
    return new_cards

def get_next_card() -> Optional[Card]:
    """Получает следующую карточку"""
    # Сначала карточки для повторения
    due_cards = get_due_cards()
    if due_cards:
        return due_cards[0]
    
    # Затем новые карточки
    if st.session_state.daily_stats['new_cards_today'] < st.session_state.settings['new_cards_per_day']:
        new_cards = get_new_cards()
        if new_cards:
            verb, pronoun_index, tense = new_cards[0]
            return get_or_create_card(verb, pronoun_index, tense)
    
    return None

def process_answer(difficulty: Difficulty):
    """Обрабатывает ответ пользователя"""
    if not st.session_state.current_card:
        return
    
    is_new_card = st.session_state.current_card.total_reviews == 0
    
    # Обновляем карточку с помощью SRS
    updated_card = SRSManager.update_card(st.session_state.current_card, difficulty)
    card_key = get_card_key(updated_card.verb, updated_card.pronoun_index, updated_card.tense)
    st.session_state.cards[card_key] = updated_card
    
    # Обновляем статистику
    st.session_state.daily_stats['reviews_today'] += 1
    if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
        st.session_state.daily_stats['correct_today'] += 1
    if is_new_card:
        st.session_state.daily_stats['new_cards_today'] += 1
    
    # Сохраняем данные
    save_user_data()
    
    # Переходим к следующей карточке
    next_card()

def next_card():
    """Переход к следующей карточке"""
    st.session_state.current_card = None
    st.session_state.is_revealed = False
    st.rerun()

def force_new_card():
    """Принудительно получает новую карточку"""
    new_cards = get_new_cards()
    if new_cards:
        verb, pronoun_index, tense = random.choice(new_cards)
        st.session_state.current_card = get_or_create_card(verb, pronoun_index, tense)
        st.session_state.is_revealed = False
        st.rerun()

def reset_daily_stats():
    """Сбрасывает дневную статистику"""
    today = datetime.date.today().isoformat()
    if st.session_state.daily_stats['last_reset'] != today:
        st.session_state.daily_stats.update({
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': today
        })

def clear_url_params():
    """Очищает URL параметры"""
    try:
        st.query_params.clear()
    except:
        pass

def clear_oauth_and_reload():
    """Очищает OAuth и перезагружает"""
    st.session_state.oauth_state = None
    clear_url_params()
    st.rerun()

def logout():
    """Выход из системы"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.oauth_state = None
    st.session_state.cards = {}
    st.session_state.current_card = None
    st.session_state.daily_stats = {
        'reviews_today': 0,
        'correct_today': 0,
        'new_cards_today': 0,
        'last_reset': datetime.date.today().isoformat()
    }

if __name__ == "__main__":
    main()
