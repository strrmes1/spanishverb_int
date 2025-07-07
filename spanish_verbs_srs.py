import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import datetime

# Конфигурация
st.set_page_config(page_title="🇪🇸 Spanish Verbs - OAuth Fixed", page_icon="🇪🇸")

# OAuth настройки - ИЗМЕНЕНО для root path
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
# Используем root path вместо /auth/callback
ROOT_DOMAIN = "https://spanishverbint-production.up.railway.app"
REDIRECT_URI = ROOT_DOMAIN  # Просто root, без /auth/callback

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def main():
    st.title("🇪🇸 Тренажер испанских глаголов")
    st.caption("OAuth исправлен - используем root path")
    
    # Инициализация
    init_session_state()
    
    # Диагностика
    show_debug_info()
    
    # Получаем query параметры
    query_params = dict(st.query_params)
    
    # ОСНОВНАЯ ЛОГИКА
    
    # 1. Проверяем OAuth callback (теперь на root path)
    if 'code' in query_params and 'state' in query_params:
        handle_oauth_callback(query_params)
    
    # 2. Если уже авторизован
    elif st.session_state.authenticated:
        show_main_app()
    
    # 3. Показываем форму входа
    else:
        show_login_form()
    
    # Показываем логи
    show_event_log()

def init_session_state():
    """Инициализация session state"""
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'event_log' not in st.session_state:
        st.session_state.event_log = []

def log_event(event, data=None):
    """Логирует события"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "time": timestamp,
        "event": event,
        "data": data or {}
    }
    st.session_state.event_log.append(log_entry)
    
    if len(st.session_state.event_log) > 15:
        st.session_state.event_log = st.session_state.event_log[-15:]

def show_debug_info():
    """Отладочная информация"""
    with st.expander("🔍 Debug Info", expanded=False):
        query_params = dict(st.query_params)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Query Params:**")
            if query_params:
                st.json(query_params)
            else:
                st.write("(empty)")
        
        with col2:
            st.write("**OAuth Status:**")
            st.write(f"authenticated: {st.session_state.authenticated}")
            st.write(f"oauth_state: {bool(st.session_state.oauth_state)}")
            st.write(f"REDIRECT_URI: {REDIRECT_URI}")

def handle_oauth_callback(query_params):
    """Обрабатывает OAuth callback"""
    st.markdown("## 🔄 OAuth Callback (на root path)")
    
    code = query_params.get('code')
    state = query_params.get('state')
    error = query_params.get('error')
    
    log_event("oauth_callback_received", {
        "has_code": bool(code),
        "has_state": bool(state),
        "has_error": bool(error),
        "path": "root"
    })
    
    # Проверяем ошибки
    if error:
        st.error(f"❌ OAuth Error: {error}")
        error_description = query_params.get('error_description', 'No description')
        st.write(f"Description: {error_description}")
        
        if st.button("🔄 Try Again"):
            clear_url_params()
            st.rerun()
        return
    
    # Проверяем код
    if not code:
        st.error("❌ Authorization code missing")
        return
    
    # Проверяем state
    if not state or state != st.session_state.oauth_state:
        st.error("❌ State mismatch")
        st.write(f"Received: {state[:20] if state else 'None'}...")
        st.write(f"Expected: {st.session_state.oauth_state[:20] if st.session_state.oauth_state else 'None'}...")
        return
    
    # Все ОК
    st.success("✅ OAuth callback validation passed!")
    st.write(f"Code: {code[:30]}...")
    st.write(f"State: {state[:20]}...")
    
    # Автоматически обрабатываем код
    with st.spinner("Processing authorization..."):
        success = process_authorization_code(code)
        
        if success:
            st.success("🎉 Authentication successful!")
            # Очищаем URL и перезагружаем
            clear_url_params()
            time.sleep(1)  # Небольшая пауза
            st.rerun()
        else:
            st.error("❌ Authentication failed")

def process_authorization_code(code):
    """Обрабатывает authorization code"""
    try:
        # Получаем токен
        token_data = exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            st.error("❌ Failed to get access token")
            return False
        
        access_token = token_data['access_token']
        st.success("✅ Access token received")
        
        # Получаем пользователя
        user_info = get_user_info(access_token)
        if not user_info:
            st.error("❌ Failed to get user info")
            return False
        
        st.success("✅ User info received")
        
        # Сохраняем
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        
        log_event("authentication_successful", {
            "user_email": user_info.get('email'),
            "user_name": user_info.get('name')
        })
        
        return True
        
    except Exception as e:
        st.error(f"❌ Exception: {e}")
        log_event("authentication_failed", {"error": str(e)})
        return False

def exchange_code_for_token(code):
    """Обменивает код на токен"""
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,  # Теперь это root path
    }
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Token request failed: {response.status_code}")
            st.code(response.text)
            return None
            
    except Exception as e:
        st.error(f"Token request exception: {e}")
        return None

def get_user_info(access_token):
    """Получает информацию о пользователе"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"User info request failed: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"User info request exception: {e}")
        return None

def show_login_form():
    """Показывает форму входа"""
    st.markdown("## 🔐 Вход в систему")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Войдите через Google для доступа к тренажеру:")
        
        if st.button("🔐 Войти через Google", type="primary"):
            start_oauth_flow()
    
    with col2:
        st.info("""
        **OAuth исправлен!**
        
        Теперь используем root path 
        для redirect вместо 
        `/auth/callback`
        """)

def start_oauth_flow():
    """Запускает OAuth flow"""
    # Генерируем state
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    st.session_state.oauth_state = state
    
    log_event("oauth_flow_started", {"state": state[:20]})
    
    # Параметры OAuth - REDIRECT_URI теперь root
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,  # Root path!
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    st.write(f"**Redirect URI:** {REDIRECT_URI}")
    st.write(f"**State:** {state[:20]}...")
    
    # Redirect через JavaScript
    st.components.v1.html(f"""
    <script>
    console.log('OAuth redirect to:', '{auth_url}');
    window.location.href = '{auth_url}';
    </script>
    <div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 10px;">
        <h3>🔄 Redirecting to Google...</h3>
        <p>State: {state[:20]}...</p>
        <p>If redirect doesn't work, <a href="{auth_url}" target="_self">click here</a></p>
    </div>
    """, height=150)

def show_main_app():
    """Показывает основное приложение"""
    st.markdown("## ✅ Авторизован!")
    
    user_info = st.session_state.user_info
    if user_info:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Добро пожаловать, {user_info.get('name')}!**")
            st.write(f"📧 {user_info.get('email')}")
            
            if user_info.get('picture'):
                st.image(user_info['picture'], width=80)
        
        with col2:
            if st.button("🚪 Выйти"):
                logout()
                st.rerun()
    
    # Простой интерфейс тренажера
    st.markdown("---")
    st.markdown("## 🇪🇸 Тренажер глаголов")
    
    st.success("🎉 OAuth успешно работает!")
    st.write("Теперь можно интегрировать полную функциональность тренажера.")
    
    # Демо функционал
    if st.button("🎯 Начать изучение"):
        st.balloons()
        st.write("Здесь будет интерфейс изучения глаголов!")

def clear_url_params():
    """Очищает URL параметры"""
    try:
        st.query_params.clear()
        log_event("url_params_cleared")
    except Exception as e:
        log_event("url_params_clear_failed", {"error": str(e)})

def logout():
    """Выход из системы"""
    log_event("user_logout")
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.oauth_state = None

def show_event_log():
    """Показывает лог событий"""
    if st.session_state.event_log:
        with st.expander("📋 Event Log", expanded=False):
            for entry in reversed(st.session_state.event_log[-5:]):
                st.write(f"**{entry['time']}** - {entry['event']}")
                if entry['data']:
                    st.json(entry['data'])
                st.write("---")

if __name__ == "__main__":
    main()
