import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import time

# Конфигурация
st.set_page_config(page_title="🔍 URL Debug", page_icon="🔍")

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', '')

def main():
    st.title("🔍 URL Redirect Debug Tool")
    
    # Инициализация
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'url_history' not in st.session_state:
        st.session_state.url_history = []
    
    # ПОСТОЯННЫЙ МОНИТОРИНГ URL
    st.markdown("## 🌐 Постоянный URL мониторинг")
    
    # JavaScript который отслеживает ВСЕ изменения URL
    url_monitor = st.components.v1.html("""
    <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3>🔍 LIVE URL Monitor</h3>
        <p><strong>Current URL:</strong> <span id="current-url">Loading...</span></p>
        <p><strong>Search Params:</strong> <span id="search-params">Loading...</span></p>
        <p><strong>Page Loads:</strong> <span id="load-count">0</span></p>
        
        <h4>📋 URL History:</h4>
        <div id="url-history" style="background: white; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;">
            Loading...
        </div>
        
        <button onclick="captureURL()" style="margin-top: 10px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
            📸 Capture Current URL
        </button>
    </div>
    
    <script>
    let loadCount = 0;
    let urlHistory = [];
    
    function updateURL() {
        loadCount++;
        const url = window.location.href;
        const search = window.location.search;
        const timestamp = new Date().toLocaleTimeString();
        
        document.getElementById('current-url').textContent = url;
        document.getElementById('search-params').textContent = search || '(empty)';
        document.getElementById('load-count').textContent = loadCount;
        
        // Добавляем в историю если URL изменился
        const lastURL = urlHistory.length > 0 ? urlHistory[urlHistory.length - 1].url : '';
        if (url !== lastURL) {
            urlHistory.push({
                time: timestamp,
                url: url,
                search: search,
                load: loadCount
            });
            
            // Ограничиваем историю
            if (urlHistory.length > 10) {
                urlHistory = urlHistory.slice(-10);
            }
            
            updateHistoryDisplay();
        }
        
        // Логируем все в консоль
        console.log(`[${timestamp}] URL: ${url}`);
        if (search) {
            console.log(`[${timestamp}] Search: ${search}`);
            console.log(`[${timestamp}] Parsed:`, Object.fromEntries(new URLSearchParams(search)));
        }
    }
    
    function updateHistoryDisplay() {
        const historyDiv = document.getElementById('url-history');
        historyDiv.innerHTML = urlHistory.map(entry => 
            `<div style="margin-bottom: 5px; padding: 5px; border-left: 3px solid #007bff;">
                <strong>${entry.time}</strong> (Load #${entry.load})<br>
                ${entry.url}<br>
                <small>Search: ${entry.search || '(empty)'}</small>
            </div>`
        ).join('');
    }
    
    function captureURL() {
        updateURL();
        alert('URL captured! Check history above.');
    }
    
    // Обновляем при загрузке
    updateURL();
    
    // Отслеживаем изменения URL
    let lastURL = window.location.href;
    setInterval(() => {
        if (window.location.href !== lastURL) {
            lastURL = window.location.href;
            updateURL();
        }
    }, 500);
    
    // Отслеживаем события навигации
    window.addEventListener('popstate', updateURL);
    window.addEventListener('pushstate', updateURL);
    window.addEventListener('replacestate', updateURL);
    
    // Обновляем каждые 2 секунды для надежности
    setInterval(updateURL, 2000);
    </script>
    """, height=400)
    
    # STREAMLIT ДИАГНОСТИКА
    st.markdown("## 📋 Streamlit Query Params")
    
    query_params = dict(st.query_params)
    
    if query_params:
        st.success("✅ Streamlit видит параметры!")
        st.json(query_params)
    else:
        st.warning("⚠️ Streamlit не видит параметры")
    
    # ПРОВЕРКА REDIRECT_URI
    st.markdown("## 🔗 OAuth Configuration Check")
    
    st.write("**Environment Variables:**")
    st.write(f"REDIRECT_URI: `{REDIRECT_URI}`")
    
    # Проверяем соответствие с текущим доменом
    current_domain = "https://spanishverbint-production.up.railway.app"
    expected_redirect = f"{current_domain}/auth/callback"
    
    st.write(f"**Expected:** `{expected_redirect}`")
    
    if REDIRECT_URI == expected_redirect:
        st.success("✅ REDIRECT_URI соответствует домену")
    else:
        st.error("❌ REDIRECT_URI не соответствует домену!")
        st.write("**Исправьте переменную окружения в Railway:**")
        st.code(f"REDIRECT_URI={expected_redirect}")
    
    # ТЕСТОВЫЕ ССЫЛКИ
    st.markdown("## 🧪 Тесты callback URL")
    
    # Тест 1: Прямой переход на callback с параметрами
    callback_test_url = f"{current_domain}/auth/callback?code=test_code&state=test_state"
    st.markdown(f"**Тест 1:** [Callback с тестовыми параметрами]({callback_test_url})")
    
    # Тест 2: Прямой переход на callback без параметров
    callback_empty_url = f"{current_domain}/auth/callback"
    st.markdown(f"**Тест 2:** [Callback без параметров]({callback_empty_url})")
    
    # Тест 3: Обычная страница с параметрами
    main_test_url = f"{current_domain}?test=main_page&timestamp={int(time.time())}"
    st.markdown(f"**Тест 3:** [Главная с параметрами]({main_test_url})")
    
    # GOOGLE CONSOLE ПРОВЕРКА
    st.markdown("## 🔧 Google Console Verification")
    
    st.write("**Проверьте в Google Cloud Console:**")
    st.write("1. APIs & Services → Credentials")
    st.write("2. Ваш OAuth 2.0 Client ID")
    st.write("3. Authorized redirect URIs должен содержать ТОЧНО:")
    st.code(REDIRECT_URI)
    
    # ЛОГИ OAUTH
    st.markdown("## 📋 OAuth Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Test OAuth Flow"):
            test_oauth_flow()
    
    with col2:
        if st.button("🧹 Clear All"):
            st.query_params.clear()
            st.session_state.oauth_state = None
            st.rerun()
    
    # SESSION STATE
    st.markdown("## 📊 Session State")
    st.write(f"oauth_state: {st.session_state.oauth_state}")
    
    if st.button("📋 Show Full Session"):
        st.json(dict(st.session_state))

def test_oauth_flow():
    """Тестирует OAuth flow с логированием"""
    st.write("### 🔄 Testing OAuth Flow...")
    
    # Генерируем state
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    st.session_state.oauth_state = state
    
    # Проверяем конфигурацию
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.error("❌ OAuth credentials missing")
        return
    
    # Показываем что будем отправлять
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    st.write("**OAuth Parameters:**")
    st.json(params)
    
    st.write("**Full Auth URL:**")
    st.code(auth_url)
    
    st.write(f"**State (first 20 chars):** {state[:20]}")
    
    # Инструкции
    st.info("""
    **Инструкции:**
    1. Нажмите ссылку ниже для авторизации
    2. После авторизации Google вернет вас на callback URL
    3. Посмотрите на URL Monitor выше - он покажет ТОЧНЫЙ URL куда Google делает redirect
    4. Проверьте есть ли параметры code и state в URL
    """)
    
    # Ссылка для ручного перехода
    st.markdown(f"**[🔐 Authorize with Google]({auth_url})**")
    
    # Автоматический redirect через JavaScript (опционально)
    if st.button("🚀 Auto Redirect"):
        st.components.v1.html(f"""
        <script>
        console.log('Redirecting to OAuth...');
        window.location.href = '{auth_url}';
        </script>
        <p>Redirecting...</p>
        """, height=100)

if __name__ == "__main__":
    main()
