import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64

# Конфигурация
st.set_page_config(page_title="🇪🇸 Debug OAuth", page_icon="🇪🇸")

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', '')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def main():
    st.title("🔍 OAuth Debug Tool - Fixed Version")
    
    # Инициализация session state
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # ОТЛАДКА: показываем что происходит
    st.write("### 🔧 Диагностика")
    
    # Получаем query parameters ТОЛЬКО новым способом
    try:
        # Конвертируем в обычный словарь для удобства
        query_params = {}
        for key in st.query_params:
            query_params[key] = st.query_params[key]
        
        st.write("**Query Parameters (новый API):**")
        st.json(query_params)
        
        # Показываем как raw значения
        st.write("**Raw query_params объект:**")
        st.write(f"Тип: {type(st.query_params)}")
        st.write(f"Ключи: {list(st.query_params.keys())}")
        
    except Exception as e:
        st.error(f"Ошибка с query_params: {e}")
        query_params = {}
    
    # Показываем URL через JavaScript
    st.markdown("""
    <div style="background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <strong>Текущий URL:</strong> <span id="current-url">Loading...</span><br>
        <strong>Search параметры:</strong> <span id="search-params">Loading...</span>
    </div>
    
    <script>
    document.getElementById('current-url').textContent = window.location.href;
    document.getElementById('search-params').textContent = window.location.search || '(нет параметров)';
    console.log('Current URL:', window.location.href);
    console.log('Search params:', window.location.search);
    </script>
    """, unsafe_allow_html=True)
    
    # Проверяем переменные окружения
    st.write("**Environment Variables:**")
    st.write(f"GOOGLE_CLIENT_ID: {'✅ Set' if GOOGLE_CLIENT_ID else '❌ Missing'}")
    st.write(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if GOOGLE_CLIENT_SECRET else '❌ Missing'}")
    st.write(f"REDIRECT_URI: {REDIRECT_URI}")
    
    # Проверяем session state
    st.write("**Session State:**")
    st.write(f"oauth_state: {st.session_state.oauth_state}")
    st.write(f"authenticated: {st.session_state.authenticated}")
    if st.session_state.user_info:
        st.write(f"user_info: {st.session_state.user_info.get('name', 'Unknown')}")
    
    # ОСНОВНАЯ ЛОГИКА
    
    # Проверяем наличие кода авторизации
    if 'code' in query_params:
        st.success("🎉 Найден authorization code!")
        
        code = query_params['code']
        state = query_params.get('state', '')
        
        st.write(f"**Code:** {code[:30]}...")
        st.write(f"**State:** {state[:30]}...")
        st.write(f"**Stored state:** {st.session_state.oauth_state[:30] if st.session_state.oauth_state else 'None'}...")
        
        # Автоматическая обработка или кнопка
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Обработать авторизацию", type="primary"):
                process_oauth_code(code, state)
        
        with col2:
            if st.button("🧹 Очистить URL"):
                clear_query_params()
                st.rerun()
    
    elif st.session_state.authenticated and st.session_state.user_info:
        st.success("✅ Вы успешно авторизованы!")
        
        user_info = st.session_state.user_info
        st.write(f"**Имя:** {user_info.get('name')}")
        st.write(f"**Email:** {user_info.get('email')}")
        st.write(f"**ID:** {user_info.get('id')}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Перейти к приложению"):
                # Здесь можно добавить переход к основному приложению
                st.info("Переход к основному приложению...")
        
        with col2:
            if st.button("🚪 Выйти"):
                logout()
                st.rerun()
    
    else:
        st.info("👤 Необходима авторизация")
        
        if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
            if st.button("🔐 Войти через Google", type="primary"):
                auth_url = generate_auth_url()
                st.write(f"Генерируем redirect на: {auth_url}")
                
                # Redirect через JavaScript
                st.markdown(f"""
                <script>
                window.location.href = '{auth_url}';
                </script>
                """, unsafe_allow_html=True)
                
                st.info("Перенаправляем на Google...")
        else:
            st.error("❌ OAuth переменные не настроены")
    
    # Дополнительные кнопки управления
    st.markdown("---")
    st.write("### 🛠️ Управление")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Обновить страницу"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Очистить всё"):
            clear_query_params()
            logout()
            st.rerun()
    
    with col3:
        if st.button("📋 Показать session"):
            st.json(dict(st.session_state))

def generate_auth_url():
    """Генерирует URL для авторизации"""
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
    st.write(f"Generated state: {state[:20]}...")
    return auth_url

def process_oauth_code(code, state):
    """Обрабатывает OAuth код"""
    st.write("### 🔄 Обработка авторизации...")
    
    # Проверяем state
    if state != st.session_state.oauth_state:
        st.error(f"❌ State не совпадает!")
        st.write(f"Получен: {state[:20]}...")
        st.write(f"Ожидался: {st.session_state.oauth_state[:20] if st.session_state.oauth_state else 'None'}...")
        return
    
    st.write("✅ State проверен")
    
    # Обмениваем код на токен
    with st.spinner("Получаем токен..."):
        token_response = exchange_code_for_token(code)
        
        if token_response and 'access_token' in token_response:
            access_token = token_response['access_token']
            st.write("✅ Токен получен!")
            
            # Получаем данные пользователя
            with st.spinner("Получаем данные пользователя..."):
                user_info = get_user_info(access_token)
                
                if user_info:
                    st.write("✅ Данные пользователя получены!")
                    
                    # Сохраняем в session
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    
                    st.success("🎉 Авторизация завершена успешно!")
                    
                    # Очищаем URL и перезагружаем
                    clear_query_params()
                    st.rerun()
                else:
                    st.error("❌ Ошибка получения данных пользователя")
        else:
            st.error("❌ Ошибка получения токена")

def exchange_code_for_token(code):
    """Обменивает код на токен"""
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        st.write(f"Token response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Exception: {e}")
        return None

def get_user_info(access_token):
    """Получает информацию о пользователе"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
        st.write(f"User info response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Exception: {e}")
        return None

def clear_query_params():
    """Очищает query параметры"""
    try:
        st.query_params.clear()
        st.write("✅ Query параметры очищены")
    except Exception as e:
        st.error(f"Ошибка очистки параметров: {e}")

def logout():
    """Выход из системы"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.oauth_state = None

if __name__ == "__main__":
    main()
