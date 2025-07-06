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
    st.title("🔍 OAuth Debug Tool")
    
    # ВСЕГДА показываем отладочную информацию
    st.write("### 🔧 Диагностика")
    
    # Проверяем query parameters
    st.write("**Query Parameters:**")
    try:
        # Пробуем разные способы получить параметры
        query_params = st.query_params
        st.write(f"st.query_params: {dict(query_params)}")
        
        # Альтернативный способ
        import streamlit as st_alt
        try:
            alt_params = st_alt.experimental_get_query_params()
            st.write(f"experimental (fallback): {alt_params}")
        except:
            st.write("experimental API недоступен")
            
    except Exception as e:
        st.error(f"Ошибка получения параметров: {e}")
    
    # Проверяем URL
    st.write("**URL информация:**")
    try:
        # Получаем текущий URL через JavaScript
        st.components.v1.html("""
        <script>
        window.parent.postMessage({
            type: 'streamlit:componentReady',
            data: {
                url: window.location.href,
                search: window.location.search,
                hash: window.location.hash
            }
        }, '*');
        </script>
        <p>Текущий URL: <span id="url">Loading...</span></p>
        <script>
        document.getElementById('url').textContent = window.location.href;
        </script>
        """, height=100)
    except:
        st.write("Не удалось получить URL через JavaScript")
    
    # Проверяем переменные окружения
    st.write("**Environment Variables:**")
    st.write(f"GOOGLE_CLIENT_ID: {'✅ Set' if GOOGLE_CLIENT_ID else '❌ Missing'}")
    st.write(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if GOOGLE_CLIENT_SECRET else '❌ Missing'}")
    st.write(f"REDIRECT_URI: {REDIRECT_URI}")
    
    # Проверяем session state
    st.write("**Session State:**")
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    st.write(f"oauth_state: {st.session_state.oauth_state}")
    st.write(f"authenticated: {st.session_state.authenticated}")
    
    # Простая обработка callback
    query_params = st.query_params
    
    if 'code' in query_params:
        st.success("🎉 Найден authorization code!")
        
        code = query_params['code']
        state = query_params.get('state', '')
        
        st.write(f"**Code:** {code[:30]}...")
        st.write(f"**State:** {state[:30]}...")
        
        # Кнопка для обработки
        if st.button("🔄 Обработать авторизацию", type="primary"):
            process_oauth_code(code, state)
    
    elif st.session_state.authenticated:
        st.success("✅ Вы авторизованы!")
        
        if st.button("🚪 Выйти"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()
    
    else:
        st.info("👤 Войдите для продолжения")
        
        if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
            # Генерируем auth URL
            if st.button("🔐 Войти через Google", type="primary"):
                auth_url = generate_auth_url()
                st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
                st.write(f"Перенаправляем на: {auth_url}")
        else:
            st.error("❌ OAuth не настроен")
    
    # Кнопка очистки URL
    if query_params:
        if st.button("🧹 Очистить URL"):
            st.query_params.clear()
            st.rerun()

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
    
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def process_oauth_code(code, state):
    """Обрабатывает OAuth код"""
    st.write("### 🔄 Обработка авторизации...")
    
    # Проверяем state
    if state != st.session_state.oauth_state:
        st.error(f"❌ State не совпадает: получен {state[:10]}..., ожидался {st.session_state.oauth_state[:10] if st.session_state.oauth_state else 'None'}...")
        return
    
    st.write("✅ State проверен")
    
    # Обмениваем код на токен
    st.write("🔄 Обмениваем код на токен...")
    
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        st.write(f"Token request status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            st.write("✅ Токен получен!")
            
            access_token = token_data.get('access_token')
            if access_token:
                st.write("🔄 Получаем данные пользователя...")
                
                # Получаем пользователя
                headers = {'Authorization': f'Bearer {access_token}'}
                user_response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
                
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    st.write("✅ Пользователь получен!")
                    
                    st.json(user_info)
                    
                    # Сохраняем в session
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    
                    st.success("🎉 Авторизация завершена!")
                    
                    # Очищаем URL
                    if st.button("🚀 Перейти к приложению"):
                        st.query_params.clear()
                        st.rerun()
                        
                else:
                    st.error(f"❌ Ошибка получения пользователя: {user_response.status_code}")
                    st.code(user_response.text)
            else:
                st.error("❌ Access token не найден")
                st.json(token_data)
        else:
            st.error(f"❌ Ошибка токена: {response.status_code}")
            st.code(response.text)
            
    except Exception as e:
        st.error(f"❌ Исключение: {e}")

if __name__ == "__main__":
    main()
