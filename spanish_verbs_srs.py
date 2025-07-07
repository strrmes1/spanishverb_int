import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import datetime
import time

# Конфигурация
st.set_page_config(page_title="🇪🇸 Spanish Verbs Trainer", page_icon="🇪🇸", layout="wide")

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://spanishverbint-production.up.railway.app')

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Данные для демо тренажера
DEMO_VERBS = {
    'ser': {'translation': 'быть, являться'},
    'estar': {'translation': 'находиться, быть'},
    'tener': {'translation': 'иметь'},
    'hacer': {'translation': 'делать'},
    'ir': {'translation': 'идти, ехать'},
    'ver': {'translation': 'видеть'},
    'dar': {'translation': 'давать'},
    'saber': {'translation': 'знать'},
    'querer': {'translation': 'хотеть, любить'},
    'hablar': {'translation': 'говорить'},
}

DEMO_CONJUGATIONS = {
    'ser': ['soy', 'eres', 'es', 'somos', 'sois', 'son'],
    'estar': ['estoy', 'estás', 'está', 'estamos', 'estáis', 'están'],
    'tener': ['tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen'],
    'hacer': ['hago', 'haces', 'hace', 'hacemos', 'hacéis', 'hacen'],
    'ir': ['voy', 'vas', 'va', 'vamos', 'vais', 'van'],
    'ver': ['veo', 'ves', 've', 'vemos', 'veis', 'ven'],
    'dar': ['doy', 'das', 'da', 'damos', 'dais', 'dan'],
    'saber': ['sé', 'sabes', 'sabe', 'sabemos', 'sabéis', 'saben'],
    'querer': ['quiero', 'quieres', 'quiere', 'queremos', 'queréis', 'quieren'],
    'hablar': ['hablo', 'hablas', 'habla', 'hablamos', 'habláis', 'hablan'],
}

PRONOUNS = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']

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
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'current_verb' not in st.session_state:
        st.session_state.current_verb = None
    if 'current_pronoun' not in st.session_state:
        st.session_state.current_pronoun = 0
    if 'is_revealed' not in st.session_state:
        st.session_state.is_revealed = False
    if 'score' not in st.session_state:
        st.session_state.score = {'correct': 0, 'total': 0}

def handle_oauth_callback(query_params):
    """Обрабатывает OAuth callback"""
    st.title("🔄 Обрабатываем авторизацию...")
    
    code = query_params.get('code')
    state = query_params.get('state')
    error = query_params.get('error')
    
    # Проверяем ошибки
    if error:
        st.error(f"❌ OAuth Error: {error}")
        if st.button("🔄 Попробовать снова"):
            clear_oauth_and_reload()
        return
    
    # Проверяем код и state
    if not code:
        st.error("❌ Authorization code missing")
        return
    
    if not state or state != st.session_state.oauth_state:
        st.error("❌ Security validation failed")
        st.write("Это может произойти если:")
        st.write("- Страница была перезагружена")
        st.write("- Авторизация заняла слишком много времени")
        st.write("- Открыто несколько вкладок")
        
        if st.button("🔄 Начать авторизацию заново"):
            clear_oauth_and_reload()
        return
    
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
            if st.button("🔄 Попробовать снова"):
                clear_oauth_and_reload()

def process_authorization_code(code):
    """Обрабатывает authorization code"""
    try:
        # Обменяем код на токен
        token_data = exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            st.error("❌ Не удалось получить токен доступа")
            return False
        
        access_token = token_data['access_token']
        
        # Получаем информацию о пользователе
        user_info = get_user_info(access_token)
        if not user_info:
            st.error("❌ Не удалось получить информацию о пользователе")
            return False
        
        # Сохраняем в session
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
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Token request failed: {response.status_code}")
        return None

def get_user_info(access_token):
    """Получает информацию о пользователе"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"User info request failed: {response.status_code}")
        return None

def show_welcome_page():
    """Показывает страницу приветствия"""
    # Красивый заголовок
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 3.5rem; color: #2d3748; margin-bottom: 1rem;">
            🇪🇸 Тренажер испанских глаголов
        </h1>
        <h3 style="color: #718096; font-weight: 400; margin-bottom: 2rem;">
            Изучайте спряжения с системой интервального повторения
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Преимущества
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1rem; margin: 1rem 0;">
            <h3>🧠 Умное повторение</h3>
            <p>Алгоритм показывает карточки именно тогда, когда вы готовы их забыть</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 1rem; margin: 1rem 0;">
            <h3>📊 Прогресс-трекинг</h3>
            <p>Детальная статистика изучения и персональные рекомендации</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 1rem; margin: 1rem 0;">
            <h3>☁️ Облачная синхронизация</h3>
            <p>Изучайте на любом устройстве, прогресс всегда с вами</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Кнопка входа
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Войти через Google", type="primary", use_container_width=True):
            start_oauth_flow()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #718096;">
            <small>
                Нужен Google аккаунт для сохранения прогресса.<br>
                Мы не получаем доступ к вашим личным данным.
            </small>
        </div>
        """, unsafe_allow_html=True)

def start_oauth_flow():
    """Запускает OAuth flow"""
    # Генерируем новый state
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    st.session_state.oauth_state = state
    
    # Параметры OAuth
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
    
    # Redirect через JavaScript
    st.components.v1.html(f"""
    <div style="text-align: center; padding: 2rem; background: #e3f2fd; border-radius: 1rem;">
        <h3>🔄 Перенаправляем в Google...</h3>
        <p>Подождите несколько секунд</p>
    </div>
    <script>
    setTimeout(function() {{
        window.location.href = '{auth_url}';
    }}, 1500);
    </script>
    """, height=150)

def show_main_app():
    """Показывает основное приложение"""
    user_info = st.session_state.user_info
    
    # Верхняя панель
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🇪🇸 Тренажер глаголов")
        st.caption(f"Добро пожаловать, {user_info.get('name')}!")
    
    with col2:
        st.metric("Правильных", st.session_state.score['correct'])
    
    with col3:
        accuracy = (st.session_state.score['correct'] / st.session_state.score['total'] * 100) if st.session_state.score['total'] > 0 else 0
        st.metric("Точность", f"{accuracy:.0f}%")
    
    # Боковая панель
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f7fafc; border-radius: 0.5rem; margin-bottom: 1rem;">
            <strong>👤 {user_info.get('name')}</strong><br>
            <small>{user_info.get('email')}</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Выйти", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.subheader("📊 Статистика")
        st.write(f"**Всего ответов:** {st.session_state.score['total']}")
        st.write(f"**Правильных:** {st.session_state.score['correct']}")
        
        if st.session_state.score['total'] > 0:
            accuracy = st.session_state.score['correct'] / st.session_state.score['total'] * 100
            st.write(f"**Точность:** {accuracy:.1f}%")
    
    # Основной интерфейс тренажера
    show_verb_trainer()

def show_verb_trainer():
    """Показывает интерфейс тренажера"""
    import random
    
    # Получаем текущий глагол
    if not st.session_state.current_verb:
        st.session_state.current_verb = random.choice(list(DEMO_VERBS.keys()))
        st.session_state.current_pronoun = random.randint(0, 5)
        st.session_state.is_revealed = False
    
    verb = st.session_state.current_verb
    pronoun_idx = st.session_state.current_pronoun
    verb_info = DEMO_VERBS[verb]
    
    # Карточка глагола
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 3rem; border-radius: 1rem; text-align: center; margin: 2rem 0;">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">{verb}</h1>
        <h3 style="opacity: 0.9; margin-bottom: 2rem;">{verb_info['translation']}</h3>
        <div style="font-size: 2.5rem; background: rgba(255,255,255,0.2); padding: 1rem 2rem; border-radius: 0.5rem; display: inline-block;">
            {PRONOUNS[pronoun_idx]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Кнопки управления
    if not st.session_state.is_revealed:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Показать ответ", type="primary", use_container_width=True):
                st.session_state.is_revealed = True
                st.rerun()
    else:
        # Показываем ответ
        conjugation = DEMO_CONJUGATIONS[verb][pronoun_idx]
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #48ca8b 0%, #2dd4bf 100%); color: white; padding: 2rem; border-radius: 1rem; text-align: center; margin: 2rem 0;">
            <h2 style="font-size: 3rem; margin: 0;">✅ {conjugation}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопки оценки
        st.subheader("🎯 Как хорошо вы знали ответ?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("❌ Не знал", use_container_width=True, key="wrong"):
                process_answer(False)
        
        with col2:
            if st.button("😐 Сложно", use_container_width=True, key="hard"):
                process_answer(True)
        
        with col3:
            if st.button("😊 Хорошо", use_container_width=True, key="good"):
                process_answer(True)
        
        with col4:
            if st.button("😎 Легко", use_container_width=True, key="easy"):
                process_answer(True)

def process_answer(correct):
    """Обрабатывает ответ пользователя"""
    st.session_state.score['total'] += 1
    if correct:
        st.session_state.score['correct'] += 1
    
    # Переходим к следующему глаголу
    next_verb()

def next_verb():
    """Переход к следующему глаголу"""
    import random
    
    st.session_state.current_verb = random.choice(list(DEMO_VERBS.keys()))
    st.session_state.current_pronoun = random.randint(0, 5)
    st.session_state.is_revealed = False
    st.rerun()

def clear_url_params():
    """Очищает URL параметры"""
    try:
        st.query_params.clear()
    except:
        pass

def clear_oauth_and_reload():
    """Очищает OAuth состояние и перезагружает"""
    st.session_state.oauth_state = None
    clear_url_params()
    st.rerun()

def logout():
    """Выход из системы"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.oauth_state = None
    st.session_state.current_verb = None
    st.session_state.score = {'correct': 0, 'total': 0}

if __name__ == "__main__":
    main()
