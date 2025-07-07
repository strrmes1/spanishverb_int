import streamlit as st
import os

# Минимальный тест Railway routing
st.set_page_config(page_title="🔧 Railway Test", page_icon="🔧")

def main():
    st.title("🔧 Railway Routing Test")
    
    # Тест 1: Базовая работа Streamlit
    st.success("✅ Streamlit работает на Railway!")
    
    # Тест 2: Query параметры
    st.markdown("## 📋 Query Parameters Test")
    
    try:
        params = dict(st.query_params)
        if params:
            st.success(f"✅ Query параметры найдены: {params}")
        else:
            st.info("ℹ️ Query параметры отсутствуют")
        
        st.write(f"**Количество параметров:** {len(params)}")
        st.write(f"**Тип объекта:** {type(st.query_params)}")
        
    except Exception as e:
        st.error(f"❌ Ошибка query_params: {e}")
    
    # Тест 3: Создаем тестовые ссылки
    st.markdown("## 🔗 Тестовые ссылки")
    
    base_url = "https://spanishverbint-production.up.railway.app"
    
    test_links = [
        f"{base_url}?test=simple",
        f"{base_url}?code=test_code&state=test_state",
        f"{base_url}?param1=value1&param2=value2",
        f"{base_url}/auth/callback?code=fake_code&state=fake_state"
    ]
    
    st.write("**Нажмите на ссылки для тестирования routing:**")
    
    for i, link in enumerate(test_links, 1):
        st.markdown(f"**Тест {i}:** [Открыть]({link})")
        st.code(link)
    
    # Тест 4: JavaScript URL тест
    st.markdown("## 🌐 JavaScript URL Test")
    
    st.components.v1.html("""
    <div style="padding: 20px; background: #f0f8ff; border-radius: 10px; margin: 10px 0;">
        <h4>🔍 JavaScript URL диагностика:</h4>
        <p><strong>Full URL:</strong> <span id="js-url">Loading...</span></p>
        <p><strong>Search:</strong> <span id="js-search">Loading...</span></p>
        <p><strong>Parameters:</strong></p>
        <pre id="js-params" style="background: white; padding: 10px; border-radius: 5px;">Loading...</pre>
        
        <button onclick="testURL()" style="margin-top: 10px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🔄 Refresh URL Info
        </button>
    </div>
    
    <script>
    function updateURLInfo() {
        try {
            const url = window.location.href;
            const search = window.location.search;
            
            document.getElementById('js-url').textContent = url;
            document.getElementById('js-search').textContent = search || '(empty)';
            
            // Parse parameters
            const params = new URLSearchParams(search);
            const paramsObj = {};
            for (const [key, value] of params) {
                paramsObj[key] = value;
            }
            
            document.getElementById('js-params').textContent = JSON.stringify(paramsObj, null, 2);
            
            console.log('URL Info Update:', { url, search, params: paramsObj });
            
        } catch (error) {
            console.error('Error updating URL info:', error);
            document.getElementById('js-url').textContent = 'Error: ' + error.message;
        }
    }
    
    function testURL() {
        updateURLInfo();
        alert('URL info updated! Check console for details.');
    }
    
    // Auto-update on load
    updateURLInfo();
    
    // Update every 2 seconds
    setInterval(updateURLInfo, 2000);
    </script>
    """, height=250)
    
    # Тест 5: Environment variables
    st.markdown("## 🔧 Environment Test")
    
    st.write("**OAuth Variables:**")
    oauth_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'REDIRECT_URI']
    
    for var in oauth_vars:
        value = os.getenv(var, '')
        status = "✅ Set" if value else "❌ Missing"
        length = f"({len(value)} chars)" if value else ""
        st.write(f"**{var}:** {status} {length}")
    
    # Тест 6: Ручная навигация
    st.markdown("## 🎯 Ручное тестирование")
    
    st.write("**Инструкции:**")
    st.write("1. Скопируйте один из тестовых URL выше")
    st.write("2. Вставьте в новую вкладку браузера")
    st.write("3. Посмотрите, показываются ли параметры в JavaScript разделе")
    st.write("4. Проверьте, видит ли их Streamlit вверху страницы")
    
    # Кнопки управления
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reload Page"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Params"):
            try:
                st.query_params.clear()
                st.success("Parameters cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Clear failed: {e}")
    
    with col3:
        if st.button("📊 Show Session"):
            st.json(dict(st.session_state))
    
    # Результаты анализа
    st.markdown("## 📊 Анализ результатов")
    
    params = dict(st.query_params)
    
    if params:
        st.success("🎉 Railway правильно передает query параметры в Streamlit!")
        st.write("Проблема OAuth была в другом месте.")
    else:
        st.warning("⚠️ Query параметры не обнаружены")
        st.write("Возможные причины:")
        st.write("- URL не содержит параметры")
        st.write("- Railway не передает параметры")
        st.write("- Streamlit не может их прочитать")
        st.write("- Проблема с routing/proxy")

if __name__ == "__main__":
    main()
