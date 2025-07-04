import streamlit as st
import random
import json
import datetime
import math
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Пробуем импортировать plotly, если не получается - используем альтернативу
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Local Storage пока недоступен в простом варианте
LOCAL_STORAGE_AVAILABLE = False

# Конфигурация страницы
st.set_page_config(
    page_title="🇪🇸 Тренажер испанских глаголов с интервальным повторением",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стили
st.markdown("""
<style>
    .card-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    }
    
    .verb-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .verb-translation {
        font-size: 1.4rem;
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }
    
    .pronoun-display {
        font-size: 2rem;
        font-weight: bold;
        margin: 1.5rem 0;
        background: rgba(255,255,255,0.2);
        padding: 0.8rem 1.5rem;
        border-radius: 0.5rem;
        display: inline-block;
    }
    
    .answer-display {
        font-size: 2.5rem;
        font-weight: bold;
        background: rgba(255,255,255,0.9);
        color: #2d5e3e;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .difficulty-btn {
        margin: 0.2rem;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: bold;
        cursor: pointer;
    }
    
    .btn-again { background: #ff6b6b; color: white; }
    .btn-hard { background: #feca57; color: black; }
    .btn-good { background: #48ca8b; color: white; }
    .btn-easy { background: #0abde3; color: white; }
    
    /* Стили для боковой панели */
    .stSidebar > div > div > div > div {
        padding-top: 1rem;
    }
    
    /* Ярче кнопка сворачивания панели */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 50% !important;
        font-weight: bold !important;
        font-size: 1.8rem !important;
        width: 4rem !important;
        height: 4rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 4px solid #ffffff !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
        position: fixed !important;
        z-index: 999 !important;
        animation: pulse 2s infinite !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #5a67d8, #6b46c1) !important;
        transform: scale(1.15) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.7) !important;
        animation: none !important;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 6px 25px rgba(102, 126, 234, 0.8); }
        100% { box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5); }
    }
    
    /* Более заметные вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0.5rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        background: white;
        color: #4a5568;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border-color: #667eea !important;
    }
    
    /* Стили для карточки */
    .card-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .card-container.revealed {
        background: linear-gradient(135deg, #48ca8b 0%, #2dd4bf 100%);
        transform: scale(1.02);
        box-shadow: 0 12px 40px rgba(72, 202, 139, 0.3);
    }
    /* Менее заметная кнопка сброса */
    .reset-btn {
        background: #f7fafc !important;
        color: #718096 !important;
        border: 1px solid #e2e8f0 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 15px !important;
        font-size: 0.85rem !important;
        margin-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Перечисления для оценки сложности
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
    easiness_factor: float = 2.5  # Начальная легкость
    interval: int = 1             # Интервал в днях
    repetitions: int = 0          # Количество повторений
    next_review_date: str = ""    # Дата следующего повторения
    last_review_date: str = ""    # Дата последнего повторения
    total_reviews: int = 0        # Общее количество повторений
    correct_reviews: int = 0      # Количество правильных ответов
    
    def __post_init__(self):
        if not self.next_review_date:
            self.next_review_date = datetime.date.today().isoformat()

# Данные глаголов (те же что и раньше)
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
    'estudiar': {'translation': 'изучать', 'type': 'regular-ar'}
}

PRONOUNS = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']

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
        'estudiar': ['estudio', 'estudias', 'estudia', 'estudiamos', 'estudiáis', 'estudian']
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
        'llevar': ['llevé', 'llevaste', 'llevó', 'llevamos', 'llevasteis', 'llevaron'],
        'dejar': ['dejé', 'dejaste', 'dejó', 'dejamos', 'dejasteis', 'dejaron'],
        'seguir': ['seguí', 'seguiste', 'siguió', 'seguimos', 'seguisteis', 'siguieron'],
        'encontrar': ['encontré', 'encontraste', 'encontró', 'encontramos', 'encontrasteis', 'encontraron'],
        'llamar': ['llamé', 'llamaste', 'llamó', 'llamamos', 'llamasteis', 'llamaron'],
        'venir': ['vine', 'viniste', 'vino', 'vinimos', 'vinisteis', 'vinieron'],
        'pensar': ['pensé', 'pensaste', 'pensó', 'pensamos', 'pensasteis', 'pensaron'],
        'salir': ['salí', 'saliste', 'salió', 'salimos', 'salisteis', 'salieron'],
        'vivir': ['viví', 'viviste', 'vivió', 'vivimos', 'vivisteis', 'vivieron'],
        'sentir': ['sentí', 'sentiste', 'sintió', 'sentimos', 'sentisteis', 'sintieron'],
        'trabajar': ['trabajé', 'trabajaste', 'trabajó', 'trabajamos', 'trabajasteis', 'trabajaron'],
        'estudiar': ['estudié', 'estudiaste', 'estudió', 'estudiamos', 'estudiasteis', 'estudiaron']
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
        'llegar': ['llegue', 'llegues', 'llegue', 'lleguemos', 'lleguéis', 'lleguen'],
        'pasar': ['pase', 'pases', 'pase', 'pasemos', 'paséis', 'pasen'],
        'deber': ['deba', 'debas', 'deba', 'debamos', 'debáis', 'deban'],
        'poner': ['ponga', 'pongas', 'ponga', 'pongamos', 'pongáis', 'pongan'],
        'parecer': ['parezca', 'parezcas', 'parezca', 'parezcamos', 'parezcáis', 'parezcan'],
        'quedar': ['quede', 'quedes', 'quede', 'quedemos', 'quedéis', 'queden'],
        'creer': ['crea', 'creas', 'crea', 'creamos', 'creáis', 'crean'],
        'hablar': ['hable', 'hables', 'hable', 'hablemos', 'habléis', 'hablen'],
        'llevar': ['lleve', 'lleves', 'lleve', 'llevemos', 'llevéis', 'lleven'],
        'dejar': ['deje', 'dejes', 'deje', 'dejemos', 'dejéis', 'dejen'],
        'seguir': ['siga', 'sigas', 'siga', 'sigamos', 'sigáis', 'sigan'],
        'encontrar': ['encuentre', 'encuentres', 'encuentre', 'encontremos', 'encontréis', 'encuentren'],
        'llamar': ['llame', 'llames', 'llame', 'llamemos', 'llaméis', 'llamen'],
        'venir': ['venga', 'vengas', 'venga', 'vengamos', 'vengáis', 'vengan'],
        'pensar': ['piense', 'pienses', 'piense', 'pensemos', 'penséis', 'piensen'],
        'salir': ['salga', 'salgas', 'salga', 'salgamos', 'salgáis', 'salgan'],
        'vivir': ['viva', 'vivas', 'viva', 'vivamos', 'viváis', 'vivan'],
        'sentir': ['sienta', 'sientas', 'sienta', 'sintamos', 'sintáis', 'sientan'],
        'trabajar': ['trabaje', 'trabajes', 'trabaje', 'trabajemos', 'trabajéis', 'trabajen'],
        'estudiar': ['estudie', 'estudies', 'estudie', 'estudiemos', 'estudiéis', 'estudien']
    },
    'imperfecto': {
        'ser': ['era', 'eras', 'era', 'éramos', 'erais', 'eran'],
        'estar': ['estaba', 'estabas', 'estaba', 'estábamos', 'estabais', 'estaban'],
        'tener': ['tenía', 'tenías', 'tenía', 'teníamos', 'teníais', 'tenían'],
        'hacer': ['hacía', 'hacías', 'hacía', 'hacíamos', 'hacíais', 'hacían'],
        'decir': ['decía', 'decías', 'decía', 'decíamos', 'decíais', 'decían'],
        'ir': ['iba', 'ibas', 'iba', 'íbamos', 'ibais', 'iban'],
        'ver': ['veía', 'veías', 'veía', 'veíamos', 'veíais', 'veían'],
        'dar': ['daba', 'dabas', 'daba', 'dábamos', 'dabais', 'daban'],
        'saber': ['sabía', 'sabías', 'sabía', 'sabíamos', 'sabíais', 'sabían'],
        'querer': ['quería', 'querías', 'quería', 'queríamos', 'queríais', 'querían'],
        'llegar': ['llegaba', 'llegabas', 'llegaba', 'llegábamos', 'llegabais', 'llegaban'],
        'pasar': ['pasaba', 'pasabas', 'pasaba', 'pasábamos', 'pasabais', 'pasaban'],
        'deber': ['debía', 'debías', 'debía', 'debíamos', 'debíais', 'debían'],
        'poner': ['ponía', 'ponías', 'ponía', 'poníamos', 'poníais', 'ponían'],
        'parecer': ['parecía', 'parecías', 'parecía', 'parecíamos', 'parecíais', 'parecían'],
        'quedar': ['quedaba', 'quedabas', 'quedaba', 'quedábamos', 'quedabais', 'quedaban'],
        'creer': ['creía', 'creías', 'creía', 'creíamos', 'creíais', 'creían'],
        'hablar': ['hablaba', 'hablabas', 'hablaba', 'hablábamos', 'hablabais', 'hablaban'],
        'llevar': ['llevaba', 'llevabas', 'llevaba', 'llevábamos', 'llevabais', 'llevaban'],
        'dejar': ['dejaba', 'dejabas', 'dejaba', 'dejábamos', 'dejabais', 'dejaban'],
        'seguir': ['seguía', 'seguías', 'seguía', 'seguíamos', 'seguíais', 'seguían'],
        'encontrar': ['encontraba', 'encontrabas', 'encontraba', 'encontrábamos', 'encontrabais', 'encontraban'],
        'llamar': ['llamaba', 'llamabas', 'llamaba', 'llamábamos', 'llamabais', 'llamaban'],
        'venir': ['venía', 'venías', 'venía', 'veníamos', 'veníais', 'venían'],
        'pensar': ['pensaba', 'pensabas', 'pensaba', 'pensábamos', 'pensabais', 'pensaban'],
        'salir': ['salía', 'salías', 'salía', 'salíamos', 'salíais', 'salían'],
        'vivir': ['vivía', 'vivías', 'vivía', 'vivíamos', 'vivíais', 'vivían'],
        'sentir': ['sentía', 'sentías', 'sentía', 'sentíamos', 'sentíais', 'sentían'],
        'trabajar': ['trabajaba', 'trabajabas', 'trabajaba', 'trabajábamos', 'trabajabais', 'trabajaban'],
        'estudiar': ['estudiaba', 'estudiabas', 'estudiaba', 'estudiábamos', 'estudíabais', 'estudiaban']
    }
}

class SRSManager:
    """Менеджер системы интервального повторения"""
    
    @staticmethod
    def calculate_next_interval(card: Card, difficulty: Difficulty) -> Tuple[int, float]:
        """
        Алгоритм SM-2 для расчета следующего интервала
        Возвращает (новый_интервал, новый_easiness_factor)
        """
        ef = card.easiness_factor
        interval = card.interval
        repetitions = card.repetitions
        
        if difficulty == Difficulty.AGAIN:
            # Сбрасываем прогресс, начинаем заново
            return 1, max(1.3, ef - 0.2)
        
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ef)
        
        # Обновляем easiness factor на основе сложности
        if difficulty == Difficulty.EASY:
            ef = ef + 0.15
        elif difficulty == Difficulty.GOOD:
            ef = ef + 0.1
        elif difficulty == Difficulty.HARD:
            ef = ef - 0.15
        
        # Ограничиваем easiness factor
        ef = max(1.3, min(3.0, ef))
        
        return interval, ef
    
    @staticmethod
    def update_card(card: Card, difficulty: Difficulty) -> Card:
        """Обновляет карточку после ответа"""
        today = datetime.date.today()
        
        # Обновляем статистику
        card.total_reviews += 1
        if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
            card.correct_reviews += 1
        
        # Рассчитываем новый интервал
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

class DataManager:
    """Менеджер сохранения и загрузки данных"""
    
    @staticmethod
    def save_to_local_storage():
        """Псевдо-сохранение (данные уже в session_state)"""
        # В текущей версии данные сохраняются в session_state автоматически
        # В будущем здесь будет Google Auth
        return True
    
    @staticmethod
    def load_from_local_storage():
        """Псевдо-загрузка (данные уже в session_state)"""
        # В текущей версии данные загружаются из session_state автоматически
        # В будущем здесь будет Google Auth
        return False
    
    @staticmethod
    def clear_all_data():
        """Полностью очищает все данные"""
        # Очищаем session state
        st.session_state.cards = {}
        st.session_state.current_card = None
        st.session_state.daily_stats = {
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': datetime.date.today().isoformat()
        }

def init_session_state():
    """Инициализация состояния сессии"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
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
    
    if 'show_tips' not in st.session_state:
        st.session_state.show_tips = False
    
    # Флаг для отслеживания первого запуска
    if 'first_time' not in st.session_state:
        st.session_state.first_time = True
    
    # Флаг для отслеживания изменений настроек
    if 'settings_changed' not in st.session_state:
        st.session_state.settings_changed = False

def get_card_key(verb: str, pronoun_index: int, tense: str) -> str:
    """Генерирует уникальный ключ для карточки"""
    return f"{verb}_{pronoun_index}_{tense}"

def get_or_create_card(verb: str, pronoun_index: int, tense: str) -> Card:
    """Получает существующую карточку или создает новую"""
    key = get_card_key(verb, pronoun_index, tense)
    
    if key not in st.session_state.cards:
        st.session_state.cards[key] = Card(
            verb=verb,
            pronoun_index=pronoun_index,
            tense=tense
        )
    
    return st.session_state.cards[key]

def get_due_cards() -> List[Card]:
    """Получает карточки для повторения на сегодня"""
    today = datetime.date.today().isoformat()
    
    due_cards = []
    for card in st.session_state.cards.values():
        if (card.next_review_date <= today and 
            card.tense in st.session_state.settings['selected_tenses']):
            due_cards.append(card)
    
    return sorted(due_cards, key=lambda x: x.next_review_date)

def get_new_cards() -> List[Tuple[str, int, str]]:
    """Получает новые карточки для изучения"""
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
    """Получает следующую карточку для изучения"""
    # Сначала проверяем карточки для повторения
    due_cards = get_due_cards()
    if due_cards and len(due_cards) > 0:
        return due_cards[0]
    
    # Затем новые карточки
    if st.session_state.daily_stats['new_cards_today'] < st.session_state.settings['new_cards_per_day']:
        new_cards = get_new_cards()
        if new_cards:
            verb, pronoun_index, tense = new_cards[0]
            return get_or_create_card(verb, pronoun_index, tense)
    
    return None

def reset_daily_stats():
    """Сбрасывает дневную статистику при смене дня"""
    today = datetime.date.today().isoformat()
    if st.session_state.daily_stats['last_reset'] != today:
        st.session_state.daily_stats.update({
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': today
        })

def process_answer(difficulty: Difficulty):
    """Обрабатывает ответ пользователя"""
    if not st.session_state.current_card:
        return
    
    # Отмечаем карточку как новую если это первый раз
    is_new_card = st.session_state.current_card.total_reviews == 0
    
    # Обновляем карточку
    updated_card = SRSManager.update_card(st.session_state.current_card, difficulty)
    card_key = get_card_key(
        updated_card.verb, 
        updated_card.pronoun_index, 
        updated_card.tense
    )
    st.session_state.cards[card_key] = updated_card
    
    # Обновляем статистику
    st.session_state.daily_stats['reviews_today'] += 1
    if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
        st.session_state.daily_stats['correct_today'] += 1
    if is_new_card:
        st.session_state.daily_stats['new_cards_today'] += 1
    
    # Автосохранение в Local Storage
    if st.session_state.settings.get('auto_save', True):
        DataManager.save_to_local_storage()
    
    # Сбрасываем текущую карточку
    st.session_state.current_card = None
    st.session_state.is_revealed = False

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
    
    with st.expander("🎯 Стратегии изучения"):
        st.markdown("""
        **Этап 1: Знакомство (первые 2 недели)**
        - Только **Presente** - самое важное время
        - **5 новых карточек в день**
        - Фокус на **регулярных глаголах** (-ar, -er, -ir)
        
        **Этап 2: Расширение (3-4 недели)**  
        - Добавьте **Pretérito Indefinido**
        - Увеличьте до **10 новых карточек**
        - Начните **неправильные глаголы** (ser, estar, tener)
        
        **Этап 3: Углубление (2+ месяца)**
        - **Все времена одновременно**
        - **15+ новых карточек в день**
        - Фокус на **сложных глаголах** (subjuntivo)
        """)
    
    with st.expander("💡 Техники запоминания"):
        st.markdown("""
        **Мнемонические приемы:**
        - **Ассоциации**: связывайте формы с похожими словами
        - **Рифмы**: "yo soy, tú vas, él da"
        - **Визуальные образы**: представляйте ситуации использования
        
        **Группировка глаголов:**
        - По типу: регулярные vs неправильные
        - По частоте: изучайте сначала самые частые
        - По теме: глаголы движения, эмоций, действий
        """)
    
    with st.expander("📊 Интерпретация статистики"):
        st.markdown("""
        **Здоровые показатели:**
        - Точность: **80-90%** (в долгосрочной перспективе)
        - Новых карточек: **70%** от дневного лимита
        - Активные дни: **6-7 дней в неделю**
        
        **Тревожные сигналы:**
        - Точность **< 70%** - слишком много новых карточек
        - **Пропуск дней** - нарушается принцип интервального повторения
        - Много карточек **"Снова"** - изучаете слишком быстро
        """)

def show_statistics():
    """Показывает подробную статистику"""
    if not st.session_state.cards:
        st.info("Пока нет данных для статистики. Начните изучение!")
        return
    
    st.header("📊 Детальная статистика")
    
    # Общая статистика
    total_cards = len(st.session_state.cards)
    total_reviews = sum(card.total_reviews for card in st.session_state.cards.values())
    total_correct = sum(card.correct_reviews for card in st.session_state.cards.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Всего карточек", total_cards)
    with col2:
        st.metric("🔄 Всего повторений", total_reviews)
    with col3:
        accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
        st.metric("🎯 Точность", f"{accuracy:.1f}%")
    with col4:
        due_today = len(get_due_cards())
        st.metric("⏰ К повторению", due_today)
    
    # Статистика по категориям карточек
    st.subheader("📈 Распределение карточек")
    
    today = datetime.date.today().isoformat()
    categories = {
        'Новые': 0,
        'Изучаемые': 0,
        'Повторение': 0,
        'Завершенные': 0
    }
    
    for card in st.session_state.cards.values():
        if card.total_reviews == 0:
            categories['Новые'] += 1
        elif card.repetitions < 5:
            categories['Изучаемые'] += 1
        elif card.next_review_date <= today:
            categories['Повторение'] += 1
        else:
            categories['Завершенные'] += 1
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for i, (category, count) in enumerate(categories.items()):
        with cols[i]:
            st.metric(category, count)
    
    # График прогресса по дням
    if total_reviews > 0:
        st.subheader("📅 Активность по времени")
        
        # Создаем данные для графика
        review_dates = []
        for card in st.session_state.cards.values():
            if card.last_review_date:
                review_dates.append(card.last_review_date)
        
        if review_dates:
            df = pd.DataFrame({'date': review_dates})
            df['date'] = pd.to_datetime(df['date'])
            daily_reviews = df.groupby(df['date'].dt.date).size().reset_index()
            daily_reviews.columns = ['Дата', 'Повторений']
            daily_reviews['Дата'] = daily_reviews['Дата'].astype(str)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(daily_reviews, x='Дата', y='Повторений', 
                            title='Количество повторений по дням')
                
                # Упрощаем график - убираем лишние элементы управления
                fig.update_layout(
                    showlegend=False,
                    xaxis=dict(
                        title="Дата",
                        showgrid=True,
                        fixedrange=True  # Отключаем зум по X
                    ),
                    yaxis=dict(
                        title="Количество повторений",
                        showgrid=True,
                        fixedrange=True  # Отключаем зум по Y
                    ),
                    dragmode=False,  # Отключаем драг
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                # Убираем тулбар и делаем график статичным
                config = {
                    'displayModeBar': False,
                    'staticPlot': False,
                    'scrollZoom': False,
                    'doubleClick': False,
                    'showTips': False,
                    'displaylogo': False
                }
                
                st.plotly_chart(fig, use_container_width=True, config=config)
            else:
                # Простая таблица вместо графика
                st.dataframe(daily_reviews, use_container_width=True, hide_index=True)
                st.caption("📊 Для графика установите plotly: pip install plotly")
    
    # Статистика по временам
    st.subheader("⏰ Статистика по временам")
    
    tense_stats = {}
    for card in st.session_state.cards.values():
        tense = card.tense
        if tense not in tense_stats:
            tense_stats[tense] = {
                'total': 0,
                'reviews': 0,
                'correct': 0
            }
        
        tense_stats[tense]['total'] += 1
        tense_stats[tense]['reviews'] += card.total_reviews
        tense_stats[tense]['correct'] += card.correct_reviews
    
    tense_names = {
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto'
    }
    
    for tense, stats in tense_stats.items():
        tense_name = tense_names.get(tense, tense)
        accuracy = (stats['correct'] / stats['reviews'] * 100) if stats['reviews'] > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{tense_name} - Карточек", stats['total'])
        with col2:
            st.metric(f"{tense_name} - Повторений", stats['reviews'])
        with col3:
            st.metric(f"{tense_name} - Точность", f"{accuracy:.1f}%")

def apply_settings():
    """Применяет настройки и сохраняет их"""
    if st.session_state.settings.get('auto_save', True):
        DataManager.save_to_local_storage()
    
    # Сбрасываем текущую карточку чтобы обновить в соответствии с новыми настройками
    st.session_state.current_card = None
    st.session_state.is_revealed = False
    
    st.success("✅ Настройки применены и сохранены!")
    if not st.session_state.cards:
        st.info("Пока нет данных для статистики. Начните изучение!")
        return
    
    st.header("📊 Детальная статистика")
    
    # Общая статистика
    total_cards = len(st.session_state.cards)
    total_reviews = sum(card.total_reviews for card in st.session_state.cards.values())
    total_correct = sum(card.correct_reviews for card in st.session_state.cards.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Всего карточек", total_cards)
    with col2:
        st.metric("🔄 Всего повторений", total_reviews)
    with col3:
        accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
        st.metric("🎯 Точность", f"{accuracy:.1f}%")
    with col4:
        due_today = len(get_due_cards())
        st.metric("⏰ К повторению", due_today)
    
    # Статистика по категориям карточек
    st.subheader("📈 Распределение карточек")
    
    today = datetime.date.today().isoformat()
    categories = {
        'Новые': 0,
        'Изучаемые': 0,
        'Повторение': 0,
        'Завершенные': 0
    }
    
    for card in st.session_state.cards.values():
        if card.total_reviews == 0:
            categories['Новые'] += 1
        elif card.repetitions < 5:
            categories['Изучаемые'] += 1
        elif card.next_review_date <= today:
            categories['Повторение'] += 1
        else:
            categories['Завершенные'] += 1
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for i, (category, count) in enumerate(categories.items()):
        with cols[i]:
            st.metric(category, count)
    
    # График прогресса по дням
    if total_reviews > 0:
        st.subheader("📅 Активность по времени")
        
        # Создаем данные для графика
        review_dates = []
        for card in st.session_state.cards.values():
            if card.last_review_date:
                review_dates.append(card.last_review_date)
        
        if review_dates:
            df = pd.DataFrame({'date': review_dates})
            df['date'] = pd.to_datetime(df['date'])
            daily_reviews = df.groupby(df['date'].dt.date).size().reset_index()
            daily_reviews.columns = ['Дата', 'Повторений']
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(daily_reviews, x='Дата', y='Повторений', 
                            title='Количество повторений по дням')
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Простая таблица вместо графика
                st.dataframe(daily_reviews, use_container_width=True)
                st.caption("📊 График активности (установите plotly для полной визуализации)")
    
    # Статистика по временам
    st.subheader("⏰ Статистика по временам")
    
    tense_stats = {}
    for card in st.session_state.cards.values():
        tense = card.tense
        if tense not in tense_stats:
            tense_stats[tense] = {
                'total': 0,
                'reviews': 0,
                'correct': 0
            }
        
        tense_stats[tense]['total'] += 1
        tense_stats[tense]['reviews'] += card.total_reviews
        tense_stats[tense]['correct'] += card.correct_reviews
    
    tense_names = {
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto'
    }
    
    for tense, stats in tense_stats.items():
        tense_name = tense_names.get(tense, tense)
        accuracy = (stats['correct'] / stats['reviews'] * 100) if stats['reviews'] > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{tense_name} - Карточек", stats['total'])
        with col2:
            st.metric(f"{tense_name} - Повторений", stats['reviews'])
        with col3:
            st.metric(f"{tense_name} - Точность", f"{accuracy:.1f}%")

def main():
    init_session_state()
    reset_daily_stats()
    
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption("Система интервального повторения для эффективного изучения")
    
    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки")
        
        # Советы по изучению - в самом начале
        if st.button("💡 Советы по эффективному изучению", key="study_tips", use_container_width=True):
            st.session_state.show_tips = True
        
        st.markdown("---")
        
        # Выбор времен
        st.subheader("📚 Времена для изучения")
        tense_options = {
            'presente': 'Presente',
            'indefinido': 'Pretérito Indefinido',
            'subjuntivo': 'Subjuntivo Presente',
            'imperfecto': 'Pretérito Imperfecto'
        }
        
        # Сохраняем текущие настройки для сравнения
        current_settings = {
            'selected_tenses': st.session_state.settings['selected_tenses'].copy(),
            'new_cards_per_day': st.session_state.settings['new_cards_per_day'],
            'review_cards_per_day': st.session_state.settings['review_cards_per_day'],
            'auto_save': st.session_state.settings.get('auto_save', True)
        }
        
        # Временные переменные для новых настроек
        new_selected_tenses = []
        for tense_key, tense_name in tense_options.items():
            if st.checkbox(tense_name, value=tense_key in st.session_state.settings['selected_tenses'], key=f"tense_{tense_key}"):
                new_selected_tenses.append(tense_key)
        
        new_selected_tenses = new_selected_tenses or ['presente']
        
        # Настройки лимитов
        st.subheader("🎯 Дневные лимиты")
        new_new_cards = st.slider(
            "Новых карточек в день", 1, 50, st.session_state.settings['new_cards_per_day'], key="new_cards_slider"
        )
        new_review_cards = st.slider(
            "Повторений в день", 10, 200, st.session_state.settings['review_cards_per_day'], key="review_cards_slider"
        )
        
        # Автосохранение
        new_auto_save = st.checkbox(
            "🔄 Автосохранение", 
            value=st.session_state.settings.get('auto_save', True),
            help="Автоматически сохранять прогресс в браузере",
            key="auto_save_checkbox"
        )
        
        # Проверяем, изменились ли настройки
        settings_changed = (
            current_settings['selected_tenses'] != new_selected_tenses or
            current_settings['new_cards_per_day'] != new_new_cards or
            current_settings['review_cards_per_day'] != new_review_cards or
            current_settings['auto_save'] != new_auto_save
        )
        
        # Кнопка применить (показывается только если настройки изменились)
        if settings_changed:
            if st.button("✅ Применить настройки", key="apply_settings", use_container_width=True, type="primary"):
                # Применяем настройки
                st.session_state.settings['selected_tenses'] = new_selected_tenses
                st.session_state.settings['new_cards_per_day'] = new_new_cards
                st.session_state.settings['review_cards_per_day'] = new_review_cards
                st.session_state.settings['auto_save'] = new_auto_save
                
                apply_settings()
                st.rerun()
        
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
        
        # Общая точность
        total_reviews = sum(card.total_reviews for card in st.session_state.cards.values())
        total_correct = sum(card.correct_reviews for card in st.session_state.cards.values())
        accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
        st.metric("🎯 Общая точность", f"{accuracy:.1f}%")
        
        # Информация о хранении данных
        st.markdown("---")
        st.subheader("💾 Хранение данных")
        st.info("ℹ️ Данные сохраняются в рамках сессии браузера")
        st.caption("Для постоянного сохранения планируется Google Auth")
        
        if st.button("💾 Google Auth (скоро)", type="secondary", disabled=True, key="google_auth_placeholder"):
            st.info("🚧 Функция Google авторизации находится в разработке")
        
        # Кнопка сброса прогресса (внизу, менее заметная)
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Сбросить прогресс", key="reset_progress", use_container_width=True):
            if st.checkbox("Я понимаю, что все данные будут удалены", key="confirm_reset"):
                DataManager.clear_all_data()
                st.success("Прогресс сброшен!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Основной интерфейс
    # Проверяем, нужно ли показать советы
    if st.session_state.get('show_tips', False):
        show_study_tips()
        if st.button("← Вернуться к изучению", type="primary"):
            st.session_state.show_tips = False
            st.rerun()
        return
    
    tab1, tab2 = st.tabs(["🎓 Изучение", "📊 Статистика"])
    
    with tab1:
        # Получаем следующую карточку если нет текущей
        if not st.session_state.current_card:
            st.session_state.current_card = get_next_card()
            st.session_state.is_revealed = False
        
        if not st.session_state.current_card:
            st.success("🎉 Отлично! Вы завершили все запланированные повторения на сегодня!")
            st.info("Возвращайтесь завтра для новых карточек или измените настройки в боковой панели.")
            return
        
        card = st.session_state.current_card
        
        # Проверяем что у нас есть данные для этой карточки
        if (card.verb not in VERBS or 
            card.tense not in CONJUGATIONS or 
            card.verb not in CONJUGATIONS[card.tense]):
            st.error("❌ Ошибка: данные карточки повреждены")
            st.session_state.current_card = None
            st.rerun()
            return
        
        verb_info = VERBS[card.verb]
        
        # Отображаем карточку
        st.markdown(f"""
        <div class="card-container">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1rem; opacity: 0.8; margin-bottom: 1rem;">
                {card.tense.title()}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Информация о карточке
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Повторений", card.total_reviews)
        with col2:
            accuracy = (card.correct_reviews / card.total_reviews * 100) if card.total_reviews > 0 else 0
            st.metric("Точность", f"{accuracy:.0f}%")
        with col3:
            st.metric("Легкость", f"{card.easiness_factor:.1f}")
        
        if not st.session_state.is_revealed:
            # Кнопка показа ответа
            if st.button("🔍 Показать ответ", type="primary", use_container_width=True):
                st.session_state.is_revealed = True
                st.rerun()
        else:
            # Показываем ответ
            conjugation = CONJUGATIONS[card.tense][card.verb][card.pronoun_index]
            
            st.markdown(f"""
            <div class="answer-display">
                ✅ {conjugation}
            </div>
            """, unsafe_allow_html=True)
            
            # Кнопки оценки сложности
            st.subheader("🎯 Как легко было ответить?")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("❌ Снова\n(< 1 мин)", key="again", use_container_width=True):
                    process_answer(Difficulty.AGAIN)
                    st.rerun()
            
            with col2:
                if st.button("😓 Сложно\n(< 10 мин)", key="hard", use_container_width=True):
                    process_answer(Difficulty.HARD)
                    st.rerun()
            
            with col3:
                if st.button("😊 Хорошо\n(4 дня)", key="good", use_container_width=True):
                    process_answer(Difficulty.GOOD)
                    st.rerun()
            
            with col4:
                if st.button("😎 Легко\n(> 4 дней)", key="easy", use_container_width=True):
                    process_answer(Difficulty.EASY)
                    st.rerun()
            
            st.caption("Выберите, насколько легко было вспомнить ответ. Это влияет на частоту повторения карточки.")
    
    with tab2:
        show_statistics()

if __name__ == "__main__":
    main()
