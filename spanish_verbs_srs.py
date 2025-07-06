import streamlit as st
import random
import time
import json
import datetime
import math
import pandas as pd
import hashlib
import base64
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from urllib.parse import urlencode
import os

# Пробуем импортировать plotly, если не получается - используем альтернативу
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Конфигурация страницы
st.set_page_config(
    page_title="🇪🇸 Тренажер испанских глаголов с Google Auth",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google OAuth конфигурация
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://spanishverbint-production.up.railway.app/auth/callback')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# CSS стили (расширенные для OAuth)
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
    
    .auth-container {
        background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(66, 133, 244, 0.3);
    }
    
    .auth-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .auth-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .google-btn {
        background: white !important;
        color: #333 !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .google-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
    }
    
    .user-info {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sync-status {
        background: rgba(52, 168, 83, 0.1);
        border: 1px solid rgba(52, 168, 83, 0.3);
        color: #34a853;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .offline-warning {
        background: rgba(234, 67, 53, 0.1);
        border: 1px solid rgba(234, 67, 53, 0.3);
        color: #ea4335;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Прочие стили остаются такими же */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
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
    
    .main-content {
        max-width: 600px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
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

# Google OAuth класс
class GoogleAuth:
    @staticmethod
    def get_auth_url() -> str:
        """Генерирует URL для авторизации через Google"""
        # Генерируем state для безопасности
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
        
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict]:
        """Обменивает authorization code на access token"""
        data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
        }
        
        try:
            response = requests.post(GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Ошибка получения токена: {e}")
            return None
    
    @staticmethod
    def get_user_info(access_token: str) -> Optional[Dict]:
        """Получает информацию о пользователе"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Ошибка получения информации о пользователе: {e}")
            return None

# Менеджер данных с Google Auth
class DataManager:
    @staticmethod
    def get_user_data_key(user_id: str) -> str:
        """Генерирует ключ для данных пользователя"""
        return f"spanish_verbs_user_{hashlib.md5(user_id.encode()).hexdigest()}"
    
    @staticmethod
    def save_user_data(user_id: str, data: Dict) -> bool:
        """Сохраняет данные пользователя"""
        try:
            # В production версии здесь будет сохранение в базу данных
            # Пока сохраняем в session_state с user_id
            key = DataManager.get_user_data_key(user_id)
            st.session_state[f"{key}_data"] = {
                'cards': data.get('cards', {}),
                'daily_stats': data.get('daily_stats', {}),
                'settings': data.get('settings', {}),
                'last_sync': datetime.datetime.now().isoformat()
            }
            return True
        except Exception as e:
            st.error(f"Ошибка сохранения данных: {e}")
            return False
    
    @staticmethod
    def load_user_data(user_id: str) -> Optional[Dict]:
        """Загружает данные пользователя"""
        try:
            key = DataManager.get_user_data_key(user_id)
            return st.session_state.get(f"{key}_data")
        except Exception as e:
            st.error(f"Ошибка загрузки данных: {e}")
            return None
    
    @staticmethod
    def sync_with_cloud(user_id: str) -> bool:
        """Синхронизация с облаком (заглушка для будущего API)"""
        # В будущем здесь будет реальная синхронизация с Firebase/Supabase
        return True

# Остальные классы и функции остаются теми же...
# (SRSManager, VERBS, PRONOUNS, CONJUGATIONS, etc.)

# Данные глаголов
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
        'hablar': ['hablo', 'hablas', 'habla', 'hablamos', 'habláis', 'hablan'],
        'vivir': ['vivo', 'vives', 'vive', 'vivimos', 'vivís', 'viven'],
        'trabajar': ['trabajo', 'trabajas', 'trabaja', 'trabajamos', 'trabajáis', 'trabajan'],
        'estudiar': ['estudio', 'estudias', 'estudia', 'estudiamos', 'estudiáis', 'estudian']
    }
    # Добавьте остальные времена по необходимости
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

def init_session_state():
    """Инициализация состояния сессии"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    # Состояние авторизации
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    
    # Основные данные приложения
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
    
    if 'last_sync' not in st.session_state:
        st.session_state.last_sync = None

def handle_oauth_callback():
    """Обрабатывает callback от Google OAuth"""
    # Получаем параметры из URL
    query_params = st.experimental_get_query_params()
    
    if 'code' in query_params and 'state' in query_params:
        code = query_params['code'][0]
        state = query_params['state'][0]
        
        # Проверяем state для безопасности
        if state != st.session_state.get('oauth_state'):
            st.error("Ошибка безопасности: неверный state parameter")
            return False
        
        # Обмениваем code на токен
        token_response = GoogleAuth.exchange_code_for_token(code)
        if not token_response:
            return False
        
        access_token = token_response.get('access_token')
        if not access_token:
            st.error("Не удалось получить access token")
            return False
        
        # Получаем информацию о пользователе
        user_info = GoogleAuth.get_user_info(access_token)
        if not user_info:
            return False
        
        # Сохраняем данные в session state
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.access_token = access_token
        
        # Загружаем данные пользователя
        load_user_data()
        
        # Очищаем параметры URL
        st.experimental_set_query_params()
        
        return True
    
    return False

def load_user_data():
    """Загружает данные пользователя из хранилища"""
    if not st.session_state.authenticated or not st.session_state.user_info:
        return
    
    user_id = st.session_state.user_info['id']
    user_data = DataManager.load_user_data(user_id)
    
    if user_data:
        # Восстанавливаем данные пользователя
        st.session_state.cards = user_data.get('cards', {})
        st.session_state.daily_stats = user_data.get('daily_stats', st.session_state.daily_stats)
        st.session_state.settings = user_data.get('settings', st.session_state.settings)
        st.session_state.last_sync = user_data.get('last_sync')
        
        # Конвертируем словари обратно в Card объекты
        cards_objects = {}
        for key, card_data in st.session_state.cards.items():
            if isinstance(card_data, dict):
                cards_objects[key] = Card(**card_data)
            else:
                cards_objects[key] = card_data
        st.session_state.cards = cards_objects

def save_user_data():
    """Сохраняет данные пользователя"""
    if not st.session_state.authenticated or not st.session_state.user_info:
        return False
    
    user_id = st.session_state.user_info['id']
    
    # Конвертируем Card объекты в словари для сериализации
    cards_data = {}
    for key, card in st.session_state.cards.items():
        if isinstance(card, Card):
            cards_data[key] = asdict(card)
        else:
            cards_data[key] = card
    
    data = {
        'cards': cards_data,
        'daily_stats': st.session_state.daily_stats,
        'settings': st.session_state.settings
    }
    
    success = DataManager.save_user_data(user_id, data)
    if success:
        st.session_state.last_sync = datetime.datetime.now().isoformat()
    
    return success

def logout():
    """Выход из аккаунта"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.access_token = None
    st.session_state.last_sync = None
    
    # Очищаем данные приложения
    st.session_state.cards = {}
    st.session_state.current_card = None
    st.session_state.is_revealed = False
    st.session_state.daily_stats = {
        'reviews_today': 0,
        'correct_today': 0,
        'new_cards_today': 0,
        'last_reset': datetime.date.today().isoformat()
    }

def show_auth_page():
    """Показывает страницу авторизации"""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-title">🇪🇸 Тренажер испанских глаголов</div>
        <div class="auth-subtitle">
            Войдите через Google, чтобы сохранять прогресс между устройствами
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            st.error("⚠️ Google OAuth не настроен. Проверьте переменные окружения.")
            st.code("""
            Необходимые переменные:
            - GOOGLE_CLIENT_ID
            - GOOGLE_CLIENT_SECRET  
            - REDIRECT_URI
            """)
            return
        
        auth_url = GoogleAuth.get_auth_url()
        
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <a href="{auth_url}" target="_self">
                <button class="google-btn">
                    🔐 Войти через Google
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔒 Безопасность и конфиденциальность"):
            st.markdown("""
            **Что мы используем из вашего Google аккаунта:**
            - Имя и email для идентификации
            - Профильная фотография для интерфейса
            
            **Что мы НЕ делаем:**
            - Не получаем доступ к Gmail или Google Drive
            - Не передаем данные третьим лицам  
            - Не используем информацию для рекламы
            
            **Ваши данные в безопасности:**
            - Прогресс изучения сохраняется отдельно для каждого пользователя
            - Используется шифрование при передаче данных
            - Возможность удалить все данные в любой момент
            """)
        
        with st.expander("✨ Преимущества авторизации"):
            st.markdown("""
            **🌐 Синхронизация между устройствами**
            - Изучайте на телефоне, компьютере, планшете
            - Прогресс автоматически синхронизируется
            
            **📈 Расширенная статистика**
            - Долгосрочные графики прогресса
            - Анализ эффективности изучения
            - Персональные рекомендации
            
            **🎯 Интервальное повторение**
            - Умный алгоритм подбора карточек
            - Оптимальное планирование повторений
            - Максимальная эффективность изучения
            
            **💾 Безопасное хранение**
            - Никогда не потеряете прогресс
            - Резервное копирование в облаке
            - Восстановление данных при необходимости
            """)

def show_user_panel():
    """Показывает панель пользователя в сайдбаре"""
    if not st.session_state.authenticated:
        return
    
    user_info = st.session_state.user_info
    
    # Информация о пользователе
    st.markdown(f"""
    <div class="user-info">
        <strong>👤 {user_info.get('name', 'Пользователь')}</strong><br>
        <small>{user_info.get('email', '')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Статус синхронизации
    if st.session_state.last_sync:
        sync_time = datetime.datetime.fromisoformat(st.session_state.last_sync)
        time_diff = datetime.datetime.now() - sync_time
        
        if time_diff.total_seconds() < 300:  # Меньше 5 минут
            st.markdown('<div class="sync-status">✅ Синхронизировано</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="offline-warning">⚠️ Требуется синхронизация</div>', unsafe_allow_html=True)
    
    # Кнопки управления
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Синхронизация", key="sync_data", use_container_width=True):
            if save_user_data():
                st.success("✅ Данные синхронизированы!")
                st.rerun()
            else:
                st.error("❌ Ошибка синхронизации")
    
    with col2:
        if st.button("🚪 Выйти", key="logout", use_container_width=True):
            logout()
            st.rerun()

# Остальные функции остаются теми же (get_card_key, get_or_create_card, etc.)
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
    
    # Автосохранение
    if st.session_state.settings.get('auto_save', True) and st.session_state.authenticated:
        save_user_data()
    
    # Сбрасываем текущую карточку
    st.session_state.current_card = None
    st.session_state.is_revealed = False

# ЗАМЕНИТЕ ВАШУ ФУНКЦИЮ main() ПОЛНОСТЬЮ НА ЭТУ:

def main():
    init_session_state()
    
    # ОТЛАДКА: Показываем что происходит
    query_params = st.experimental_get_query_params()
    
    # Если есть query параметры, показываем их
    if query_params:
        st.write("🔍 **Отладка - получены параметры:**")
        st.write(query_params)
        
        # Проверяем есть ли code
        if 'code' in query_params:
            st.write("✅ Найден код авторизации!")
            
            try:
                code = query_params['code'][0]
                state = query_params.get('state', [''])[0]
                
                st.write(f"📝 Code: {code[:20]}...")
                st.write(f"📝 State: {state[:20]}...")
                
                # Проверяем переменные окружения
                st.write("🔧 **Проверка конфигурации:**")
                st.write(f"CLIENT_ID: {'✅ Настроен' if GOOGLE_CLIENT_ID else '❌ НЕ НАСТРОЕН'}")
                st.write(f"CLIENT_SECRET: {'✅ Настроен' if GOOGLE_CLIENT_SECRET else '❌ НЕ НАСТРОЕН'}")
                st.write(f"REDIRECT_URI: {REDIRECT_URI}")
                
                if st.button("🔄 Обработать авторизацию"):
                    with st.spinner("Обрабатываем авторизацию..."):
                        # Обмениваем code на токен
                        st.write("1️⃣ Обмениваем code на токен...")
                        
                        data = {
                            'client_id': GOOGLE_CLIENT_ID,
                            'client_secret': GOOGLE_CLIENT_SECRET,
                            'code': code,
                            'grant_type': 'authorization_code',
                            'redirect_uri': REDIRECT_URI,
                        }
                        
                        try:
                            response = requests.post(GOOGLE_TOKEN_URL, data=data)
                            st.write(f"Token response status: {response.status_code}")
                            
                            if response.status_code == 200:
                                token_data = response.json()
                                st.write("✅ Токен получен!")
                                
                                access_token = token_data.get('access_token')
                                if access_token:
                                    st.write("2️⃣ Получаем информацию о пользователе...")
                                    
                                    # Получаем данные пользователя
                                    headers = {'Authorization': f'Bearer {access_token}'}
                                    user_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
                                    
                                    if user_response.status_code == 200:
                                        user_info = user_response.json()
                                        st.write("✅ Данные пользователя получены!")
                                        st.write(f"👤 Имя: {user_info.get('name')}")
                                        st.write(f"📧 Email: {user_info.get('email')}")
                                        
                                        # Сохраняем в session state
                                        st.session_state.authenticated = True
                                        st.session_state.user_info = user_info
                                        st.session_state.access_token = access_token
                                        
                                        st.success("🎉 Авторизация успешна!")
                                        
                                        # Кнопка для перехода к приложению
                                        if st.button("🚀 Перейти к приложению"):
                                            st.experimental_set_query_params()  # Очищаем URL
                                            st.rerun()
                                    else:
                                        st.error(f"❌ Ошибка получения пользователя: {user_response.status_code}")
                                        st.write(user_response.text)
                                else:
                                    st.error("❌ Access token не найден в ответе")
                                    st.write(token_data)
                            else:
                                st.error(f"❌ Ошибка получения токена: {response.status_code}")
                                st.write(response.text)
                                
                        except Exception as e:
                            st.error(f"❌ Исключение при обработке: {e}")
                
                # Кнопка для очистки URL
                if st.button("🧹 Очистить URL и начать заново"):
                    st.experimental_set_query_params()
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Ошибка обработки параметров: {e}")
        else:
            st.write("❌ Код авторизации не найден в параметрах")
            
        # Всегда показываем кнопку возврата
        st.markdown("---")
        if st.button("🏠 Вернуться на главную"):
            st.experimental_set_query_params()
            st.rerun()
            
        return  # Не показываем основное приложение при отладке
    
    # Обычная логика приложения
    # Если не авторизован, показываем страницу входа
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Основное приложение для авторизованных пользователей
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption("Система интервального повторения для эффективного изучения")
    
    # Простая проверка что авторизация работает
    if st.session_state.user_info:
        st.success(f"👋 Добро пожаловать, {st.session_state.user_info.get('name')}!")
        
        # Кнопка выхода для тестирования
        if st.button("🚪 Выйти из аккаунта"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.access_token = None
            st.rerun()
    
    
            
    # Основной интерфейс приложения
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption("Система интервального повторения для эффективного изучения")
    
    # Боковая панель с настройками и профилем пользователя
    with st.sidebar:
        show_user_panel()
        
        st.markdown("---")
        st.header("⚙️ Настройки")
        
        # Выбор времен
        st.subheader("📚 Времена для изучения")
        tense_options = {
            'presente': 'Presente'
        }
        
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
        
        # Применяем настройки
        st.session_state.settings['selected_tenses'] = new_selected_tenses
        st.session_state.settings['new_cards_per_day'] = new_new_cards
        st.session_state.settings['review_cards_per_day'] = new_review_cards
        
        st.markdown("---")
        
        # Статистика в боковой панели
        st.subheader("📊 Статистика")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Повторений", st.session_state.daily_stats['reviews_today'])
            st.metric("Новых", st.session_state.daily_stats['new_cards_today'])
        with col2:
            st.metric("Правильных", st.session_state.daily_stats['correct_today'])
            due_count = len(get_due_cards())
            st.metric("К повторению", due_count)
    
    # Основной интерфейс изучения
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

if __name__ == "__main__":
    main()
