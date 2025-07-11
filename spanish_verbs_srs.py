import streamlit as st
import sqlite3
import hashlib
import datetime
import random
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import os

# Конфигурация
st.set_page_config(
    page_title="🇪🇸 Тренажер испанских глаголов",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Путь к базе данных
DB_PATH = "spanish_verbs.db"

# CSS стили
st.markdown("""
<style>
    .main > div {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
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
    
    .login-form {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 400px;
    }
    
    .user-panel {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
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
    
    .welcome-hero {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 1rem;
        margin: 2rem 0;
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

# База данных глаголов
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

# Спряжения глаголов
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

# ===== ФУНКЦИИ БАЗЫ ДАННЫХ =====

def init_database():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            settings TEXT DEFAULT '{}'
        )
    ''')
    
    # Таблица карточек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            verb TEXT NOT NULL,
            pronoun_index INTEGER NOT NULL,
            tense TEXT NOT NULL,
            easiness_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review_date TEXT NOT NULL,
            last_review_date TEXT,
            total_reviews INTEGER DEFAULT 0,
            correct_reviews INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, verb, pronoun_index, tense)
        )
    ''')
    
    # Таблица статистики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            reviews_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            new_cards_count INTEGER DEFAULT 0,
            study_time_minutes INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, date)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Проверка пароля"""
    return hash_password(password) == password_hash

def create_user(email: str, password: str, name: str) -> bool:
    """Создание нового пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (email, password_hash, name)
        )
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Email уже существует
    except Exception as e:
        st.error(f"Ошибка создания пользователя: {e}")
        return False

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Аутентификация пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, email, password_hash, name, settings FROM users WHERE email = ?",
            (email,)
        )
        
        user = cursor.fetchone()
        
        if user and verify_password(password, user[2]):
            # Обновляем время последнего входа
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user[0],)
            )
            conn.commit()
            
            user_data = {
                'id': user[0],
                'email': user[1],
                'name': user[3],
                'settings': json.loads(user[4] or '{}')
            }
            
            conn.close()
            return user_data
        
        conn.close()
        return None
    except Exception as e:
        st.error(f"Ошибка аутентификации: {e}")
        return None

def save_user_settings(user_id: int, settings: dict):
    """Сохранение настроек пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET settings = ? WHERE id = ?",
            (json.dumps(settings), user_id)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Ошибка сохранения настроек: {e}")

def load_user_cards(user_id: int) -> Dict[str, Card]:
    """Загрузка карточек пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT verb, pronoun_index, tense, easiness_factor, interval_days,
                   repetitions, next_review_date, last_review_date,
                   total_reviews, correct_reviews
            FROM cards WHERE user_id = ?
        ''', (user_id,))
        
        cards = {}
        for row in cursor.fetchall():
            card = Card(
                verb=row[0],
                pronoun_index=row[1],
                tense=row[2],
                easiness_factor=row[3],
                interval=row[4],
                repetitions=row[5],
                next_review_date=row[6],
                last_review_date=row[7],
                total_reviews=row[8],
                correct_reviews=row[9]
            )
            key = f"{row[0]}_{row[1]}_{row[2]}"
            cards[key] = card
        
        conn.close()
        return cards
    except Exception as e:
        st.error(f"Ошибка загрузки карточек: {e}")
        return {}

def save_card(user_id: int, card: Card):
    """Сохранение карточки"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cards 
            (user_id, verb, pronoun_index, tense, easiness_factor, interval_days,
             repetitions, next_review_date, last_review_date, total_reviews, 
             correct_reviews, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            user_id, card.verb, card.pronoun_index, card.tense,
            card.easiness_factor, card.interval, card.repetitions,
            card.next_review_date, card.last_review_date,
            card.total_reviews, card.correct_reviews
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Ошибка сохранения карточки: {e}")

def update_daily_stats(user_id: int, reviews_count: int = 0, correct_count: int = 0, new_cards_count: int = 0):
    """Обновление дневной статистики"""
    try:
        today = datetime.date.today().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats 
            (user_id, date, reviews_count, correct_count, new_cards_count)
            VALUES (?, ?, 
                    COALESCE((SELECT reviews_count FROM daily_stats WHERE user_id = ? AND date = ?), 0) + ?,
                    COALESCE((SELECT correct_count FROM daily_stats WHERE user_id = ? AND date = ?), 0) + ?,
                    COALESCE((SELECT new_cards_count FROM daily_stats WHERE user_id = ? AND date = ?), 0) + ?)
        ''', (user_id, today, user_id, today, reviews_count, user_id, today, correct_count, user_id, today, new_cards_count))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Ошибка обновления статистики: {e}")

def get_daily_stats(user_id: int) -> dict:
    """Получение дневной статистики"""
    try:
        today = datetime.date.today().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT reviews_count, correct_count, new_cards_count
            FROM daily_stats WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'reviews_today': result[0],
                'correct_today': result[1],
                'new_cards_today': result[2]
            }
        else:
            return {
                'reviews_today': 0,
                'correct_today': 0,
                'new_cards_today': 0
            }
    except Exception as e:
        st.error(f"Ошибка получения статистики: {e}")
        return {'reviews_today': 0, 'correct_today': 0, 'new_cards_today': 0}

# ===== ОСНОВНЫЕ ФУНКЦИИ ПРИЛОЖЕНИЯ =====

def init_session_state():
    """Инициализация session state"""
    # Аутентификация
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
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
            'new_cards_today': 0
        }
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'new_cards_per_day': 10,
            'selected_tenses': ['presente']
        }

def main():
    """Главная функция приложения"""
    # Инициализация базы данных
    init_database()
    
    # Инициализация session state
    init_session_state()
    
    # Главная логика
    if st.session_state.authenticated:
        show_main_app()
    else:
        show_auth_page()

def show_auth_page():
    """Страница аутентификации"""
    st.markdown("""
    <div class="welcome-hero">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">
            🇪🇸 Тренажер испанских глаголов
        </h1>
        <h3 style="font-weight: 400; margin-bottom: 2rem;">
            Изучайте спряжения с системой интервального повторения
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Вкладки для входа и регистрации
    tab1, tab2 = st.tabs(["🔑 Вход", "📝 Регистрация"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_registration_form()

def show_login_form():
    """Форма входа"""
    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.subheader("🔑 Вход в систему")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="example@mail.com")
        password = st.text_input("🔒 Пароль", type="password", placeholder="Введите пароль")
        submit = st.form_submit_button("🚀 Войти", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("❌ Заполните все поля!")
                return
            
            user = authenticate_user(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                
                # Загружаем данные пользователя
                st.session_state.cards = load_user_cards(user['id'])
                st.session_state.daily_stats = get_daily_stats(user['id'])
                st.session_state.settings.update(user.get('settings', {}))
                
                st.success("✅ Успешный вход!")
                st.rerun()
            else:
                st.error("❌ Неверный email или пароль!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_registration_form():
    """Форма регистрации"""
    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.subheader("📝 Регистрация")
    
    with st.form("registration_form"):
        name = st.text_input("👤 Имя", placeholder="Ваше имя")
        email = st.text_input("📧 Email", placeholder="example@mail.com")
        password = st.text_input("🔒 Пароль", type="password", placeholder="Минимум 6 символов")
        password_confirm = st.text_input("🔒 Подтверждение пароля", type="password", placeholder="Повторите пароль")
        submit = st.form_submit_button("✨ Зарегистрироваться", use_container_width=True, type="primary")
        
        if submit:
            if not all([name, email, password, password_confirm]):
                st.error("❌ Заполните все поля!")
                return
            
            if len(password) < 6:
                st.error("❌ Пароль должен содержать минимум 6 символов!")
                return
            
            if password != password_confirm:
                st.error("❌ Пароли не совпадают!")
                return
            
            if "@" not in email or "." not in email:
                st.error("❌ Введите корректный email!")
                return
            
            if create_user(email, password, name):
                st.success("✅ Регистрация успешна! Теперь войдите в систему.")
            else:
                st.error("❌ Email уже используется или произошла ошибка!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    """Основное приложение"""
    user = st.session_state.user
    
    # Заголовок
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption(f"Добро пожаловать, {user['name']}! Система интервального повторения")
    
    # Боковая панель
    with st.sidebar:
        show_user_panel()
        show_sidebar_content()
    
    # Основной интерфейс
    show_learning_interface()

def show_user_panel():
    """Панель пользователя"""
    user = st.session_state.user
    
    st.markdown(f"""
    <div class="user-panel">
        <strong>👤 {user['name']}</strong><br>
        <small>{user['email']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Сохранить", use_container_width=True):
            save_all_data()
            st.success("✅ Данные сохранены!")
    
    with col2:
        if st.button("🚪 Выйти", use_container_width=True):
            logout()

def show_sidebar_content():
    """Содержимое боковой панели"""
    st.markdown("---")
    
    # Настройки
    st.subheader("⚙️ Настройки")
    
    # Сохраняем текущие настройки
    current_settings = st.session_state.settings.copy()
    
    # Выбор времен
    tense_options = {
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto'
    }
    
    new_selected_tenses = []
    for tense_key, tense_name in tense_options.items():
        if st.checkbox(tense_name, value=tense_key in st.session_state.settings['selected_tenses'], key=f"tense_{tense_key}"):
            new_selected_tenses.append(tense_key)
    
    new_selected_tenses = new_selected_tenses or ['presente']
    
    # Лимиты
    new_cards_per_day = st.slider(
        "Новых карточек в день", 1, 50, st.session_state.settings['new_cards_per_day']
    )
    
    # Кнопка применения настроек
    settings_changed = (
        current_settings['selected_tenses'] != new_selected_tenses or
        current_settings['new_cards_per_day'] != new_cards_per_day
    )
    
    if settings_changed:
        if st.button("✅ Применить", use_container_width=True, type="primary"):
            st.session_state.settings['selected_tenses'] = new_selected_tenses
            st.session_state.settings['new_cards_per_day'] = new_cards_per_day
            
            # Сохраняем в БД
            save_user_settings(st.session_state.user['id'], st.session_state.settings)
            
            # Сбрасываем текущую карточку
            st.session_state.current_card = None
            st.session_state.is_revealed = False
            
            st.success("✅ Настройки применены!")
            st.rerun()
    
    st.markdown("---")
    
    # Статистика
    st.subheader("📊 Сегодня")
    stats = st.session_state.daily_stats
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Повторений", stats['reviews_today'])
        st.metric("Новых", stats['new_cards_today'])
    with col2:
        st.metric("Правильных", stats['correct_today'])
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

def show_learning_interface():
    """Интерфейс изучения"""
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
    """Карточка глагола"""
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
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
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
            if st.button("❌ Снова\n(< 1 мин)", key="again", use_container_width=True):
                process_answer(Difficulty.AGAIN)
        
        with col2:
            if st.button("😓 Сложно\n(< 10 мин)", key="hard", use_container_width=True):
                process_answer(Difficulty.HARD)
        
        with col3:
            if st.button("😊 Хорошо\n(4 дня)", key="good", use_container_width=True):
                process_answer(Difficulty.GOOD)
        
        with col4:
            if st.button("😎 Легко\n(> 4 дней)", key="easy", use_container_width=True):
                process_answer(Difficulty.EASY)
    
    # Правила спряжения
    st.markdown("---")
    st.subheader("📚 Правила спряжения")
    
    for tense in st.session_state.settings['selected_tenses']:
        if tense in GRAMMAR_RULES:
            with st.expander(f"{GRAMMAR_RULES[tense]['title']}", expanded=False):
                st.markdown(GRAMMAR_RULES[tense]['content'])

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_tense_name(tense):
    """Название времени"""
    names = {
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto'
    }
    return names.get(tense, tense)

def get_card_key(verb: str, pronoun_index: int, tense: str) -> str:
    """Ключ карточки"""
    return f"{verb}_{pronoun_index}_{tense}"

def get_or_create_card(verb: str, pronoun_index: int, tense: str) -> Card:
    """Получение или создание карточки"""
    key = get_card_key(verb, pronoun_index, tense)
    
    if key not in st.session_state.cards:
        st.session_state.cards[key] = Card(
            verb=verb,
            pronoun_index=pronoun_index,
            tense=tense
        )
    
    return st.session_state.cards[key]

def get_due_cards() -> List[Card]:
    """Карточки для повторения"""
    today = datetime.date.today().isoformat()
    
    due_cards = []
    for card in st.session_state.cards.values():
        if (card.next_review_date <= today and 
            card.tense in st.session_state.settings['selected_tenses']):
            due_cards.append(card)
    
    return sorted(due_cards, key=lambda x: x.next_review_date)

def get_new_cards() -> List[Tuple[str, int, str]]:
    """Новые карточки"""
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
    """Следующая карточка"""
    # Сначала карточки для повторения
    due_cards = get_due_cards()
    if due_cards:
        return due_cards[0]
    
    # Затем новые карточки
    stats = st.session_state.daily_stats
    if stats['new_cards_today'] < st.session_state.settings['new_cards_per_day']:
        new_cards = get_new_cards()
        if new_cards:
            verb, pronoun_index, tense = new_cards[0]
            return get_or_create_card(verb, pronoun_index, tense)
    
    return None

def process_answer(difficulty: Difficulty):
    """Обработка ответа"""
    if not st.session_state.current_card:
        return
    
    card = st.session_state.current_card
    is_new_card = card.total_reviews == 0
    
    # Обновляем карточку с помощью SRS
    updated_card = SRSManager.update_card(card, difficulty)
    card_key = get_card_key(updated_card.verb, updated_card.pronoun_index, updated_card.tense)
    st.session_state.cards[card_key] = updated_card
    
    # Сохраняем в БД
    save_card(st.session_state.user['id'], updated_card)
    
    # Обновляем статистику
    reviews_increment = 1
    correct_increment = 1 if difficulty in [Difficulty.GOOD, Difficulty.EASY] else 0
    new_cards_increment = 1 if is_new_card else 0
    
    st.session_state.daily_stats['reviews_today'] += reviews_increment
    st.session_state.daily_stats['correct_today'] += correct_increment
    st.session_state.daily_stats['new_cards_today'] += new_cards_increment
    
    # Сохраняем статистику в БД
    update_daily_stats(
        st.session_state.user['id'], 
        reviews_increment, 
        correct_increment, 
        new_cards_increment
    )
    
    # Переходим к следующей карточке
    next_card()

def next_card():
    """Следующая карточка"""
    st.session_state.current_card = None
    st.session_state.is_revealed = False
    st.rerun()

def force_new_card():
    """Принудительная новая карточка"""
    new_cards = get_new_cards()
    if new_cards:
        verb, pronoun_index, tense = random.choice(new_cards)
        st.session_state.current_card = get_or_create_card(verb, pronoun_index, tense)
        st.session_state.is_revealed = False
        st.rerun()

def save_all_data():
    """Сохранение всех данных"""
    user_id = st.session_state.user['id']
    
    # Сохраняем все карточки
    for card in st.session_state.cards.values():
        save_card(user_id, card)
    
    # Сохраняем настройки
    save_user_settings(user_id, st.session_state.settings)

def logout():
    """Выход из системы"""
    # Сохраняем данные перед выходом
    save_all_data()
    
    # Очищаем session state
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.cards = {}
    st.session_state.current_card = None
    st.session_state.is_revealed = False
    st.session_state.daily_stats = {
        'reviews_today': 0,
        'correct_today': 0,
        'new_cards_today': 0
    }
    st.session_state.settings = {
        'new_cards_per_day': 10,
        'selected_tenses': ['presente']
    }
    
    st.success("👋 Данные сохранены. До свидания!")
    st.rerun()

if __name__ == "__main__":
    main()
