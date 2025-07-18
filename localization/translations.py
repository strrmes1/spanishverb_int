# spanish_trainer.py - Модуль испанского тренажера глаголов

import streamlit as st
import datetime
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

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

# Расширенная база испанских глаголов (100 глаголов)
SPANISH_VERBS = {
    # Топ 30 - самые основные
    'ser': {'translation': 'быть, являться', 'type': 'irregular'},
    'estar': {'translation': 'находиться, быть', 'type': 'irregular'},
    'tener': {'translation': 'иметь', 'type': 'irregular'},
    'hacer': {'translation': 'делать', 'type': 'irregular'},
    'decir': {'translation': 'говорить, сказать', 'type': 'irregular'},
    'ir': {'translation': 'идти, ехать', 'type': 'irregular'},
    'ver': {'translation': 'видеть', 'type': 'irregular'},
    'dar': {'translation': 'давать', 'type': 'irregular'},
    'saber': {'translation': 'знать', 'type': 'irregular'},
    'querer': {'translation': 'хотеть, любить', 'type': 'irregular'},
    'poder': {'translation': 'мочь', 'type': 'irregular'},
    'venir': {'translation': 'приходить', 'type': 'irregular'},
    'hablar': {'translation': 'говорить', 'type': 'regular-ar'},
    'vivir': {'translation': 'жить', 'type': 'regular-ir'},
    'comer': {'translation': 'есть', 'type': 'regular-er'},
    'trabajar': {'translation': 'работать', 'type': 'regular-ar'},
    'estudiar': {'translation': 'изучать', 'type': 'regular-ar'},
    'llegar': {'translation': 'прибывать, приходить', 'type': 'regular-ar'},
    'pasar': {'translation': 'проходить, проводить', 'type': 'regular-ar'},
    'encontrar': {'translation': 'находить, встречать', 'type': 'irregular'},
    'llamar': {'translation': 'звать, называть', 'type': 'regular-ar'},
    'pensar': {'translation': 'думать', 'type': 'irregular'},
    'salir': {'translation': 'выходить', 'type': 'irregular'},
    'poner': {'translation': 'класть, ставить', 'type': 'irregular'},
    'seguir': {'translation': 'следовать, продолжать', 'type': 'irregular'},
    'llevar': {'translation': 'носить, нести', 'type': 'regular-ar'},
    'dejar': {'translation': 'оставлять', 'type': 'regular-ar'},
    'parecer': {'translation': 'казаться', 'type': 'irregular'},
    'quedar': {'translation': 'оставаться', 'type': 'regular-ar'},
    'creer': {'translation': 'верить, считать', 'type': 'regular-er'},
    
    # Топ 31-50 - популярные глаголы
    'conocer': {'translation': 'знать (людей/места)', 'type': 'irregular'},
    'sentir': {'translation': 'чувствовать', 'type': 'irregular'},
    'deber': {'translation': 'быть должным', 'type': 'regular-er'},
    'entrar': {'translation': 'входить', 'type': 'regular-ar'},
    'escribir': {'translation': 'писать', 'type': 'irregular'},
    'leer': {'translation': 'читать', 'type': 'irregular'},
    'beber': {'translation': 'пить', 'type': 'regular-er'},
    'comprar': {'translation': 'покупать', 'type': 'regular-ar'},
    'abrir': {'translation': 'открывать', 'type': 'irregular'},
    'cerrar': {'translation': 'закрывать', 'type': 'irregular'},
    'empezar': {'translation': 'начинать', 'type': 'irregular'},
    'terminar': {'translation': 'заканчивать', 'type': 'regular-ar'},
    'buscar': {'translation': 'искать', 'type': 'regular-ar'},
    'entender': {'translation': 'понимать', 'type': 'irregular'},
    'escuchar': {'translation': 'слушать', 'type': 'regular-ar'},
    'mirar': {'translation': 'смотреть', 'type': 'regular-ar'},
    'usar': {'translation': 'использовать', 'type': 'regular-ar'},
    'ayudar': {'translation': 'помогать', 'type': 'regular-ar'},
    'necesitar': {'translation': 'нуждаться', 'type': 'regular-ar'},
    'preguntar': {'translation': 'спрашивать', 'type': 'regular-ar'},
    
    # Топ 51-100 - дополнительные глаголы
    'responder': {'translation': 'отвечать', 'type': 'regular-er'},
    'jugar': {'translation': 'играть', 'type': 'irregular'},
    'dormir': {'translation': 'спать', 'type': 'irregular'},
    'ganar': {'translation': 'выигрывать, зарабатывать', 'type': 'regular-ar'},
    'perder': {'translation': 'терять', 'type': 'irregular'},
    'amar': {'translation': 'любить', 'type': 'regular-ar'},
    'cantar': {'translation': 'петь', 'type': 'regular-ar'},
    'bailar': {'translation': 'танцевать', 'type': 'regular-ar'},
    'tocar': {'translation': 'трогать, играть (на инструменте)', 'type': 'regular-ar'},
    'cambiar': {'translation': 'менять', 'type': 'regular-ar'},
    'mover': {'translation': 'двигать', 'type': 'irregular'},
    'caminar': {'translation': 'ходить пешком', 'type': 'regular-ar'},
    'correr': {'translation': 'бегать', 'type': 'regular-er'},
    'subir': {'translation': 'подниматься', 'type': 'regular-ir'},
    'bajar': {'translation': 'спускаться', 'type': 'regular-ar'},
    'explicar': {'translation': 'объяснять', 'type': 'regular-ar'},
    'recordar': {'translation': 'помнить', 'type': 'irregular'},
    'olvidar': {'translation': 'забывать', 'type': 'regular-ar'},
    'aprender': {'translation': 'учиться', 'type': 'regular-er'},
    'enseñar': {'translation': 'учить', 'type': 'regular-ar'},
    'viajar': {'translation': 'путешествовать', 'type': 'regular-ar'},
    'volar': {'translation': 'летать', 'type': 'irregular'},
    'conducir': {'translation': 'водить машину', 'type': 'irregular'},
    'cocinar': {'translation': 'готовить', 'type': 'regular-ar'},
    'lavar': {'translation': 'мыть', 'type': 'regular-ar'},
    'limpiar': {'translation': 'чистить', 'type': 'regular-ar'},
    'construir': {'translation': 'строить', 'type': 'irregular'},
    'romper': {'translation': 'ломать', 'type': 'irregular'},
    'crear': {'translation': 'создавать', 'type': 'regular-ar'},
    'imaginar': {'translation': 'воображать', 'type': 'regular-ar'},
    'soñar': {'translation': 'мечтать, видеть сны', 'type': 'irregular'},
    'despertar': {'translation': 'просыпаться', 'type': 'irregular'},
    'levantar': {'translation': 'поднимать', 'type': 'regular-ar'},
    'sentar': {'translation': 'сажать', 'type': 'irregular'},
    'acostar': {'translation': 'укладывать спать', 'type': 'irregular'},
    'vestir': {'translation': 'одевать', 'type': 'irregular'},
    'casar': {'translation': 'жениться/выходить замуж', 'type': 'regular-ar'},
    'nacer': {'translation': 'рождаться', 'type': 'irregular'},
    'morir': {'translation': 'умирать', 'type': 'irregular'},
    'reír': {'translation': 'смеяться', 'type': 'irregular'},
    'llorar': {'translation': 'плакать', 'type': 'regular-ar'},
    'gritar': {'translation': 'кричать', 'type': 'regular-ar'},
    'susurrar': {'translation': 'шептать', 'type': 'regular-ar'},
    'cuidar': {'translation': 'заботиться', 'type': 'regular-ar'},
    'odiar': {'translation': 'ненавидеть', 'type': 'regular-ar'},
    'manejar': {'translation': 'управлять', 'type': 'regular-ar'},
    'reparar': {'translation': 'чинить', 'type': 'regular-ar'},
    'duchar': {'translation': 'принимать душ', 'type': 'regular-ar'},
    'divorciarse': {'translation': 'разводиться', 'type': 'regular-ar'},
    'levantarse': {'translation': 'вставать', 'type': 'regular-ar'}
}

SPANISH_PRONOUNS = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']

# Расширенные спряжения испанских глаголов
SPANISH_CONJUGATIONS = {
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
        'poder': ['puedo', 'puedes', 'puede', 'podemos', 'podéis', 'pueden'],
        'venir': ['vengo', 'vienes', 'viene', 'venimos', 'venís', 'vienen'],
        'hablar': ['hablo', 'hablas', 'habla', 'hablamos', 'habláis', 'hablan'],
        'vivir': ['vivo', 'vives', 'vive', 'vivimos', 'vivís', 'viven'],
        'comer': ['como', 'comes', 'come', 'comemos', 'coméis', 'comen'],
        'trabajar': ['trabajo', 'trabajas', 'trabaja', 'trabajamos', 'trabajáis', 'trabajan'],
        'estudiar': ['estudio', 'estudias', 'estudia', 'estudiamos', 'estudiáis', 'estudian'],
        'llegar': ['llego', 'llegas', 'llega', 'llegamos', 'llegáis', 'llegan'],
        'pasar': ['paso', 'pasas', 'pasa', 'pasamos', 'pasáis', 'pasan'],
        'encontrar': ['encuentro', 'encuentras', 'encuentra', 'encontramos', 'encontráis', 'encuentran'],
        'llamar': ['llamo', 'llamas', 'llama', 'llamamos', 'llamáis', 'llaman'],
        'pensar': ['pienso', 'piensas', 'piensa', 'pensamos', 'pensáis', 'piensan'],
        'salir': ['salgo', 'sales', 'sale', 'salimos', 'salís', 'salen'],
        'poner': ['pongo', 'pones', 'pone', 'ponemos', 'ponéis', 'ponen'],
        'seguir': ['sigo', 'sigues', 'sigue', 'seguimos', 'seguís', 'siguen'],
        'llevar': ['llevo', 'llevas', 'lleva', 'llevamos', 'lleváis', 'llevan'],
        'dejar': ['dejo', 'dejas', 'deja', 'dejamos', 'dejáis', 'dejan'],
        'parecer': ['parezco', 'pareces', 'parece', 'parecemos', 'parecéis', 'parecen'],
        'quedar': ['quedo', 'quedas', 'queda', 'quedamos', 'quedáis', 'quedan'],
        'creer': ['creo', 'crees', 'cree', 'creemos', 'creéis', 'creen'],
        'conocer': ['conozco', 'conoces', 'conoce', 'conocemos', 'conocéis', 'conocen'],
        'sentir': ['siento', 'sientes', 'siente', 'sentimos', 'sentís', 'sienten'],
        'deber': ['debo', 'debes', 'debe', 'debemos', 'debéis', 'deben'],
        'entrar': ['entro', 'entras', 'entra', 'entramos', 'entráis', 'entran'],
        'escribir': ['escribo', 'escribes', 'escribe', 'escribimos', 'escribís', 'escriben'],
        'leer': ['leo', 'lees', 'lee', 'leemos', 'leéis', 'leen'],
        'beber': ['bebo', 'bebes', 'bebe', 'bebemos', 'bebéis', 'beben'],
        'comprar': ['compro', 'compras', 'compra', 'compramos', 'compráis', 'compran'],
        'abrir': ['abro', 'abres', 'abre', 'abrimos', 'abrís', 'abren'],
        'cerrar': ['cierro', 'cierras', 'cierra', 'cerramos', 'cerráis', 'cierran'],
        'empezar': ['empiezo', 'empiezas', 'empieza', 'empezamos', 'empezáis', 'empiezan'],
        'terminar': ['termino', 'terminas', 'termina', 'terminamos', 'termináis', 'terminan']
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
        'poder': ['pude', 'pudiste', 'pudo', 'pudimos', 'pudisteis', 'pudieron'],
        'venir': ['vine', 'viniste', 'vino', 'vinimos', 'vinisteis', 'vinieron'],
        'hablar': ['hablé', 'hablaste', 'habló', 'hablamos', 'hablasteis', 'hablaron'],
        'vivir': ['viví', 'viviste', 'vivió', 'vivimos', 'vivisteis', 'vivieron'],
        'comer': ['comí', 'comiste', 'comió', 'comimos', 'comisteis', 'comieron'],
        'trabajar': ['trabajé', 'trabajaste', 'trabajó', 'trabajamos', 'trabajasteis', 'trabajaron'],
        'estudiar': ['estudié', 'estudiaste', 'estudió', 'estudiamos', 'estudiasteis', 'estudiaron']
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

# Опции размера словаря
VOCABULARY_SIZES = {
    30: {'name': 'Базовый (30 глаголов)', 'verbs': 30},
    50: {'name': 'Средний (50 глаголов)', 'verbs': 50},
    100: {'name': 'Полный (100 глаголов)', 'verbs': 100}
}

# Правила грамматики
GRAMMAR_RULES = {
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

def init_spanish_trainer_state():
    """Инициализация состояния испанского тренажера"""
    if 'spanish_cards' not in st.session_state:
        st.session_state.spanish_cards = {}
    if 'spanish_current_card' not in st.session_state:
        st.session_state.spanish_current_card = None
    if 'spanish_is_revealed' not in st.session_state:
        st.session_state.spanish_is_revealed = False
    if 'spanish_daily_stats' not in st.session_state:
        st.session_state.spanish_daily_stats = {
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': datetime.date.today().isoformat()
        }
    if 'spanish_settings' not in st.session_state:
        st.session_state.spanish_settings = {
            'new_cards_per_day': 10,
            'selected_tenses': ['presente'],
            'vocabulary_size': 30
        }
    if 'spanish_recent_combinations' not in st.session_state:
        st.session_state.spanish_recent_combinations = []

def get_verbs_for_level(vocab_size: int) -> Dict:
    """Получить глаголы для выбранного размера словаря"""
    all_verbs = list(SPANISH_VERBS.keys())
    
    if vocab_size == 30:
        selected_verbs = all_verbs[:30]
    elif vocab_size == 50:
        selected_verbs = all_verbs[:50]
    else:  # 100
        selected_verbs = all_verbs
    
    return {verb: SPANISH_VERBS[verb] for verb in selected_verbs}

def get_card_key(verb: str, pronoun_index: int, tense: str) -> str:
    """Генерирует ключ для карточки"""
    return f"{verb}_{pronoun_index}_{tense}"

def get_or_create_card(verb: str, pronoun_index: int, tense: str) -> Card:
    """Получает или создает карточку"""
    key = get_card_key(verb, pronoun_index, tense)
    
    if key not in st.session_state.spanish_cards:
        st.session_state.spanish_cards[key] = Card(
            verb=verb,
            pronoun_index=pronoun_index,
            tense=tense
        )
    
    return st.session_state.spanish_cards[key]

def get_due_cards() -> List[Card]:
    """Получает карточки для повторения"""
    today = datetime.date.today().isoformat()
    
    vocab_size = st.session_state.spanish_settings.get('vocabulary_size', 30)
    available_verbs = get_verbs_for_level(vocab_size)
    
    due_cards = []
    for card in st.session_state.spanish_cards.values():
        if (card.next_review_date <= today and 
            card.tense in st.session_state.spanish_settings['selected_tenses'] and
            card.verb in available_verbs):
            due_cards.append(card)
    
    return sorted(due_cards, key=lambda x: x.next_review_date)

def get_new_cards() -> List[Tuple[str, int, str]]:
    """Получает новые карточки с учетом размера словаря"""
    new_cards = []
    existing_keys = set(st.session_state.spanish_cards.keys())
    
    vocab_size = st.session_state.spanish_settings.get('vocabulary_size', 30)
    available_verbs = get_verbs_for_level(vocab_size)
    
    for tense in st.session_state.spanish_settings['selected_tenses']:
        if tense not in SPANISH_CONJUGATIONS:
            continue
            
        for verb in available_verbs:
            if verb not in SPANISH_CONJUGATIONS[tense]:
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
    if st.session_state.spanish_daily_stats['new_cards_today'] < st.session_state.spanish_settings['new_cards_per_day']:
        new_cards = get_new_cards()
        if new_cards:
            verb, pronoun_index, tense = new_cards[0]
            return get_or_create_card(verb, pronoun_index, tense)
    
    return None

def reset_daily_stats():
    """Сбрасывает дневную статистику"""
    today = datetime.date.today().isoformat()
    if st.session_state.spanish_daily_stats['last_reset'] != today:
        st.session_state.spanish_daily_stats.update({
            'reviews_today': 0,
            'correct_today': 0,
            'new_cards_today': 0,
            'last_reset': today
        })

def process_answer(difficulty: Difficulty):
    """Обрабатывает ответ пользователя"""
    if not st.session_state.spanish_current_card:
        return
    
    is_new_card = st.session_state.spanish_current_card.total_reviews == 0
    
    # Обновляем карточку с помощью SRS
    updated_card = SRSManager.update_card(st.session_state.spanish_current_card, difficulty)
    card_key = get_card_key(updated_card.verb, updated_card.pronoun_index, updated_card.tense)
    st.session_state.spanish_cards[card_key] = updated_card
    
    # Обновляем статистику
    st.session_state.spanish_daily_stats['reviews_today'] += 1
    if difficulty in [Difficulty.GOOD, Difficulty.EASY]:
        st.session_state.spanish_daily_stats['correct_today'] += 1
    if is_new_card:
        st.session_state.spanish_daily_stats['new_cards_today'] += 1
    
    # Переходим к следующей карточке
    next_card()

def next_card():
    """Переход к следующей карточке"""
    st.session_state.spanish_current_card = None
    st.session_state.spanish_is_revealed = False
    st.rerun()

def show_trainer():
    """Показывает интерфейс испанского тренажера"""
    init_spanish_trainer_state()
    reset_daily_stats()
    
    # CSS стили для тренажера
    st.markdown("""
    <style>
        .trainer-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .trainer-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .back-button {
            position: absolute;
            top: 1rem;
            left: 1rem;
            background: rgba(102, 126, 234, 0.1);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.5rem;
            color: #667eea;
            transition: all 0.3s ease;
        }
        
        .back-button:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: translateX(-2px);
        }
        
        .verb-card {
            background: white;
            border-radius: 1rem;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 3px solid transparent;
        }
        
        .verb-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }
        
        .verb-card.revealed {
            border-color: #48bb78;
            background: linear-gradient(135deg, #f0fff4, #c6f6d5);
        }
        
        .verb-title {
            font-size: 3rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .verb-translation {
            font-size: 1.3rem;
            color: #718096;
            margin-bottom: 1.5rem;
            font-style: italic;
        }
        
        .pronoun-display {
            font-size: 2rem;
            color: #4a5568;
            margin: 1.5rem 0;
            font-weight: 600;
        }
        
        .answer-display {
            font-size: 2.5rem;
            font-weight: bold;
            color: #38a169;
            margin: 1.5rem 0;
        }
        
        .difficulty-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }
        
        .difficulty-btn {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-again { background: #ff6b6b; color: white; }
        .btn-hard { background: #feca57; color: black; }
        .btn-good { background: #48ca8b; color: white; }
        .btn-easy { background: #0abde3; color: white; }
        
        .difficulty-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .click-hint {
            font-size: 1.2rem;
            margin-top: 1rem;
            opacity: 0.6;
            color: #4a5568;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Кнопка назад
    if st.button("← Назад", key="back_to_main"):
        st.session_state.page = 'language_selection'
        st.rerun()
    
    # Заголовок
    st.title("🇪🇸 Испанский тренажер глаголов")
    
    # Статистика
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Повторений сегодня", st.session_state.spanish_daily_stats['reviews_today'])
    with col2:
        st.metric("Правильных", st.session_state.spanish_daily_stats['correct_today'])
    with col3:
        st.metric("Новых карточек", st.session_state.spanish_daily_stats['new_cards_today'])
    with col4:
        due_count = len(get_due_cards())
        st.metric("К повторению", due_count)
    
    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки")
        
        # Выбор размера словаря
        vocab_size = st.selectbox(
            "Размер словаря:",
            options=list(VOCABULARY_SIZES.keys()),
            format_func=lambda x: VOCABULARY_SIZES[x]['name'],
            index=list(VOCABULARY_SIZES.keys()).index(st.session_state.spanish_settings.get('vocabulary_size', 30))
        )
        
        # Выбор времен
        st.subheader("Времена для изучения:")
        tense_options = {
            'presente': 'Presente',
            'indefinido': 'Pretérito Indefinido',
            'subjuntivo': 'Subjuntivo',
            'imperfecto': 'Imperfecto'
        }
        
        selected_tenses = []
        for tense_key, tense_name in tense_options.items():
            if st.checkbox(tense_name, value=tense_key in st.session_state.spanish_settings['selected_tenses'], key=f"spanish_tense_{tense_key}"):
                selected_tenses.append(tense_key)
        
        selected_tenses = selected_tenses or ['presente']
        
        # Лимит новых карточек
        new_cards_per_day = st.slider(
            "Новых карточек в день:",
            min_value=1,
            max_value=50,
            value=st.session_state.spanish_settings['new_cards_per_day']
        )
        
        # Применить настройки
        if st.button("Применить настройки", key="apply_spanish_settings"):
            st.session_state.spanish_settings.update({
                'vocabulary_size': vocab_size,
                'selected_tenses': selected_tenses,
                'new_cards_per_day': new_cards_per_day
            })
            st.session_state.spanish_current_card = None
            st.session_state.spanish_is_revealed = False
            st.success("Настройки применены!")
            st.rerun()
    
    # Основной интерфейс карточек
    if not st.session_state.spanish_current_card:
        st.session_state.spanish_current_card = get_next_card()
        st.session_state.spanish_is_revealed = False
    
    if not st.session_state.spanish_current_card:
        st.success("🎉 Отлично! Вы завершили все повторения на сегодня!")
        st.info("Возвращайтесь завтра для новых карточек или измените настройки в боковой панели.")
        return
    
    # Отображение карточки
    show_verb_card()
    
    # Правила грамматики
    st.markdown("---")
    st.subheader("📚 Правила спряжения")
    
    for tense in st.session_state.spanish_settings['selected_tenses']:
        if tense in GRAMMAR_RULES:
            with st.expander(f"{GRAMMAR_RULES[tense]['title']}", expanded=False):
                st.markdown(GRAMMAR_RULES[tense]['content'])

def show_verb_card():
    """Показывает карточку глагола"""
    card = st.session_state.spanish_current_card
    
    # Получаем доступные глаголы для текущего размера словаря
    vocab_size = st.session_state.spanish_settings.get('vocabulary_size', 30)
    available_verbs = get_verbs_for_level(vocab_size)
    
    if (card.verb not in available_verbs or 
        card.tense not in SPANISH_CONJUGATIONS or 
        card.verb not in SPANISH_CONJUGATIONS[card.tense]):
        st.error("❌ Данные карточки повреждены")
        next_card()
        return
    
    verb_info = available_verbs[card.verb]
    is_revealed = st.session_state.spanish_is_revealed
    
    # Отображаем карточку
    if not is_revealed:
        st.markdown(f'''
        <div class="verb-card">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {card.tense.title()}
            </div>
            <div class="pronoun-display">
                {SPANISH_PRONOUNS[card.pronoun_index]}
            </div>
            <div class="click-hint">
                🔍 Нажмите на кнопку, чтобы увидеть ответ
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Кнопка для показа ответа
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Показать ответ", key="reveal_answer", type="primary", use_container_width=True):
                st.session_state.spanish_is_revealed = True
                st.rerun()
    else:
        # Показываем ответ
        conjugation = SPANISH_CONJUGATIONS[card.tense][card.verb][card.pronoun_index]
        
        st.markdown(f'''
        <div class="verb-card revealed">
            <div class="verb-title">{card.verb}</div>
            <div class="verb-translation">{verb_info['translation']}</div>
            <div style="font-size: 1.2rem; opacity: 0.8; margin-bottom: 1rem;">
                {card.tense.title()}
            </div>
            <div class="pronoun-display">
                {SPANISH_PRONOUNS[card.pronoun_index]}
            </div>
            <div class="answer-display">
                ✅ {conjugation}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Кнопки оценки сложности
        st.subheader("🎯 Как хорошо вы знали ответ?")
        st.caption("Честная оценка поможет алгоритму лучше планировать повторения")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("❌ Снова\n(< 1 мин)", key="again", use_container_width=True, help="Не помню вообще"):
                process_answer(Difficulty.AGAIN)
        
        with col2:
            if st.button("😓 Сложно\n(< 10 мин)", key="hard", use_container_width=True, help="Помню с трудом"):
                process_answer(Difficulty.HARD)
        
        with col3:
            if st.button("😊 Хорошо\n(4 дня)", key="good", use_container_width=True, help="Помню уверенно"):
                process_answer(Difficulty.GOOD)
        
        with col4:
            if st.button("😎 Легко\n(> 4 дней)", key="easy", use_container_width=True, help="Помню мгновенно"):
                process_answer(Difficulty.EASY)
