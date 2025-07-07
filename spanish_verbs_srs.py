import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import json

# Конфигурация
st.set_page_config(page_title="🔧 Fragment Workaround", page_icon="🔧")

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', '')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def main():
    st.title("🔧 OAuth Fragment Workaround")
    
    # Инициализация session state
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # ФРАГМЕНТ ПАРСЕР - читает данные из URL hash
    st.markdown("## 🔗 Fragment OAuth Parser")
    
    # JavaScript для чтения fragment и отправки в Streamlit
    fragment_data = st.components.v1.html("""
    <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3>🔍 Fragment Data Reader</h3>
        <p><strong>Full URL:</strong> <span id="full-url">Loading...</span></p>
        <p><strong>Hash:</strong> <span id="hash-content">Loading...</span></p>
        <p><strong>Parsed Data:</strong></p>
        <pre id="parsed-data" style="background: white; padding: 10px; border-radius: 5px;">Loading...</pre>
        
        <div id="oauth-data" style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 5px; display: none;">
            <h4>🎉 OAuth Data Found!</h4>
            <p><strong>Code:</strong> <span id="oauth-code">-</span></p>
            <p><strong>State:</strong> <span id="oauth-state">-</span></p>
        </div>
    </div>
    
    <script>
    function parseFragment() {
        try {
            const url = window.location.href;
            const hash = window.location.hash;
            
            document.getElementById('full-url').textContent = url;
            document.getElementById('hash-content').textContent = hash || '(empty)';
            
            let data = {};
            
            if (hash && hash.length > 1) {
                // Убираем # и парсим как query string
                const params = new URLSearchParams(hash.substring(1));
                for (const [key, value] of params) {
                    data[key] = value;
                }
                
                // Или парсим как JSON если это JSON
                try {
                    if (hash.startsWith('#json:')) {
                        data = JSON.parse(decodeURIComponent(hash.substring(6)));
                    }
                } catch (e) {
                    console.log('Not JSON format');
                }
            }
            
            document.getElementById('parsed-data').textContent = JSON.stringify(data, null, 2);
            
            // Проверяем OAuth данные
            if (data.code && data.state) {
                document.getElementById('oauth-code').textContent = data.code.substring(0, 30) + '...';
                document.getElementById('oauth-state').textContent = data.state.substring(0, 30) + '...';
                document.getElementById('oauth-data').style.display = 'block';
                
                // Автоматически отправляем данные в Streamlit
                // Сохраняем в localStorage для передачи в Streamlit
                localStorage.setItem('oauth_fragment_data', JSON.stringify(data));
                
                console.log('OAuth data saved to localStorage:', data);
            }
            
            console.log('Fragment parsed:', data);
            
        } catch (error) {
            console.error('Error parsing fragment:', error);
            document.getElementById('full-url').textContent = 'Error: ' + error.message;
        }
    }
    
    // Парсим при загрузке
    parseFragment();
    
    // Парсим каждые 2 секунды для обновлений
    setInterval(parseFragment, 2000);
    </script>
    """, height=300)
    
    # Читаем данные из fragment через localStorage
    oauth_data = get_oauth_from_fragment()
    
    if oauth_data:
        st.success("🎉 OAuth данные получены из fragment!")
        st.json(oauth_data)
        
        code = oauth_data.get('code')
        state = oauth_data.get('state')
        
        if code and state and st.button("🔄 Обработать OAuth данные"):
            process_oauth_code(code, state)
    
    # Обычная логика авторизации
    st.markdown("---")
    
    if st.session_state.authenticated:
        st.success("✅ Вы авторизованы!")
        user_info = st.session_state.user_info
        if user_info:
            st.write(f"**Имя:** {user_info.get('name')}")
            st.write(f"**Email:** {user_info.get('email')}")
        
        if st.button("🚪 Выйти"):
            logout()
            st.rerun()
    
    else:
        st.info("👤 Необходима авторизация")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔐 Войти через Google (Query)", type="primary"):
                # Обычный OAuth с query параметрами
                auth_url = generate_auth_url()
                redirect_with_js(auth_url)
        
        with col2:
            if st.button("🔧 Войти через Google (Fragment)", help="Альтернативный метод"):
                # Модифицированный OAuth с fragment redirect
                auth_url = generate_fragment_auth_url()
                redirect_with_js(auth_url)
    
    # Тестовые ссылки с fragment
    st.markdown("## 🧪 Тест Fragment URLs")
    
    base_url = "https://spanishverbint-production.up.railway.app"
    test_fragments = [
        f"{base_url}#test=simple",
        f"{base_url}#code=test_code&state=test_state",
        f"{base_url}#json:{{'test': 'json_data', 'working': true}}"
    ]
    
    for i, url in enumerate(test_fragments, 1):
        st.markdown(f"**Fragment Test {i}:** [Открыть]({url})")
    
    # Кнопки управления
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reload"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Fragment"):
            clear_fragment()
    
    with col3:
        if st.button("📊 Show Session"):
            st.json(dict(st.session_state))

def get_oauth_from_fragment():
    """Получает OAuth данные из fragment через localStorage"""
    # В реальной реализации здесь будет JavaScript bridge
    # Пока возвращаем None, данные будут обрабатываться через JavaScript
    return None

def generate_auth_url():
    """Генерирует обычный OAuth URL"""
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

def generate_fragment_auth_url():
    """Генерирует OAuth URL с fragment redirect"""
    # Создаем промежуточную страницу которая конвертирует query в fragment
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    st.session_state.oauth_state = state
    
    # Используем специальный redirect URI который конвертирует query в fragment
    fragment_redirect_uri = REDIRECT_URI.replace('/auth/callback', '/auth/fragment')
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': fragment_redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    st.info("⚠️ Для fragment метода нужна дополнительная настройка redirect URI")
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def redirect_with_js(url):
    """Выполняет redirect через JavaScript"""
    st.components.v1.html(f"""
    <script>
    console.log('Redirecting to:', '{url}');
    window.location.href = '{url}';
    </script>
    <p>Перенаправляем на Google...</p>
    """, height=100)

def clear_fragment():
    """Очищает fragment из URL"""
    st.components.v1.html("""
    <script>
    // Очищаем hash
    if (window.location.hash) {
        history.replaceState(null, null, window.location.pathname + window.location.search);
    }
    // Очищаем localStorage
    localStorage.removeItem('oauth_fragment_data');
    console.log('Fragment and localStorage cleared');
    </script>
    <p>Fragment очищен</p>
    """, height=100)

def process_oauth_code(code, state):
    """Обрабатывает OAuth код"""
    st.write("### 🔄 Обработка OAuth...")
    
    if state != st.session_state.oauth_state:
        st.error("❌ State не совпадает!")
        return
    
    with st.spinner("Получаем токен..."):
        data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
        }
        
        try:
            response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                
                if access_token:
                    headers = {'Authorization': f'Bearer {access_token}'}
