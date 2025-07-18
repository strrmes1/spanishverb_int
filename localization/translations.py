# localization/translations.py
"""
Полный файл с переводами для всех языков с расширенным словарем (100 глаголов)
"""

import streamlit as st

# Основные переводы интерфейса
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
        
        # Размер словаря
        'vocabulary_size': '📚 Размер словаря',
        'verbs': 'глаголов',
        'current_vocabulary': 'Текущий словарь',
        'choose_vocabulary_size': '📚 Выберите размер словаря',
        
        # Варианты размера словаря
        'vocabulary_30': 'Базовый (30 глаголов)',
        'vocabulary_50': 'Средний (50 глаголов)',
        'vocabulary_100': 'Полный (100 глаголов)',
        
        # Описания размеров словаря
        'vocab_30_desc': 'Самые важные и часто используемые глаголы. Идеально для начинающих.',
        'vocab_50_desc': 'Расширенный набор популярных глаголов. Для продолжающих изучение.',
        'vocab_100_desc': 'Полный набор самых популярных испанских глаголов. Для серьезного изучения.',
        
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
        
        # Vocabulary size
        'vocabulary_size': '📚 Vocabulary size',
        'verbs': 'verbs',
        'current_vocabulary': 'Current vocabulary',
        'choose_vocabulary_size': '📚 Choose vocabulary size',
        
        # Vocabulary size options
        'vocabulary_30': 'Basic (30 verbs)',
        'vocabulary_50': 'Intermediate (50 verbs)',
        'vocabulary_100': 'Complete (100 verbs)',
        
        # Vocabulary size descriptions
        'vocab_30_desc': 'Most important and frequently used verbs. Perfect for beginners.',
        'vocab_50_desc': 'Extended set of popular verbs. For continuing learners.',
        'vocab_100_desc': 'Complete set of the most popular Spanish verbs. For serious study.',
        
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
}

# Переводы глаголов на разные языки (расширенный до 100 глаголов)
VERB_TRANSLATIONS = {
    'ru': {
        # Основные глаголы (1-30)
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
        'poder': 'мочь',
        'venir': 'приходить',
        'hablar': 'говорить',
        'vivir': 'жить',
        'comer': 'есть',
        'trabajar': 'работать',
        'estudiar': 'изучать',
        'llegar': 'прибывать, приходить',
        'pasar': 'проходить, проводить',
        'encontrar': 'находить, встречать',
        'llamar': 'звать, называть',
        'pensar': 'думать',
        'salir': 'выходить',
        'poner': 'класть, ставить',
        'seguir': 'следовать, продолжать',
        'llevar': 'носить, нести',
        'dejar': 'оставлять',
        'parecer': 'казаться',
        'quedar': 'оставаться',
        'creer': 'верить, считать',
        
        # Глаголы 31-50
        'conocer': 'знать (людей/места)',
        'sentir': 'чувствовать',
        'deber': 'быть должным',
        'entrar': 'входить',
        'escribir': 'писать',
        'leer': 'читать',
        'beber': 'пить',
        'comprar': 'покупать',
        'abrir': 'открывать',
        'cerrar': 'закрывать',
        'empezar': 'начинать',
        'terminar': 'заканчивать',
        'buscar': 'искать',
        'entender': 'понимать',
        'escuchar': 'слушать',
        'mirar': 'смотреть',
        'usar': 'использовать',
        'ayudar': 'помогать',
        'necesitar': 'нуждаться',
        'preguntar': 'спрашивать',
        
        # Глаголы 51-80
        'responder': 'отвечать',
        'jugar': 'играть',
        'dormir': 'спать',
        'ganar': 'выигрывать, зарабатывать',
        'perder': 'терять',
        'amar': 'любить',
        'cantar': 'петь',
        'bailar': 'танцевать',
        'tocar': 'трогать, играть (на инструменте)',
        'cambiar': 'менять',
        'mover': 'двигать',
        'caminar': 'ходить пешком',
        'correr': 'бегать',
        'subir': 'подниматься',
        'bajar': 'спускаться',
        'explicar': 'объяснять',
        'recordar': 'помнить',
        'olvidar': 'забывать',
        'aprender': 'учиться',
        'enseñar': 'учить',
        'viajar': 'путешествовать',
        'volar': 'летать',
        'conducir': 'водить машину',
        'cocinar': 'готовить',
        'lavar': 'мыть',
        'limpiar': 'чистить',
        'construir': 'строить',
        'romper': 'ломать',
        'crear': 'создавать',
        'imaginar': 'воображать',
        
        # Глаголы 81-100
        'soñar': 'мечтать, видеть сны',
        'despertar': 'просыпаться',
        'levantar': 'поднимать',
        'sentar': 'сажать',
        'acostar': 'укладывать спать',
        'vestir': 'одевать',
        'casar': 'жениться/выходить замуж',
        'nacer': 'рождаться',
        'morir': 'умирать',
        'reír': 'смеяться',
        'llorar': 'плакать',
        'gritar': 'кричать',
        'susurrar': 'шептать',
        'cuidar': 'заботиться',
        'odiar': 'ненавидеть',
        'manejar': 'управлять',
        'reparar': 'чинить',
        'duchar': 'принимать душ',
        'divorciarse': 'разводиться',
        'levantarse': 'вставать'
    },
    'en': {
        # Basic verbs (1-30)
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
        'poder': 'to be able to, can',
        'venir': 'to come',
        'hablar': 'to speak, to talk',
        'vivir': 'to live',
        'comer': 'to eat',
        'trabajar': 'to work',
        'estudiar': 'to study',
        'llegar': 'to arrive, to come',
        'pasar': 'to pass, to spend time',
        'encontrar': 'to find, to meet',
        'llamar': 'to call, to name',
        'pensar': 'to think',
        'salir': 'to leave, to go out',
        'poner': 'to put, to place',
        'seguir': 'to follow, to continue',
        'llevar': 'to carry, to wear',
        'dejar': 'to leave, to let',
        'parecer': 'to seem, to appear',
        'quedar': 'to stay, to remain',
        'creer': 'to believe, to think',
        
        # Verbs 31-50
        'conocer': 'to know (people/places)',
        'sentir': 'to feel',
        'deber': 'to owe, must',
        'entrar': 'to enter',
        'escribir': 'to write',
        'leer': 'to read',
        'beber': 'to drink',
        'comprar': 'to buy',
        'abrir': 'to open',
        'cerrar': 'to close',
        'empezar': 'to begin, to start',
        'terminar': 'to finish, to end',
        'buscar': 'to look for, to search',
        'entender': 'to understand',
        'escuchar': 'to listen',
        'mirar': 'to look at, to watch',
        'usar': 'to use',
        'ayudar': 'to help',
        'necesitar': 'to need',
        'preguntar': 'to ask',
        
        # Verbs 51-80
        'responder': 'to answer, to respond',
        'jugar': 'to play',
        'dormir': 'to sleep',
        'ganar': 'to win, to earn',
        'perder': 'to lose',
        'amar': 'to love',
        'cantar': 'to sing',
        'bailar': 'to dance',
        'tocar': 'to touch, to play (instrument)',
        'cambiar': 'to change',
        'mover': 'to move',
        'caminar': 'to walk',
        'correr': 'to run',
        'subir': 'to go up, to climb',
        'bajar': 'to go down, to descend',
        'explicar': 'to explain',
        'recordar': 'to remember',
        'olvidar': 'to forget',
        'aprender': 'to learn',
        'enseñar': 'to teach',
        'viajar': 'to travel',
        'volar': 'to fly',
        'conducir': 'to drive',
        'cocinar': 'to cook',
        'lavar': 'to wash',
        'limpiar': 'to clean',
        'construir': 'to build, to construct',
        'romper': 'to break',
        'crear': 'to create',
        'imaginar': 'to imagine',
        
        # Verbs 81-100
        'soñar': 'to dream',
        'despertar': 'to wake up',
        'levantar': 'to lift, to raise',
        'sentar': 'to seat',
        'acostar': 'to put to bed',
        'vestir': 'to dress',
        'casar': 'to marry',
        'nacer': 'to be born',
        'morir': 'to die',
        'reír': 'to laugh',
        'llorar': 'to cry',
        'gritar': 'to shout, to scream',
        'susurrar': 'to whisper',
        'cuidar': 'to take care of',
        'odiar': 'to hate',
        'manejar': 'to handle, to manage',
        'reparar': 'to repair, to fix',
        'duchar': 'to shower',
        'divorciarse': 'to get divorced',
        'levantarse': 'to get up'
    }
}

# Правила грамматики (остаются прежними)
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

def get_text(key: str, language: str = 'en') -> str:
    """
    Получить перевод по ключу
    
    Args:
        key: Ключ перевода (может быть вложенным через точку)
        language: Код языка ('ru' или 'en')
    
    Returns:
        Переведенный текст или ключ если перевод не найден
    """
    if language not in TRANSLATIONS:
        language = 'en'  # Fallback на английский
    
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
        language = 'en'  # Fallback на английский
    
    return VERB_TRANSLATIONS[language].get(verb, verb)

def get_grammar_rule(tense: str, language: str = 'en') -> dict:
    """
    Получить правило грамматики для времени
    
    Args:
        tense: Время глагола
        language: Код языка
    
    Returns:
        Словарь с title и content
    """
    if language not in GRAMMAR_RULES:
        language = 'en'
    
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
    return st.session_state.get('interface_language', 'en')

def set_language(language_code: str):
    """Установить язык интерфейса"""
    if language_code in get_available_languages():
        st.session_state.interface_language = language_code
    else:
        st.session_state.interface_language = 'en'

def t(key: str, language: str = None) -> str:
    """Сокращенная функция перевода"""
    if language is None:
        language = get_current_language()
    return get_text(key, language)
