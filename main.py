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
    get_current_language, set_language, t
)

# Конфигурация
st.set_page_config(
    page_title="Spanish Verb Trainer",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ... (здесь остается весь существующий код с классами, данными глаголов, etc.)

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

def show_verb_card():
    """Показывает карточку глагола с поддержкой языков"""
    card = st.session_state.current_card
    
    if (card.verb not in VERBS or 
        card.tense not in CONJUGATIONS or 
        card.verb not in CONJUGATIONS[card.tense]):
        st.error(t('card_data_corrupted'))
        next_card()
        return
    
    verb_info = VERBS[card.verb]
    is_revealed = st.session_state.is_revealed
    
    # Отображаем карточку
    if not is_revealed:
        # Красивая кликабельная карточка с вопросом
        st.markdown(f"""
        <div class="verb-card">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {t(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]}
            </div>
            <div class="click-hint">
                {t('click_to_reveal')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопка для показа ответа - делаем шире
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            if st.button(t('show_answer'), type="primary", use_container_width=True):
                st.session_state.is_revealed = True
                st.rerun()
    else:
        # Показываем ответ
        conjugation = CONJUGATIONS[card.tense][card.verb][card.pronoun_index]
        
        st.markdown(f"""
        <div class="verb-card revealed">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {t(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]}
            </div>
            <div class="answer-display">
                ✅ {conjugation}
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
        
        **{t('honest_self_evaluation')}**
        - **{t('again')}** - {t('again_help').lower()}
        - **{t('hard')}** - {t('hard_help').lower()}
        - **{t('good')}** - {t('good_help').lower()}
        - **{t('easy')}** - {t('easy_help').lower()}
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

# Остальные функции остаются без изменений, только заменяем хардкод текстов на t() вызовы

# ... (остальной код без изменений)

if __name__ == "__main__":
    main()
