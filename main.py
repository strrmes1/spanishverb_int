# main.py - Главная страница выбора языка изучения

import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import datetime
import time
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Конфигурация
st.set_page_config(
    page_title="Verb Trainer - Learn Spanish & Catalan",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://your-app.herokuapp.com')

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# CSS стили для главной страницы
st.markdown("""
<style>
    .main > div {
        max-width: 1200px;
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #ff6b6b 100%);
        min-height: 100vh;
    }
    
    .main-container {
        padding: 2rem;
        color: white;
    }
    
    .header-section {
        text-align: center;
        margin-bottom: 3rem;
        opacity: 0;
        animation: fadeInUp 1s ease-out 0.2s forwards;
    }
    
    .app-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
    }
    
    .app-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .app-description {
        font-size: 1.1rem;
        opacity: 0.8;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .language-choice {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin: 3rem 0;
        opacity: 0;
        animation: fadeInUp 1s ease-out 0.4s forwards;
    }
    
    .language-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 2rem;
        padding: 3rem 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        width: 300px;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .language-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    .language-card.spanish {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(220, 53, 69, 0.2));
    }
    
    .language-card.catalan {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(254, 202, 87, 0.2));
    }
    
    .flag {
        font-size: 5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .language-name {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .language-description {
        font-size: 1.1rem;
        opacity: 0.8;
        line-height: 1.5;
        margin-bottom: 1.5rem;
    }
    
    .verb-count {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 1rem;
    }
    
    .features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 3rem;
        opacity: 0;
        animation: fadeInUp 1s ease-out 0.6s forwards;
    }
    
    .feature {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 1.5rem;
        padding: 2rem;
        text-align: center;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        opacity: 0.8;
        line-height: 1.5;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Мобильная адаптация */
    @media (max-width: 768px) {
        .language-choice {
            flex-direction: column;
            align-items: center;
        }
        
        .language-card {
            width: 100%;
            max-width: 300px;
            height: 350px;
        }
        
        .app-title {
            font-size: 2.5rem;
        }
        
        .app-subtitle {
            font-size: 1.2rem;
        }
        
        .features {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Инициализация session state"""
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'interface_language' not in st.session_state:
        st.session_state.interface_language = 'en'
    if 'learning_language' not in st.session_state:
        st.session_state.learning_language = None  # 'spanish' или 'catalan'
    if 'page' not in st.session_state:
        st.session_state.page = 'language_selection'

def show_language_selector():
    """Показывает селектор языка интерфейса"""
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        interface_lang = st.selectbox(
            "Interface Language",
            options=['en', 'ru'],
            format_func=lambda x: '🇺🇸 English' if x == 'en' else '🇷🇺 Русский',
            index=0 if st.session_state.interface_language == 'en' else 1,
            key="interface_language_selector"
        )
        if interface_lang != st.session_state.interface_language:
            st.session_state.interface_language = interface_lang
            st.rerun()

def get_text(key: str) -> str:
    """Получить текст на выбранном языке интерфейса"""
    translations = {
        'en': {
            'app_title': 'Verb Trainer',
            'app_subtitle': 'Master verb conjugations with spaced repetition',
            'app_description': 'Learn Spanish and Catalan verbs effectively using the proven SM-2 algorithm. Our intelligent system shows you cards exactly when you\'re about to forget them, maximizing your learning efficiency.',
            'spanish_title': 'Spanish',
            'spanish_description': 'Learn the most important Spanish verbs with comprehensive conjugations across all major tenses.',
            'spanish_verbs': '100+ verbs',
            'catalan_title': 'Català',
            'catalan_description': 'Master Catalan verb conjugations with our specialized trainer designed for this beautiful Romance language.',
            'catalan_verbs': '30+ verbs',
            'smart_repetition': '🧠 Smart Repetition',
            'smart_repetition_desc': 'Our SM-2 algorithm shows cards exactly when you\'re about to forget them',
            'detailed_stats': '📊 Detailed Statistics',
            'detailed_stats_desc': 'Track your progress with comprehensive analytics for each verb and tense',
            'efficient_learning': '⏱️ Efficient Learning',
            'efficient_learning_desc': 'Study just 15-20 minutes daily for maximum retention and progress',
            'login_google': '🔐 Login with Google',
            'continue_without_login': '📚 Continue without login'
        },
        'ru': {
            'app_title': 'Тренажер глаголов',
            'app_subtitle': 'Изучайте спряжения с системой интервального повторения',
            'app_description': 'Эффективно изучайте испанские и каталанские глаголы с помощью проверенного алгоритма SM-2. Наша интеллектуальная система показывает карточки именно тогда, когда вы готовы их забыть, максимизируя эффективность обучения.',
            'spanish_title': 'Испанский',
            'spanish_description': 'Изучите важнейшие испанские глаголы с полными спряжениями во всех основных временах.',
            'spanish_verbs': '100+ глаголов',
            'catalan_title': 'Каталанский',
            'catalan_description': 'Освойте спряжения каталанских глаголов с нашим специализированным тренажером для этого прекрасного романского языка.',
            'catalan_verbs': '30+ глаголов',
            'smart_repetition': '🧠 Умное повторение',
            'smart_repetition_desc': 'Алгоритм SM-2 показывает карточки именно тогда, когда вы готовы их забыть',
            'detailed_stats': '📊 Детальная статистика',
            'detailed_stats_desc': 'Отслеживайте прогресс с подробной аналитикой для каждого глагола и времени',
            'efficient_learning': '⏱️ Эффективное обучение',
            'efficient_learning_desc': 'Изучайте всего 15-20 минут в день для максимального запоминания и прогресса',
            'login_google': '🔐 Войти через Google',
            'continue_without_login': '📚 Продолжить без входа'
        }
    }
    
    return translations.get(st.session_state.interface_language, {}).get(key, key)

def show_language_selection_page():
    """Показывает страницу выбора языка изучения"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Селектор языка интерфейса
    show_language_selector()
    
    # Заголовок
    st.markdown(f'''
    <div class="header-section">
        <h1 class="app-title">{get_text('app_title')}</h1>
        <p class="app-subtitle">{get_text('app_subtitle')}</p>
        <p class="app-description">{get_text('app_description')}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Выбор языка изучения
    st.markdown('<div class="language-choice">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
        <div class="language-card spanish">
            <span class="flag">🇪🇸</span>
            <h2 class="language-name">{get_text('spanish_title')}</h2>
            <p class="language-description">{get_text('spanish_description')}</p>
            <div class="verb-count">{get_text('spanish_verbs')}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("🇪🇸 " + get_text('spanish_title'), key="spanish_btn", use_container_width=True, type="primary"):
            st.session_state.learning_language = 'spanish'
            st.session_state.page = 'auth_choice'
            st.rerun()
    
    with col2:
        st.markdown(f'''
        <div class="language-card catalan">
            <span class="flag">🏴󠁥󠁳󠁣󠁴󠁿</span>
            <h2 class="language-name">{get_text('catalan_title')}</h2>
            <p class="language-description">{get_text('catalan_description')}</p>
            <div class="verb-count">{get_text('catalan_verbs')}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("🏴󠁥󠁳󠁣󠁴󠁿 " + get_text('catalan_title'), key="catalan_btn", use_container_width=True, type="primary"):
            st.session_state.learning_language = 'catalan'
            st.session_state.page = 'auth_choice'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Преимущества
    st.markdown('<div class="features">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="feature">
            <div class="feature-icon">🧠</div>
            <h3 class="feature-title">{get_text('smart_repetition')}</h3>
            <p class="feature-description">{get_text('smart_repetition_desc')}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="feature">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">{get_text('detailed_stats')}</h3>
            <p class="feature-description">{get_text('detailed_stats_desc')}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="feature">
            <div class="feature-icon">⏱️</div>
            <h3 class="feature-title">{get_text('efficient_learning')}</h3>
            <p class="feature-description">{get_text('efficient_learning_desc')}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_auth_choice_page():
    """Показывает страницу выбора входа"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Кнопка назад
    if st.button("← Назад", key="back_btn"):
        st.session_state.page = 'language_selection'
        st.rerun()
    
    language_flag = "🇪🇸" if st.session_state.learning_language == 'spanish' else "🏴󠁥󠁳󠁣󠁴󠁿"
    language_name = get_text('spanish_title') if st.session_state.learning_language == 'spanish' else get_text('catalan_title')
    
    st.markdown(f'''
    <div class="header-section">
        <h1 class="app-title">{language_flag} {language_name}</h1>
        <p class="app-subtitle">Выберите способ входа</p>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Вход через Google
        if st.button(get_text('login_google'), key="login_google_btn", use_container_width=True, type="primary"):
            start_oauth_flow()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Продолжить без входа
        if st.button(get_text('continue_without_login'), key="continue_without_login_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.page = 'trainer'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)

def handle_oauth_callback(query_params):
    """Обрабатывает OAuth callback"""
    code = query_params.get('code')
    state = query_params.get('state')
    error = query_params.get('error')
    
    if error:
        st.error(f"❌ OAuth Error: {error}")
        return
    
    if not code or not state:
        st.error("❌ Missing authorization parameters")
        return
    
    # Обрабатываем код
    with st.spinner("🔄 Обрабатываем авторизацию..."):
        success = process_authorization_code(code)
        
        if success:
            st.session_state.page = 'trainer'
            st.success("🎉 Авторизация завершена успешно!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Ошибка при получении токена")

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

def show_trainer_page():
    """Показывает тренажер"""
    if st.session_state.learning_language == 'spanish':
        # Импортируем и запускаем испанский тренажер
        import spanish_trainer
        spanish_trainer.show_trainer()
    else:
        # Импортируем и запускаем каталанский тренажер
        import catalan_trainer
        catalan_trainer.show_trainer()

def main():
    """Главная функция"""
    init_session_state()
    
    # Обрабатываем OAuth callback
    query_params = dict(st.query_params)
    
    if 'code' in query_params and 'state' in query_params:
        handle_oauth_callback(query_params)
        return
    
    # Маршрутизация страниц
    if st.session_state.page == 'language_selection':
        show_language_selection_page()
    elif st.session_state.page == 'auth_choice':
        show_auth_choice_page()
    elif st.session_state.page == 'trainer':
        show_trainer_page()
    else:
        show_language_selection_page()

if __name__ == "__main__":
    main()
