import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import time
import datetime

# Конфигурация
st.set_page_config(page_title="🔧 Fixed OAuth", page_icon="🔧")

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', '')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def main():
    st.title("🔧 Fixed OAuth - Detailed Logging")
    
    # Инициализация session state
    init_session_state()
    
    # ВСЕГДА показываем отладочную информацию
    show_debug_info()
    
    # Получаем query параметры
    query_params = dict(st.query_params)
    
    # Логируем каждый вызов main()
    log_event("main() called", {
        "has_query_params": bool(query_params),
        "query_params": query_params,
        "authenticated": st.session_state.authenticated,
        "oauth_state_exists": bool(st.session_state.oauth_state)
    })
    
    # ОСНОВНАЯ ЛОГИКА OAUTH
    
    # 1. Проверяем OAuth callback
    if 'code' in query_params:
        handle_oauth_callback(query_params)
    
    # 2. Если уже авторизован
    elif st.session_state.authenticated:
        show_authenticated_user()
    
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
    if 'oauth_attempt_count' not in st.session_state:
        st.session_state.oauth_attempt_count = 0

def log_event(event, data=None):
    """Логирует события для отладки"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "time": timestamp,
        "event": event,
        "data": data or {}
    }
    st.session_state.event_log.append(log_entry)
    
    # Ограничиваем размер лога
    if len(st.session_state.event_log) > 20:
        st.session_state.event_log = st.session_state.event_log[-20:]

def show_debug_info():
    """Показывает отладочную информацию"""
    st.markdown("## 🔍 Debug Info")
    
    query_params = dict(st.query_params)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Query Params:**")
        if query_params:
            st.json(query_params)
        else:
            st.write("(empty)")
    
    with col2:
        st.write("**Session State:**")
        st.write(f"authenticated: {st.session_state.authenticated}")
        st.write(f"oauth_state: {st.session_state.oauth_state[:20] if st.session_state.oauth_state else 'None'}...")
        st.write(f"attempt_count: {st.session_state.oauth_attempt_count}")

def handle_oauth_callback(query_params):
    """Обрабатывает OAuth callback"""
    st.markdown("## 🔄 OAuth Callback Processing")
    
    code = query_params.get('code')
    state = query_params.get('state')
    error = query_params.get('error')
    
    log_event("oauth_callback_received", {
        "has_code": bool(code),
        "has_state": bool(state),
        "has_error": bool(error),
        "code_length": len(code) if code else 0,
        "state_length": len(state) if state else 0
    })
    
    # Проверяем на ошибки от Google
    if error:
        st.error(f"❌ OAuth Error: {error}")
        error_description = query_params.get('error_description', 'No description')
        st.write(f"Description: {error_description}")
        log_event("oauth_error", {"error": error, "description": error_description})
        
        if st.button("🔄 Try Again"):
            clear_oauth_state()
            st.rerun()
        return
    
    # Проверяем наличие кода
    if not code:
        st.error("❌ Authorization code not found in callback")
        log_event("oauth_no_code", query_params)
        return
    
    # Проверяем state
    if not state:
        st.error("❌ State parameter missing")
        log_event("oauth_no_state", query_params)
        return
    
    if state != st.session_state.oauth_state:
        st.error("❌ State mismatch - possible CSRF attack")
        st.write(f"Received: {state[:20]}...")
        st.write(f"Expected: {st.session_state.oauth_state[:20] if st.session_state.oauth_state else 'None'}...")
        log_event("oauth_state_mismatch", {
            "received_state": state[:20],
            "expected_state": st.session_state.oauth_state[:20] if st.session_state.oauth_state else None
        })
        
        if st.button("🔄 Reset and Try Again"):
            clear_oauth_state()
            st.rerun()
        return
    
    # Все проверки пройдены
    st.success("✅ OAuth callback validation passed")
    st.write(f"Code: {code[:30]}...")
    st.write(f"State: {state[:20]}...")
    
    # Кнопка для продолжения обработки
    if st.button("🚀 Process Authorization Code", type="primary"):
        process_authorization_code(code)

def process_authorization_code(code):
    """Обрабатывает authorization code"""
    st.markdown("### 🔄 Processing Authorization Code...")
    
    log_event("processing_auth_code", {"code_length": len(code)})
    
    # Обмениваем код на токен
    with st.spinner("Exchanging code for token..."):
        token_data = exchange_code_for_token(code)
        
        if not token_data:
            st.error("❌ Failed to get token")
            return
        
        access_token = token_data.get('access_token')
        if not access_token:
            st.error("❌ Access token not found in response")
            st.json(token_data)
            log_event("no_access_token", token_data)
            return
        
        st.success("✅ Access token received!")
        log_event("access_token_received", {"token_length": len(access_token)})
    
    # Получаем информацию о пользователе
    with st.spinner("Getting user information..."):
        user_info = get_user_info(access_token)
        
        if not user_info:
            st.error("❌ Failed to get user info")
            return
        
        st.success("✅ User information received!")
        st.json(user_info)
        log_event("user_info_received", {
            "user_id": user_info.get('id'),
            "user_name": user_info.get('name'),
            "user_email": user_info.get('email')
        })
    
    # Сохраняем в session state
    st.session_state.authenticated = True
    st.session_state.user_info = user_info
    log_event("user_authenticated", {"user_email": user_info.get('email')})
    
    st.success("🎉 Authentication completed successfully!")
    
    # Очищаем URL и перезагружаем
    if st.button("✨ Continue to App"):
        clear_url_params()
        st.rerun()

def exchange_code_for_token(code):
    """Обменивает authorization code на access token"""
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }
    
    try:
        st.write("🔄 Making token request to Google...")
        response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        
        st.write(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            log_event("token_exchange_success", {"status": response.status_code})
            return token_data
        else:
            st.error(f"Token request failed with status {response.status_code}")
            st.code(response.text)
            log_event("token_exchange_failed", {
                "status": response.status_code,
                "response": response.text[:200]
            })
            return None
            
    except Exception as e:
        st.error(f"Exception during token exchange: {e}")
        log_event("token_exchange_exception", {"error": str(e)})
        return None

def get_user_info(access_token):
    """Получает информацию о пользователе"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        st.write("🔄 Getting user info from Google...")
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
        
        st.write(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            log_event("user_info_success", {"status": response.status_code})
            return user_data
        else:
            st.error(f"User info request failed with status {response.status_code}")
            st.code(response.text)
            log_event("user_info_failed", {
                "status": response.status_code,
                "response": response.text[:200]
            })
            return None
            
    except Exception as e:
        st.error(f"Exception during user info request: {e}")
        log_event("user_info_exception", {"error": str(e)})
        return None

def show_authenticated_user():
    """Показывает информацию об авторизованном пользователе"""
    st.markdown("## ✅ Authenticated User")
    
    user_info = st.session_state.user_info
    if user_info:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Name:** {user_info.get('name')}")
            st.write(f"**Email:** {user_info.get('email')}")
            st.write(f"**ID:** {user_info.get('id')}")
            
            if user_info.get('picture'):
                st.image(user_info['picture'], width=100)
        
        with col2:
            if st.button("🚪 Logout"):
                logout()
                st.rerun()
    
    st.success("🎉 OAuth Authentication Working!")
    st.write("Теперь можно интегрировать с основным приложением.")

def show_login_form():
    """Показывает форму входа"""
    st.markdown("## 🔐 Login Required")
    
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error("❌ OAuth credentials not configured")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Войдите через Google для продолжения:")
        
        if st.button("🔐 Login with Google", type="primary"):
            start_oauth_flow()
    
    with col2:
        st.write("**OAuth Config:**")
        st.write(f"✅ Client ID: Set")
        st.write(f"✅ Client Secret: Set")
        st.write(f"✅ Redirect URI: Set")

def start_oauth_flow():
    """Запускает OAuth flow"""
    st.session_state.oauth_attempt_count += 1
    
    # Генерируем новый state
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    st.session_state.oauth_state = state
    
    log_event("oauth_flow_started", {
        "attempt": st.session_state.oauth_attempt_count,
        "state": state[:20]
    })
    
    # Создаем auth URL
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
    
    st.write(f"**Generated Auth URL:** {auth_url}")
    st.write(f"**State:** {state[:20]}...")
    
    # Redirect через JavaScript
    st.components.v1.html(f"""
    <script>
    console.log('OAuth redirect to:', '{auth_url}');
    setTimeout(function() {{
        window.location.href = '{auth_url}';
    }}, 1000);
    </script>
    <div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 10px;">
        <h3>🔄 Redirecting to Google...</h3>
        <p>If redirect doesn't work, <a href="{auth_url}" target="_self">click here</a></p>
    </div>
    """, height=150)

def clear_oauth_state():
    """Очищает OAuth состояние"""
    st.session_state.oauth_state = None
    st.session_state.authenticated = False
    st.session_state.user_info = None
    log_event("oauth_state_cleared")

def clear_url_params():
    """Очищает URL параметры"""
    try:
        st.query_params.clear()
        log_event("url_params_cleared")
    except Exception as e:
        log_event("url_params_clear_failed", {"error": str(e)})

def logout():
    """Выход из системы"""
    log_event("user_logout", {"user_email": st.session_state.user_info.get('email') if st.session_state.user_info else None})
    clear_oauth_state()

def show_event_log():
    """Показывает лог событий"""
    if st.session_state.event_log:
        with st.expander("📋 Event Log", expanded=False):
            for i, entry in enumerate(reversed(st.session_state.event_log[-10:])):
                st.write(f"**{entry['time']}** - {entry['event']}")
                if entry['data']:
                    st.json(entry['data'])
                st.write("---")

if __name__ == "__main__":
    main()
