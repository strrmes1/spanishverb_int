import streamlit as st
import random
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
import time

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
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://your-app.railway.app/auth/callback')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

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

# Google OAuth класс
class GoogleAuth:
    @staticmethod
    def get_auth_url() -> str:
        """Генерирует URL для авторизации через Google"""
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
    'hablar': {'translation': 'говорить', 'type': 'regular-ar'},
    'vivir': {'translation': 'жить', 'type': 'regular-ir'},
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
}

def init_session_state():
    """Инициализация состояния сессии"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    
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

def show_user_panel():
    """Показывает панель пользователя в сайдбаре"""
    if not st.session_state.authenticated:
        return
    
    user_info = st.session_state.user_info
    
    st.markdown(f"""
    <div class="user-info">
        <strong>👤 {user_info.get('name', 'Пользователь')}</strong><br>
        <small>{user_info.get('email', '')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col2:
        if st.button("🚪 Выйти", key="logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.access_token = None
            st.rerun()

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

def get_next_card() -> Optional[Card]:
    """Получает следующую карточку для изучения"""
    # Простая логика для демо - берем случайный глагол
    verb = random.choice(list(VERBS.keys()))
    pronoun_index = random.randint(0, 5)
    tense = 'presente'
    
    return get_or_create_card(verb, pronoun_index, tense)

def main():
    init_session_state()
    
    # ИСПРАВЛЕНО: Используем новый API Streamlit
    query_params = st.query_params
    
    # Отладочная информация
    if query_params:
        st.write("🔍 **Отладка - получены параметры:**")
        st.write(dict(query_params))
        
        if 'code' in query_params:
            st.write("✅ Найден код авторизации!")
            
            try:
                code = query_params['code']
                state = query_params.get('state', '')
                
                st.write(f"📝 Code: {code[:20]}...")
                st.write(f"📝 State: {state[:20]}...")
                
                # Проверяем переменные окружения
                st.write("🔧 **Проверка конфигурации:**")
                st.write(f"CLIENT_ID: {'✅ Настроен' if GOOGLE_CLIENT_ID else '❌ НЕ НАСТРОЕН'}")
                st.write(f"CLIENT_SECRET: {'✅ Настроен' if GOOGLE_CLIENT_SECRET else '❌ НЕ НАСТРОЕН'}")
                st.write(f"REDIRECT_URI: {REDIRECT_URI}")
                
                if st.button("🔄 Обработать авторизацию"):
                    with st.spinner("Обрабатываем авторизацию..."):
                        st.write("1️⃣ Обмениваем code на токен...")
                        
                        token_response = GoogleAuth.exchange_code_for_token(code)
                        
                        if token_response and 'access_token' in token_response:
                            st.write("✅ Токен получен!")
                            access_token = token_response['access_token']
                            
                            st.write("2️⃣ Получаем информацию о пользователе...")
                            user_info = GoogleAuth.get_user_info(access_token)
                            
                            if user_info:
                                st.write("✅ Данные пользователя получены!")
                                st.write(f"👤 Имя: {user_info.get('name')}")
                                st.write(f"📧 Email: {user_info.get('email')}")
                                
                                # Сохраняем в session state
                                st.session_state.authenticated = True
                                st.session_state.user_info = user_info
                                st.session_state.access_token = access_token
                                
                                st.success("🎉 Авторизация успешна!")
                                
                                if st.button("🚀 Перейти к приложению"):
                                    # ИСПРАВЛЕНО: Очищаем параметры современным способом
                                    st.query_params.clear()
                                    st.rerun()
                            else:
                                st.error("❌ Ошибка получения данных пользователя")
                        else:
                            st.error("❌ Ошибка получения токена")
                
                if st.button("🧹 Очистить URL и начать заново"):
                    st.query_params.clear()
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Ошибка обработки параметров: {e}")
        
        st.markdown("---")
        if st.button("🏠 Вернуться на главную"):
            st.query_params.clear()
            st.rerun()
            
        return
    
    # Если не авторизован, показываем страницу входа
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Основное приложение для авторизованных пользователей
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption("Система интервального повторения для эффективного изучения")
    
    # Боковая панель
    with st.sidebar:
        show_user_panel()
        
        st.markdown("---")
        st.header("⚙️ Настройки")
        
        st.subheader("📊 Статистика")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Повторений", st.session_state.daily_stats['reviews_today'])
        with col2:
            st.metric("Правильных", st.session_state.daily_stats['correct_today'])
    
    # Простая проверка что авторизация работает
    if st.session_state.user_info:
        st.success(f"👋 Добро пожаловать, {st.session_state.user_info.get('name')}!")
        
        # Демо карточка
        if not st.session_state.current_card:
            st.session_state.current_card = get_next_card()
        
        card = st.session_state.current_card
        
        if card and card.verb in VERBS and card.verb in CONJUGATIONS['presente']:
            verb_info = VERBS[card.verb]
            
            st.markdown(f"""
            <div class="card-container">
                <div class="verb-title">{card.verb}</div>
                <div class="verb-translation">{verb_info['translation']}</div>
                <div class="pronoun-display">
                    {PRONOUNS[card.pronoun_index]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.is_revealed:
                if st.button("🔍 Показать ответ", type="primary", use_container_width=True):
                    st.session_state.is_revealed = True
                    st.rerun()
            else:
                conjugation = CONJUGATIONS['presente'][card.verb][card.pronoun_index]
                
                st.markdown(f"""
                <div class="answer-display">
                    ✅ {conjugation}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("➡️ Следующий глагол", use_container_width=True):
                    st.session_state.current_card = get_next_card()
                    st.session_state.is_revealed = False
                    st.rerun()

if __name__ == "__main__":
    main()
