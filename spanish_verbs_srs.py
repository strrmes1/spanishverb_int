# main.py - Основной файл с интеграцией локализации

import streamlit as st
import os
import requests
from urllib.parse import urlencode
import base64
import datetime
import time
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Импортируем систему переводов
from localization.translations import (
    get_text, get_grammar_rule, get_available_languages, 
    get_current_language, set_language, t, get_verb_translation
)

# Конфигурация
st.set_page_config(
    page_title="Spanish Verb Trainer",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# OAuth настройки
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://spanishverbint-production.up.railway.app')

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# CSS стили
st.markdown("""
<style>
    .main > div {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    .main-content {
        max-width: 600px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .verb-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .verb-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.4);
    }
    
    .verb-card.revealed {
        background: linear-gradient(135deg, #48ca8b 0%, #2dd4bf 100%);
        box-shadow: 0 12px 40px rgba(72, 202, 139, 0.3);
    }
    
    .verb-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .verb-translation {
        font-size: 1.4rem;
        opacity: 0.9;
        margin-bottom: 1.5rem;
    }
    
    .pronoun-display {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 1.5rem 0;
        background: rgba(255,255,255,0.2);
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        display: inline-block;
    }
    
    .answer-display {
        font-size: 2.8rem;
        font-weight: bold;
        background: rgba(255,255,255,0.9);
        color: #2d5e3e;
        padding: 1.5rem 2rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        display: inline-block;
    }
    
    .user-panel {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .click-hint {
        font-size: 1.2rem;
        margin-top: 1rem;
        opacity: 0.8;
        animation: pulse-gentle 2s infinite;
    }
    
    @keyframes pulse-gentle {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# Перечисления для SRS
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

# База данных глаголов
VERBS = {
    'ser': {'type': 'irregular'},
    'estar': {'type': 'irregular'},
    'tener': {'type': 'irregular'},
    'hacer': {'type': 'irregular'},
    'decir': {'type': 'irregular'},
    'ir': {'type': 'irregular'},
    'ver': {'type': 'irregular'},
    'dar': {'type': 'irregular'},
    'saber': {'type': 'irregular'},
    'querer': {'type': 'irregular'},
    'llegar': {'type': 'regular-ar'},
    'pasar': {'type': 'regular-ar'},
    'deber': {'type': 'regular-er'},
    'poner': {'type': 'irregular'},
    'parecer': {'type': 'irregular'},
    'quedar': {'type': 'regular-ar'},
    'creer': {'type': 'regular-er'},
    'hablar': {'type': 'regular-ar'},
    'llevar': {'type': 'regular-ar'},
    'dejar': {'type': 'regular-ar'},
    'seguir': {'type': 'irregular'},
    'encontrar': {'type': 'irregular'},
    'llamar': {'type': 'regular-ar'},
    'venir': {'type': 'irregular'},
    'pensar': {'type': 'irregular'},
    'salir': {'type': 'irregular'},
    'vivir': {'type': 'regular-ir'},
    'sentir': {'type': 'irregular'},
    'trabajar': {'type': 'regular-ar'},
    'estudiar': {'type': 'regular-ar'},
    'comprar': {'type': 'regular-ar'},
    'comer': {'type': 'regular-er'},
    'beber': {'type': 'regular-er'},
    'escribir': {'type': 'regular-ir'},
    'leer': {'type': 'regular-er'},
    'abrir': {'type': 'irregular'},
    'cerrar': {'type': 'irregular'},
    'empezar': {'type': 'irregular'},
    'terminar': {'type': 'regular-ar'},
    'poder': {'type': 'irregular'}
}

PRONOUNS = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']

# Спряжения глаголов
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
        'llegar': ['llego', 'llegas', 'llega', 'llegamos', 'llegáis', 'llegan'],
        'pasar': ['paso', 'pasas', 'pasa', 'pasamos', 'pasáis', 'pasan'],
        'deber': ['debo', 'debes', 'debe', 'debemos', 'debéis', 'deben'],
        'poner': ['pongo', 'pones', 'pone', 'ponemos', 'ponéis', 'ponen'],
        'parecer': ['parezco', 'pareces', 'parece', 'parecemos', 'parecéis', 'parecen'],
        'quedar': ['quedo', 'quedas', 'queda', 'quedamos', 'quedáis', 'quedan'],
        'creer': ['creo', 'crees', 'cree', 'creemos', 'creéis', 'creen'],
        'hablar': ['hablo', 'hablas', 'habla', 'hablamos', 'habláis', 'hablan'],
        'llevar': ['llevo', 'llevas', 'lleva', 'llevamos', 'lleváis', 'llevan'],
        'dejar': ['dejo', 'dejas', 'deja', 'dejamos', 'dejáis', 'dejan'],
        'seguir': ['sigo', 'sigues', 'sigue', 'seguimos', 'seguís', 'siguen'],
        'encontrar': ['encuentro', 'encuentras', 'encuentra', 'encontramos', 'encontráis', 'encuentran'],
        'llamar': ['llamo', 'llamas', 'llama', 'llamamos', 'llamáis', 'llaman'],
        'venir': ['vengo', 'vienes', 'viene', 'venimos', 'venís', 'vienen'],
        'pensar': ['pienso', 'piensas', 'piensa', 'pensamos', 'pensáis', 'piensan'],
        'salir': ['salgo', 'sales', 'sale', 'salimos', 'salís', 'salen'],
        'vivir': ['vivo', 'vives', 'vive', 'vivimos', 'vivís', 'viven'],
        'sentir': ['siento', 'sientes', 'siente', 'sentimos', 'sentís', 'sienten'],
        'trabajar': ['trabajo', 'trabajas', 'trabaja', 'trabajamos', 'trabajáis', 'trabajan'],
        'estudiar': ['estudio', 'estudias', 'estudia', 'estudiamos', 'estudiáis', 'estudian'],
        'comprar': ['compro', 'compras', 'compra', 'compramos', 'compráis', 'compran'],
        'comer': ['como', 'comes', 'come', 'comemos', 'coméis', 'comen'],
        'beber': ['bebo', 'bebes', 'bebe', 'bebemos', 'bebéis', 'beben'],
        'escribir': ['escribo', 'escribes', 'escribe', 'escribimos', 'escribís', 'escriben'],
        'leer': ['leo', 'lees', 'lee', 'leemos', 'leéis', 'leen'],
        'abrir': ['abro', 'abres', 'abre', 'abrimos', 'abrís', 'abren'],
        'cerrar': ['cierro', 'cierras', 'cierra', 'cerramos', 'cerráis', 'cierran'],
        'empezar': ['empiezo', 'empiezas', 'empieza', 'empezamos', 'empezáis', 'empiezan'],
        'terminar': ['termino', 'terminas', 'termina', 'terminamos', 'termináis', 'terminan'],
        'poder': ['puedo', 'puedes', 'puede', 'podemos', 'podéis', 'pueden']
    },
    'indefinido': {
        'ser': ['fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron'],
        'estar': ['estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron'],
        'tener': ['tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 'tuvieron'],
        'hacer': ['hice', 'hiciste', 'hizo', 'hicimos', 'hicisteis', 'hicieron'],
        'decir': ['dije', 'dijiste', 'dijo', 'dijimos', 'dijisteis', 'dijeron'],
        'ir': ['fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron'],
        'ver': ['vi', 'viste', 'vio', 'vimos', 'visteis', 'vieron'],
        'dar': ['di', 'diste', 'dio', 'dimos', 'disteis', 'dieron'],
        'saber': ['supe', 'supiste', 'supo', 'supimos', 'supisteis', 'supieron'],
        'querer': ['quise', 'quisiste', 'quiso', 'quisimos', 'quisisteis', 'quisieron'],
        'llegar': ['llegué', 'llegaste', 'llegó', 'llegamos', 'llegasteis', 'llegaron'],
        'pasar': ['pasé', 'pasaste', 'pasó', 'pasamos', 'pasasteis', 'pasaron'],
        'deber': ['debí', 'debiste', 'debió', 'debimos', 'debisteis', 'debieron'],
        'poner': ['puse', 'pusiste', 'puso', 'pusimos', 'pusisteis', 'pusieron'],
        'parecer': ['parecí', 'pareciste', 'pareció', 'parecimos', 'parecisteis', 'parecieron'],
        'quedar': ['quedé', 'quedaste', 'quedó', 'quedamos', 'quedasteis', 'quedaron'],
        'creer': ['creí', 'creíste', 'creyó', 'creímos', 'creísteis', 'creyeron'],
        'hablar': ['hablé', 'hablaste', 'habló', 'hablamos', 'hablasteis', 'hablaron'],
        'trabajar': ['trabajé', 'trabajaste', 'trabajó', 'trabajamos', 'trabajasteis', 'trabajaron'],
        'estudiar': ['estudié', 'estudiaste', 'estudió', 'estudiamos', 'estudiasteis', 'estudiaron'],
        'poder': ['pude', 'pudiste', 'pudo', 'pudimos', 'pudisteis', 'pudieron']
    },
    'subjuntivo': {
        'ser': ['sea', 'seas', 'sea', 'seamos', 'seáis', 'sean'],
        'estar': ['esté', 'estés', 'esté', 'estemos', 'estéis', 'estén'],
        'tener': ['tenga', 'tengas', 'tenga', 'tengamos', 'tengáis', 'tengan'],
        'hacer': ['haga', 'hagas', 'haga', 'hagamos', 'hagáis', 'hagan'],
        'decir': ['diga', 'digas', 'diga', 'digamos', 'digáis', 'digan'],
        'ir': ['vaya', 'vayas', 'vaya', 'vayamos', 'vayáis', 'vayan'],
        'ver': ['vea', 'veas', 'vea', 'veamos', 'veáis', 'vean'],
        'dar': ['dé', 'des', 'dé', 'demos', 'deis', 'den'],
        'saber': ['sepa', 'sepas', 'sepa', 'sepamos', 'sepáis', 'sepan'],
        'querer': ['quiera', 'quieras', 'quiera', 'queramos', 'queráis', 'quieran'],
        'hablar': ['hable', 'hables', 'hable', 'hablemos', 'habléis', 'hablen'],
        'trabajar': ['trabaje', 'trabajes', 'trabaje', 'trabajemos', 'trabajéis', 'trabajen'],
        'poder': ['pueda', 'puedas', 'pueda', 'podamos', 'podáis', 'puedan']
    },
    'imperfecto': {
        'ser': ['era', 'eras', 'era', 'éramos', 'erais', 'eran'],
        'estar': ['estaba', 'estabas', 'estaba', 'estábamos', 'estabais', 'estaban'],
        'tener': ['tenía', 'tenías', 'tenía', 'teníamos', 'teníais', 'tenían'],
        'hacer': ['hacía', 'hacías', 'hacía', 'hacíamos', 'hacíais', 'hacían'],
        'ir': ['iba', 'ibas', 'iba', 'íbamos', 'ibais', 'iban'],
        'ver': ['veía', 'veías', 'veía', 'veíamos', 'veíais', 'veían'],
        'hablar': ['hablaba', 'hablabas', 'hablaba', 'hablábamos', 'hablabais', 'hablaban'],
        'trabajar': ['trabajaba', 'trabajabas', 'trabajaba', 'trabajábamos', 'trabajabais', 'trabajaban'],
        'vivir': ['vivía', 'vivías', 'vivía', 'vivíamos', 'vivíais', 'vivían'],
        'poder': ['podía', 'podías', 'podía', 'podíamos', 'podíais', 'podían']
    }
}

# Система интервального повторения (SRS)
class SRSManager:
    @staticmethod
    def calculate_next_interval(card: Card, difficulty: Difficulty) -> Tuple[int, float]:
        """Алгоритм SM-2 для расчета следующего интервала"""
        ef = card.easiness_factor
        interval = card.interval
        repetitions = card.repetitions
        
        if difficulty == Difficulty.AGAIN:
            return 1, max(1.3, ef - 0.2)
        
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ef)
        
        # Обновляем easiness factor
        if difficulty == Difficulty.EASY:
            ef = ef + 0.15
        elif difficulty == Difficulty.GOOD:
            ef = ef + 0.1
        elif difficulty == Difficulty.HARD:
            ef = ef - 0.15
        
        ef = max(1.3, min(3.0, ef))
        return interval, ef
    
    @staticmethod
    def update_card(card: Card, difficulty: Difficulty) -> Card:
        """Обновляет карточку после ответа"""
        today = datetime.date.today()
        
        card.total_reviews += 1
        if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
            card.correct_reviews += 1
        
        if difficulty == Difficulty.AGAIN:
            card.repetitions = 0
        else:
            card.repetitions += 1
        
        new_interval, new_ef = SRSManager.calculate_next_interval(card, difficulty)
        
        card.interval = new_interval
        card.easiness_factor = new_ef
        card.last_review_date = today.isoformat()
        card.next_review_date = (today + datetime.timedelta(days=new_interval)).isoformat()
        
        return card

def show_language_selector():
    """Показывает селектор языка в сайдбаре"""
    st.markdown("### " + t('language'))
    
    available_languages = get_available_languages()
    current_language = get_current_language()
    
    # Создаем selectbox для выбора языка
    selected_language = st.selectbox(
        label="Choose language",
        options=list(available_languages.keys()),
        format_func=lambda x: available_languages[x],
        index=list(available_languages.keys()).index(current_language),
        key="language_selector",
        label_visibility="collapsed"
    )
    
    # Если язык изменился, устанавливаем новый и перезагружаем
    if selected_language != current_language:
        set_language(selected_language)
        st.rerun()

def show_welcome_page():
    """Показывает страницу приветствия с поддержкой языков"""
    
    # Селектор языка в верхней части
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        show_language_selector()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 4rem; color: #2d3748; margin-bottom: 1rem;">
            {t('app_title')}
        </h1>
        <h3 style="color: #718096; font-weight: 400; margin-bottom: 3rem;">
            {t('welcome_subtitle')}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Преимущества
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 1rem; margin: 1rem 0; height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h3>{t('smart_repetition')}</h3>
            <p>{t('smart_repetition_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 1rem; margin: 1rem 0; height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h3>{t('detailed_stats')}</h3>
            <p>{t('detailed_stats_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 1rem; margin: 1rem 0; height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h3>{t('cloud_sync')}</h3>
            <p>{t('cloud_sync_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Кнопка входа
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Генерируем OAuth URL
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <button style="
                    background: linear-gradient(135deg, #4285f4, #34a853);
                    color: white;
                    padding: 1rem 3rem;
                    border: none;
                    border-radius: 25px;
                    font-size: 1.2rem;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
                    transition: all 0.3s ease;
                    width: 100%;
                " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    {t('login_google')}
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

def show_main_app():
    """Показывает основное приложение с поддержкой языков"""
    reset_daily_stats()
    
    user_info = st.session_state.user_info
    
    # Заголовок
    st.title(t('app_title'))
    st.caption(f"{t('welcome_back')}, {user_info.get('name')}! {t('welcome_subtitle')}")
    
    # Боковая панель
    with st.sidebar:
        show_user_panel()
        show_sidebar_content()
    
    # Основной интерфейс
    show_learning_interface()

def show_user_panel():
    """Показывает панель пользователя с поддержкой языков"""
    user_info = st.session_state.user_info
    
    st.markdown(f"""
    <div class="user-panel">
        <strong>👤 {user_info.get('name')}</strong><br>
        <small>{user_info.get('email')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('sync'), use_container_width=True):
            save_user_data()
            st.success(t('synced'))
    
    with col2:
        if st.button(t('logout'), use_container_width=True):
            logout()
            st.rerun()

def show_sidebar_content():
    """Показывает содержимое боковой панели с поддержкой языков"""
    
    # Селектор языка
    show_language_selector()
    st.markdown("---")
    
    # Настройки
    st.subheader(t('settings'))
    
    # Сохраняем текущие настройки для сравнения
    current_settings = {
        'selected_tenses': st.session_state.settings['selected_tenses'].copy(),
        'new_cards_per_day': st.session_state.settings['new_cards_per_day']
    }
    
    # Выбор времен
    tense_options = {
        'presente': t('presente'),
        'indefinido': t('indefinido'),
        'subjuntivo': t('subjuntivo'),
        'imperfecto': t('imperfecto')
    }
    
    # Временные переменные для новых настроек
    new_selected_tenses = []
    for tense_key, tense_name in tense_options.items():
        if st.checkbox(tense_name, value=tense_key in st.session_state.settings['selected_tenses'], key=f"tense_{tense_key}"):
            new_selected_tenses.append(tense_key)
    
    new_selected_tenses = new_selected_tenses or ['presente']
    
    # Лимиты
    new_cards_per_day = st.slider(
        t('new_cards_per_day'), 1, 50, st.session_state.settings['new_cards_per_day'], key="new_cards_slider"
    )
    
    # Проверяем, изменились ли настройки
    settings_changed = (
        current_settings['selected_tenses'] != new_selected_tenses or
        current_settings['new_cards_per_day'] != new_cards_per_day
    )
    
    # Кнопка применить (показывается только если настройки изменились)
    if settings_changed:
        if st.button(t('apply_settings'), key="apply_settings", use_container_width=True, type="primary"):
            # Применяем настройки
            st.session_state.settings['selected_tenses'] = new_selected_tenses
            st.session_state.settings['new_cards_per_day'] = new_cards_per_day
            
            # Сбрасываем текущую карточку чтобы обновить в соответствии с новыми настройками
            st.session_state.current_card = None
            st.session_state.is_revealed = False
            
            st.success(t('settings_applied'))
            st.rerun()
    elif st.session_state.settings['selected_tenses']:
        st.info(t('change_settings_hint'))
    
    st.markdown("---")
    
    # Статистика в боковой панели
    st.subheader(t('stats_today'))
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t('reviews'), st.session_state.daily_stats['reviews_today'])
        st.metric(t('new_cards'), st.session_state.daily_stats['new_cards_today'])
    with col2:
        st.metric(t('correct'), st.session_state.daily_stats['correct_today'])
        due_count = len(get_due_cards())
        st.metric(t('due_cards'), due_count)
    
    # Общая статистика
    total_cards = len(st.session_state.cards)
    total_reviews = sum(card.total_reviews for card in st.session_state.cards.values())
    total_correct = sum(card.correct_reviews for card in st.session_state.cards.values())
    accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
    
    st.subheader(t('stats_total'))
    st.metric(t('total_cards'), total_cards)
    st.metric(t('accuracy'), f"{accuracy:.1f}%")

 def speak_btn(text, size="35px"):
        return f'''
        <button onclick="speak('{text}')" style="
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            width: {size};
            height: {size};
            margin-left: 8px;
            cursor: pointer;
            color: white;
            vertical-align: middle;
        ">🔊</button>
        '''
    
    if not is_revealed:
        st.markdown(f"""
        <div class="verb-card">
            <div class="verb-title">
                {card.verb} {speak_btn(card.verb, "40px")}
            </div>
            <div class="verb-translation">{verb_translation}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {t(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]} {speak_btn(PRONOUNS[card.pronoun_index])}
            </div>
            
hint">

                {t('click_to_reveal')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            if st.button(t('show_answer'), type="primary", use_container_width=True):
                st.session_state.is_revealed = True
                st.rerun()
    else:
        conjugation = CONJUGATIONS[card.tense][card.verb][card.pronoun_index]
        full_phrase = f"{PRONOUNS[card.pronoun_index]} {conjugation}"
        
        st.markdown(f"""
        <div class="verb-card revealed">
            <div class="verb-title">
                {card.verb} {speak_btn(card.verb, "40px")}
            </div>
            <div class="verb-translation">{verb_translation}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {t(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]} {speak_btn(PRONOUNS[card.pronoun_index])}
            </div>
            <div class="answer-display">
                ✓ {conjugation} {speak_btn(conjugation)}
                <br>
                <button onclick="speak('{full_phrase}')" style="
                    background: rgba(45, 94, 62, 0.2);
                    border: 1px solid rgba(45, 94, 62, 0.5);
                    border-radius: 20px;
                    padding: 8px 16px;
                    margin-top: 10px;
                    cursor: pointer;
                    color: #2d5e3e;
                    font-size: 0.9rem;
                ">🔊 Произнести фразу</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопки оценки сложности
        st.subheader(t('rate_difficulty'))
        st.caption(t('honest_evaluation'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(t('again'), key="again", use_container_width=True, help=t('again_help')):
                process_answer(Difficulty.AGAIN)
        
        with col2:
            if st.button(t('hard'), key="hard", use_container_width=True, help=t('hard_help')):
                process_answer(Difficulty.HARD)
        
        with col3:
            if st.button(t('good'), key="good", use_container_width=True, help=t('good_help')):
                process_answer(Difficulty.GOOD)
        
        with col4:
            if st.button(t('easy'), key="easy", use_container_width=True, help=t('easy_help')):
                process_answer(Difficulty.EASY)
    
    # Правила спряжения для выбранных времен
    st.markdown("---")
    st.subheader(t('grammar_rules'))
    
    current_lang = get_current_language()
    for tense in st.session_state.settings['selected_tenses']:
        rule = get_grammar_rule(tense, current_lang)
        with st.expander(f"{rule['title']}", expanded=False):
            st.markdown(rule['content'])
    
    # Советы по изучению - в самом низу
    if st.button(t('study_tips'), key="study_tips", use_container_width=True):
        show_study_tips()

def show_study_tips():
    """Показывает советы по эффективному изучению с поддержкой языков"""
    st.header(t('study_tips'))
    
    with st.expander(t('srs_principles'), expanded=True):
        st.markdown(f"""
        **{t('srs_how_it_works')}**
        - {t('srs_before_forget')}
        - {t('srs_increasing_intervals')}
        - {t('srs_more_frequent')}
        - **{t('honest_self_evaluation')}**
        """)
    
    with st.expander(t('daily_practice')):
        st.markdown(f"""
        **{t('daily_practice_text')}**
        - {t('daily_better')}
        - {t('regularity_important')}
        - {t('same_time_helps')}
        
        **{t('optimal_settings')}**
        - {t('beginners_settings')}
        - {t('advanced_settings')}
        """)

def show_learning_interface():
    """Показывает интерфейс изучения с поддержкой языков"""
    # Контейнер для более компактного интерфейса
    with st.container():
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Получаем следующую карточку
        if not st.session_state.current_card:
            st.session_state.current_card = get_next_card()
            st.session_state.is_revealed = False
        
        if not st.session_state.current_card:
            st.success(t('completed_today'))
            st.info(t('come_back_tomorrow'))
            
            if st.button(t('get_new_card')):
                force_new_card()
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Отображаем карточку
        show_verb_card()
        
        st.markdown('</div>', unsafe_allow_html=True)

def handle_oauth_callback(query_params):
    """Обрабатывает OAuth callback с поддержкой языков"""
    st.title(t('processing_auth'))
    
    code = query_params.get('code')
    state = query_params.get('state')
    error = query_params.get('error')
    
    if error:
        st.error(f"❌ OAuth Error: {error}")
        if st.button("🔄 " + t('login_google')):
            clear_oauth_and_reload()
        return
    
    # Обрабатываем код
    with st.spinner(t('processing_auth')):
        success = process_authorization_code(code)
        
        if success:
            st.success(t('auth_success'))
            time.sleep(1)
            clear_url_params()
            st.rerun()
        else:
            st.error(t('auth_error'))

def main():
    """Главная функция приложения"""
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
    # OAuth состояние
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    # Язык интерфейса
    if 'interface_language' not in st.session_state:
        st.session_state.interface_language = 'ru'
    
    # Состояние приложения
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
    if 'recent_combinations' not in st.session_state:
        st.session_state.recent_combinations = []

# Также нужно добавить все остальные функции, которые были в оригинальном коде:
# process_authorization_code, exchange_code_for_token, get_user_info, etc.

def validate_state_format(state):
    """Проверяет формат state"""
    try:
        decoded = base64.urlsafe_b64decode(state + '==')
        return len(decoded) == 32 and decoded.count(0) <= 5
    except:
        return False

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
        
        # Загружаем данные пользователя
        load_user_data()
        
        return True
    except Exception as e:
        st.error(f"❌ {t('auth_error')}: {e}")
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

def load_user_data():
    """Загружает данные пользователя (заглушка для будущей базы данных)"""
    # В будущем здесь будет загрузка из Firebase/Supabase
    pass

def save_user_data():
    """Сохраняет данные пользователя (заглушка для будущей базы данных)"""
    # В будущем здесь будет сохранение в Firebase/Supabase
    pass

def get_card_key(verb: str, pronoun_index: int, tense: str) -> str:
    """Генерирует ключ для карточки"""
    return f"{verb}_{pronoun_index}_{tense}"

def get_or_create_card(verb: str, pronoun_index: int, tense: str) -> Card:
    """Получает или создает карточку"""
    key = get_card_key(verb, pronoun_index, tense)
    
    if key not in st.session_state.cards:
        st.session_state.cards[key] = Card(
            verb=verb,
            pronoun_index=pronoun_index,
            tense=tense
        )
    
    return st.session_state.cards[key]

def get_due_cards() -> List[Card]:
    """Получает карточки для повторения"""
    today = datetime.date.today().isoformat()
    
    due_cards = []
    for card in st.session_state.cards.values():
        if (card.next_review_date <= today and 
            card.tense in st.session_state.settings['selected_tenses']):
            due_cards.append(card)
    
    return sorted(due_cards, key=lambda x: x.next_review_date)

def get_new_cards() -> List[Tuple[str, int, str]]:
    """Получает новые карточки"""
    new_cards = []
    existing_keys = set(st.session_state.cards.keys())
    
    for tense in st.session_state.settings['selected_tenses']:
        if tense not in CONJUGATIONS:
            continue
            
        for verb in CONJUGATIONS[tense]:
            if verb not in VERBS:
                continue
                
            for pronoun_index in range(6):
                key = get_card_key(verb, pronoun_index, tense)
                if key not in existing_keys:
                    new_cards.append((verb, pronoun_index, tense))
    
    random.shuffle(new_cards)
    return new_cards

def get_next_card() -> Optional[Card]:
    """Получает следующую карточку"""
    # Сначала карточки для повторения
    due_cards = get_due_cards()
    if due_cards:
        return due_cards[0]
    
    # Затем новые карточки
    if st.session_state.daily_stats['new_cards_today'] < st.session_state.settings['new_cards_per_day']:
        new_cards = get_new_cards()
        if new_cards:
            verb, pronoun_index, tense = new_cards[0]
            return get_or_create_card(verb, pronoun_index, tense)
    
    return None

def process_answer(difficulty: Difficulty):
    """Обрабатывает ответ пользователя"""
    if not st.session_state.current_card:
        return
    
    is_new_card = st.session_state.current_card.total_reviews == 0
    
    # Обновляем карточку с помощью SRS
    updated_card = SRSManager.update_card(st.session_state.current_card, difficulty)
    card_key = get_card_key(updated_card.verb, updated_card.pronoun_index, updated_card.tense)
    st.session_state.cards[card_key] = updated_card
    
    # Обновляем статистику
    st.session_state.daily_stats['reviews_today'] += 1
    if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
        st.session_state.daily_stats['correct_today'] += 1
    if is_new_card:
        st.session_state.daily_stats['new_cards_today'] += 1
    
    # Сохраняем данные
    save_user_data()
    
    # Переходим к следующей карточке
    next_card()

def next_card():
    """Переход к следующей карточке"""
    st.session_state.current_card = None
    st.session_state.is_revealed = False
    st.rerun()

def force_new_card():
    """Принудительно получает новую карточку"""
    new_cards = get_new_cards()
    if new_cards:
        verb, pronoun_index, tense = random.choice(new_cards)
        st.session_state.current_card = get_or_create_card(verb, pronoun_index, tense)
        st.session_state.is_revealed = False
        st.rerun()

def reset_daily_stats():
    """Сбрасывает дневную статистику"""
    today = datetime.date.today().isoformat()
    if st.session_state.daily_stats['last_reset'] != today:
        st.session_state.daily_stats.update({
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': today
        })

def clear_url_params():
    """Очищает URL параметры"""
    try:
        st.query_params.clear()
    except:
        pass

def clear_oauth_and_reload():
    """Очищает OAuth и перезагружает"""
    st.session_state.oauth_state = None
    clear_url_params()
    st.rerun()

def logout():
    """Выход из системы"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.oauth_state = None
    st.session_state.cards = {}
    st.session_state.current_card = None
    st.session_state.daily_stats = {
        'reviews_today': 0,
        'correct_today': 0,
        'new_cards_today': 0,
        'last_reset': datetime.date.today().isoformat()
    }

if __name__ == "__main__":
    main()
