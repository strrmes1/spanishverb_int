# localization/translations.py
"""
Файл с переводами для всех языков
"""

TRANSLATIONS = {
    'ru': {
        # Основные элементы интерфейса
        'app_title': 'Тренажер испанских глаголов 🇪🇸',
        'welcome_subtitle': 'Изучайте спряжения с системой интервального повторения',
        'welcome_back': 'Добро пожаловать',
        
        # Авторизация
        'login_google': '🔐 Войти через Google',
        'processing_auth': '🔄 Обрабатываем авторизацию...',
        'auth_success': '🎉 Авторизация завершена успешно!',
        'auth_error': '❌ Ошибка при получении токена',
        'logout': '🚪 Выйти',
        'sync': '💾 Синхронизация',
        'synced': '✅ Синхронизировано!',
        
        # Основной интерфейс
        'show_answer': '🔍 Показать ответ',
        'next_verb': '➡️ Следующий глагол',
        'get_new_card': '🔄 Получить новую карточку',
        'click_to_reveal': '🔍 Нажмите на кнопку, чтобы увидеть ответ',
        
        # Оценка сложности
        'rate_difficulty': '🎯 Как хорошо вы знали ответ?',
        'honest_evaluation': 'Честная оценка поможет алгоритму лучше планировать повторения',
        'again': '❌ Снова\n(< 1 мин)',
        'hard': '😓 Сложно\n(< 10 мин)',
        'good': '😊 Хорошо\n(4 дня)',
        'easy': '😎 Легко\n(> 4 дней)',
        'again_help': 'Не помню вообще',
        'hard_help': 'Помню с трудом',
        'good_help': 'Помню уверенно',
        'easy_help': 'Помню мгновенно',
        
        # Статистика
        'stats_today': '📊 Сегодня',
        'stats_total': '📈 Всего',
        'reviews': 'Повторений',
        'correct': 'Правильных',
        'new_cards': 'Новых',
        'due_cards': 'К повторению',
        'accuracy': 'Точность',
        'total_cards': 'Карточек',
        'repetitions': 'Повторений',
        'interval': 'Интервал',
        'easiness': 'Легкость',
        'interval_days': 'дн.',
        
        # Настройки
        'settings': '⚙️ Настройки',
        'language': '🌐 Язык',
        'new_cards_per_day': 'Новых карточек в день',
        'selected_tenses': 'Выберите времена для изучения',
        'apply_settings': '✅ Применить настройки',
        'settings_applied': '✅ Настройки применены!',
        'change_settings_hint': '💡 Измените настройки выше, чтобы появилась кнопка применения',
        
        # Времена глаголов
        'presente': 'Presente',
        'indefinido': 'Pretérito Indefinido',
        'subjuntivo': 'Subjuntivo',
        'imperfecto': 'Imperfecto',
        
        # Сообщения
        'completed_today': '🎉 Отлично! Вы завершили все повторения на сегодня!',
        'come_back_tomorrow': 'Возвращайтесь завтра для новых карточек или измените настройки в боковой панели.',
        'card_data_corrupted': '❌ Данные карточки повреждены',
        
        # Правила грамматики
        'grammar_rules': '📚 Правила спряжения',
        'study_tips': '💡 Советы по эффективному изучению',
        
        # Преимущества (для страницы приветствия)
        'smart_repetition': '🧠 Умное повторение',
        'smart_repetition_desc': 'Алгоритм SM-2 показывает карточки именно тогда, когда вы готовы их забыть',
        'detailed_stats': '📊 Детальная статистика', 
        'detailed_stats_desc': 'Отслеживайте прогресс по каждому глаголу и времени отдельно',
        'cloud_sync': '☁️ Облачное сохранение',
        'cloud_sync_desc': 'Изучайте на любом устройстве, прогресс синхронизируется автоматически',
        
        # Советы по изучению
        'srs_principles': '🧠 Принципы интервального повторения',
        'daily_practice': '📅 Рекомендуемый режим изучения',
        'srs_how_it_works': 'Как работает система:',
        'srs_before_forget': 'Карточки показываются **прямо перед тем, как вы их забудете**',
        'srs_increasing_intervals': '**Увеличивающиеся интервалы** при правильных ответах',
        'srs_more_frequent': '**Чаще повторяются** при неправильных ответах',
        'honest_self_evaluation': 'Честная самооценка - ключ к успеху:',
        'daily_practice_text': 'Ежедневная практика:',
        'daily_better': '**10-20 минут** каждый день лучше, чем 2 часа раз в неделю',
        'regularity_important': '**Регулярность** важнее продолжительности',
        'same_time_helps': '**Одно и то же время** помогает выработать привычку',
        'optimal_settings': 'Оптимальные настройки:',
        'beginners_settings': '*Начинающие*: 5-10 новых карточек, 20-50 повторений, только Presente',
        'advanced_settings': '*Продвинутые*: 15-25 новых карточек, 100+ повторений, все времена',
    },
    
    'en': {
        # Main interface elements
        'app_title': 'Spanish Verb Trainer 🇪🇸',
        'welcome_subtitle': 'Learn conjugations with spaced repetition system',
        'welcome_back': 'Welcome back',
        
        # Authentication
        'login_google': '🔐 Login with Google',
        'processing_auth': '🔄 Processing authorization...',
        'auth_success': '🎉 Authorization completed successfully!',
        'auth_error': '❌ Error getting token',
        'logout': '🚪 Logout',
        'sync': '💾 Sync',
        'synced': '✅ Synced!',
        
        # Main interface
        'show_answer': '🔍 Show answer',
        'next_verb': '➡️ Next verb',
        'get_new_card': '🔄 Get new card',
        'click_to_reveal': '🔍 Click the button to see the answer',
        
        # Difficulty rating
        'rate_difficulty': '🎯 How well did you know the answer?',
        'honest_evaluation': 'Honest evaluation helps the algorithm plan better repetitions',
        'again': '❌ Again\n(< 1 min)',
        'hard': '😓 Hard\n(< 10 min)',
        'good': '😊 Good\n(4 days)',
        'easy': '😎 Easy\n(> 4 days)',
        'again_help': "Don't remember at all",
        'hard_help': 'Remember with difficulty',
        'good_help': 'Remember confidently',
        'easy_help': 'Remember instantly',
        
        # Statistics
        'stats_today': '📊 Today',
        'stats_total': '📈 Total',
        'reviews': 'Reviews',
        'correct': 'Correct',
        'new_cards': 'New',
        'due_cards': 'Due',
        'accuracy': 'Accuracy',
        'total_cards': 'Cards',
        'repetitions': 'Reviews',
        'interval': 'Interval',
        'easiness': 'Ease',
        'interval_days': 'days',
        
        # Settings
        'settings': '⚙️ Settings',
        'language': '🌐 Language',
        'new_cards_per_day': 'New cards per day',
        'selected_tenses': 'Select tenses to study',
        'apply_settings': '✅ Apply settings',
        'settings_applied': '✅ Settings applied!',
        'change_settings_hint': '💡 Change settings above to see the apply button',
        
        # Verb tenses
        'presente': 'Present',
        'indefinido': 'Preterite',
        'subjuntivo': 'Subjunctive',
        'imperfecto': 'Imperfect',
        
        # Messages
        'completed_today': '🎉 Great! You completed all reviews for today!',
        'come_back_tomorrow': 'Come back tomorrow for new cards or change settings in the sidebar.',
        'card_data_corrupted': '❌ Card data is corrupted',
        
        # Grammar rules
        'grammar_rules': '📚 Conjugation rules',
        'study_tips': '💡 Effective study tips',
        
        # Benefits (for welcome page)
        'smart_repetition': '🧠 Smart repetition',
        'smart_repetition_desc': 'SM-2 algorithm shows cards exactly when you are about to forget them',
        'detailed_stats': '📊 Detailed statistics',
        'detailed_stats_desc': 'Track progress for each verb and tense separately',
        'cloud_sync': '☁️ Cloud sync',
        'cloud_sync_desc': 'Study on any device, progress syncs automatically',
        
        # Study tips
        'srs_principles': '🧠 Spaced repetition principles',
        'daily_practice': '📅 Recommended study routine',
        'srs_how_it_works': 'How the system works:',
        'srs_before_forget': 'Cards are shown **right before you forget them**',
        'srs_increasing_intervals': '**Increasing intervals** for correct answers',
        'srs_more_frequent': '**More frequent repetition** for incorrect answers',
        'honest_self_evaluation': 'Honest self-evaluation is the key to success:',
        'daily_practice_text': 'Daily practice:',
        'daily_better': '**10-20 minutes** every day is better than 2 hours once a week',
        'regularity_important': '**Regularity** is more important than duration',
        'same_time_helps': '**Same time** helps build a habit',
        'optimal_settings': 'Optimal settings:',
        'beginners_settings': '*Beginners*: 5-10 new cards, 20-50 reviews, Present only',
        'advanced_settings': '*Advanced*: 15-25 new cards, 100+ reviews, all tenses',
    }
#______________________________


# Переводы глаголов на разные языки
VERB_TRANSLATIONS = {
    'ru': {
        'ser': 'быть, являться',
        'estar': 'находиться, быть',
        'tener': 'иметь',
        'hacer': 'делать',
        'decir': 'говорить, сказать',
        'ir': 'идти, ехать',
        'ver': 'видеть',
        'dar': 'давать',
        'saber': 'знать',
        'querer': 'хотеть, любить',
        'llegar': 'прибывать, приходить',
        'pasar': 'проходить, проводить',
        'deber': 'быть должным',
        'poner': 'класть, ставить',
        'parecer': 'казаться',
        'quedar': 'оставаться',
        'creer': 'верить, считать',
        'hablar': 'говорить',
        'llevar': 'носить, нести',
        'dejar': 'оставлять',
        'seguir': 'следовать, продолжать',
        'encontrar': 'находить, встречать',
        'llamar': 'звать, называть',
        'venir': 'приходить',
        'pensar': 'думать',
        'salir': 'выходить',
        'vivir': 'жить',
        'sentir': 'чувствовать',
        'trabajar': 'работать',
        'estudiar': 'изучать',
        'comprar': 'покупать',
        'comer': 'есть',
        'beber': 'пить',
        'escribir': 'писать',
        'leer': 'читать',
        'abrir': 'открывать',
        'cerrar': 'закрывать',
        'empezar': 'начинать',
        'terminar': 'заканчивать',
        'poder': 'мочь'
    },
    'en': {
        'ser': 'to be (permanent)',
        'estar': 'to be (temporary)',
        'tener': 'to have',
        'hacer': 'to do, to make',
        'decir': 'to say, to tell',
        'ir': 'to go',
        'ver': 'to see',
        'dar': 'to give',
        'saber': 'to know (facts)',
        'querer': 'to want, to love',
        'llegar': 'to arrive, to come',
        'pasar': 'to pass, to spend time',
        'deber': 'to owe, must',
        'poner': 'to put, to place',
        'parecer': 'to seem, to appear',
        'quedar': 'to stay, to remain',
        'creer': 'to believe, to think',
        'hablar': 'to speak, to talk',
        'llevar': 'to carry, to wear',
        'dejar': 'to leave, to let',
        'seguir': 'to follow, to continue',
        'encontrar': 'to find, to meet',
        'llamar': 'to call, to name',
        'venir': 'to come',
        'pensar': 'to think',
        'salir': 'to leave, to go out',
        'vivir': 'to live',
        'sentir': 'to feel',
        'trabajar': 'to work',
        'estudiar': 'to study',
        'comprar': 'to buy',
        'comer': 'to eat',
        'beber': 'to drink',
        'escribir': 'to write',
        'leer': 'to read',
        'abrir': 'to open',
        'cerrar': 'to close',
        'empezar': 'to begin, to start',
        'terminar': 'to finish, to end',
        'poder': 'to be able to, can'
    }
}

def get_verb_translation(verb: str, language: str = None) -> str:
    """
    Получить перевод глагола на указанном языке
    
    Args:
        verb: Инфинитив глагола
        language: Код языка ('ru' или 'en')
    
    Returns:
        Перевод глагола или сам глагол если перевод не найден
    """
    if language is None:
        language = get_current_language()
    
    if language not in VERB_TRANSLATIONS:
        language = 'ru'  # Fallback на русский
    
    return VERB_TRANSLATIONS[language].get(verb, verb)

# Обновите функцию show_verb_card в main файле:

def show_verb_card():
    """Показывает карточку глагола с поддержкой языков"""
    card = st.session_state.current_card
    
    if (card.verb not in VERBS or 
        card.tense not in CONJUGATIONS or 
        card.verb not in CONJUGATIONS[card.tense]):
        st.error(t('card_data_corrupted'))
        next_card()
        return
    
    # ИСПРАВЛЕНИЕ: Используем get_verb_translation вместо verb_info['translation']
    verb_translation = get_verb_translation(card.verb)
    is_revealed = st.session_state.is_revealed
    
    # Отображаем карточку
    if not is_revealed:
        # Красивая кликабельная карточка с вопросом
        st.markdown(f"""
        <div class="verb-card">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_translation}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {t(card.tense)}
            </div>
            <div class="pronoun-display">
                {PRONOUNS[card.pronoun_index]}
            </div>
            
hint">

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
            <div class="verb-translation">{verb_translation}</div>
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

# ТАКЖЕ нужно удалить/обновить старую структуру VERBS:

# Старая структура (можно упростить, оставив только type):
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

#______________________________    

    
}

# Правила грамматики
GRAMMAR_RULES = {
    'ru': {
        'presente': {
            'title': 'Настоящее время (Presente de Indicativo)',
            'content': '''
**Правильные глаголы -AR:**
Основа + -o, -as, -a, -amos, -áis, -an
*Ejemplo: hablar → hablo, hablas, habla, hablamos, habláis, hablan*

**Правильные глаголы -ER:**
Основа + -o, -es, -e, -emos, -éis, -en
*Ejemplo: comer → como, comes, come, comemos, coméis, comen*

**Правильные глаголы -IR:**
Основа + -o, -es, -e, -imos, -ís, -en
*Ejemplo: vivir → vivo, vives, vive, vivimos, vivís, viven*

**Неправильные глаголы** имеют особые формы спряжения.
            '''
        },
        'indefinido': {
            'title': 'Прошедшее время (Pretérito Indefinido)',
            'content': '''
**Правильные глаголы -AR:**
Основа + -é, -aste, -ó, -amos, -asteis, -aron
*Ejemplo: hablar → hablé, hablaste, habló, hablamos, hablasteis, hablaron*

**Правильные глаголы -ER/-IR:**
Основа + -í, -iste, -ió, -imos, -isteis, -ieron
*Ejemplo: comer → comí, comiste, comió, comimos, comisteis, comieron*

**Использование:** Завершенные действия в прошлом, конкретные моменты времени.
            '''
        },
        'subjuntivo': {
            'title': 'Сослагательное наклонение (Subjuntivo Presente)',
            'content': '''
**Глаголы -AR:**
Основа + -e, -es, -e, -emos, -éis, -en
*Ejemplo: hablar → hable, hables, hable, hablemos, habléis, hablen*

**Глаголы -ER/-IR:**
Основа + -a, -as, -a, -amos, -áis, -an
*Ejemplo: comer → coma, comas, coma, comamos, comáis, coman*

**Использование:** Сомнения, желания, эмоции, нереальные ситуации.
            '''
        },
        'imperfecto': {
            'title': 'Прошедшее несовершенное время (Pretérito Imperfecto)',
            'content': '''
**Глаголы -AR:**
Основа + -aba, -abas, -aba, -ábamos, -abais, -aban
*Ejemplo: hablar → hablaba, hablabas, hablaba, hablábamos, hablabais, hablaban*

**Глаголы -ER/-IR:**
Основа + -ía, -ías, -ía, -íamos, -íais, -ían
*Ejemplo: vivir → vivía, vivías, vivía, vivíamos, vivíais, vivían*

**Использование:** Повторяющиеся действия в прошлом, описания, привычки.
            '''
        }
    },
    
    'en': {
        'presente': {
            'title': 'Present Tense (Presente de Indicativo)',
            'content': '''
**Regular -AR verbs:**
Stem + -o, -as, -a, -amos, -áis, -an
*Example: hablar → hablo, hablas, habla, hablamos, habláis, hablan*

**Regular -ER verbs:**
Stem + -o, -es, -e, -emos, -éis, -en
*Example: comer → como, comes, come, comemos, coméis, comen*

**Regular -IR verbs:**
Stem + -o, -es, -e, -imos, -ís, -en
*Example: vivir → vivo, vives, vive, vivimos, vivís, viven*

**Irregular verbs** have special conjugation forms.
            '''
        },
        'indefinido': {
            'title': 'Past Tense (Pretérito Indefinido)',
            'content': '''
**Regular -AR verbs:**
Stem + -é, -aste, -ó, -amos, -asteis, -aron
*Example: hablar → hablé, hablaste, habló, hablamos, hablasteis, hablaron*

**Regular -ER/-IR verbs:**
Stem + -í, -iste, -ió, -imos, -isteis, -ieron
*Example: comer → comí, comiste, comió, comimos, comisteis, comieron*

**Usage:** Completed actions in the past, specific moments in time.
            '''
        },
        'subjuntivo': {
            'title': 'Subjunctive Mood (Subjuntivo Presente)',
            'content': '''
**-AR verbs:**
Stem + -e, -es, -e, -emos, -éis, -en
*Example: hablar → hable, hables, hable, hablemos, habléis, hablen*

**-ER/-IR verbs:**
Stem + -a, -as, -a, -amos, -áis, -an
*Example: comer → coma, comas, coma, comamos, comáis, coman*

**Usage:** Doubts, desires, emotions, unreal situations.
            '''
        },
        'imperfecto': {
            'title': 'Imperfect Past (Pretérito Imperfecto)',
            'content': '''
**-AR verbs:**
Stem + -aba, -abas, -aba, -ábamos, -abais, -aban
*Example: hablar → hablaba, hablabas, hablaba, hablábamos, hablabais, hablaban*

**-ER/-IR verbs:**
Stem + -ía, -ías, -ía, -íamos, -íais, -ían
*Example: vivir → vivía, vivías, vivía, vivíamos, vivíais, vivían*

**Usage:** Repeated actions in the past, descriptions, habits.
            '''
        }
    }
}

def get_text(key: str, language: str = 'ru') -> str:
    """
    Получить перевод по ключу
    
    Args:
        key: Ключ перевода (может быть вложенным через точку)
        language: Код языка ('ru' или 'en')
    
    Returns:
        Переведенный текст или ключ если перевод не найден
    """
    if language not in TRANSLATIONS:
        language = 'ru'  # Fallback на русский
    
    translations = TRANSLATIONS[language]
    
    # Поддержка вложенных ключей (например "stats.today")
    keys = key.split('.')
    value = translations
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        # Если перевод не найден, возвращаем ключ
        return f"[{key}]"

def get_grammar_rule(tense: str, language: str = 'ru') -> dict:
    """
    Получить правило грамматики для времени
    
    Args:
        tense: Время глагола
        language: Код языка
    
    Returns:
        Словарь с title и content
    """
    if language not in GRAMMAR_RULES:
        language = 'ru'
    
    return GRAMMAR_RULES[language].get(tense, {
        'title': f'[{tense}]',
        'content': 'Grammar rule not found'
    })

def get_available_languages() -> dict:
    """Получить список доступных языков"""
    return {
        'ru': '🇷🇺 Русский',
        'en': '🇺🇸 English'
    }

def get_current_language() -> str:
    """Получить текущий язык из session_state"""
    import streamlit as st
    return st.session_state.get('interface_language', 'ru')

def set_language(language_code: str):
    """Установить язык интерфейса"""
    import streamlit as st
    if language_code in get_available_languages():
        st.session_state.interface_language = language_code
    else:
        st.session_state.interface_language = 'ru'

# Сокращенная функция для удобства
def t(key: str, language: str = None) -> str:
    """Сокращенная функция перевода"""
    if language is None:
        language = get_current_language()
    return get_text(key, language)
