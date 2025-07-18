# main.py - Основной файл с расширенной базой глаголов (100 глаголов)

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
    
    .vocab-size-info {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #0c4a6e;
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

# Расширенная база данных глаголов (100 самых популярных)
VERBS = {
    # Топ 30 - самые основные
    'ser': {'type': 'irregular', 'level': 1, 'difficulty': 'hard'},
    'estar': {'type': 'irregular', 'level': 1, 'difficulty': 'hard'},
    'tener': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'hacer': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'decir': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'ir': {'type': 'irregular', 'level': 1, 'difficulty': 'hard'},
    'ver': {'type': 'irregular', 'level': 1, 'difficulty': 'easy'},
    'dar': {'type': 'irregular', 'level': 1, 'difficulty': 'easy'},
    'saber': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'querer': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'poder': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'venir': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'hablar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'vivir': {'type': 'regular-ir', 'level': 1, 'difficulty': 'easy'},
    'comer': {'type': 'regular-er', 'level': 1, 'difficulty': 'easy'},
    'trabajar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'estudiar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'llegar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'pasar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'encontrar': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'llamar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'pensar': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'salir': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'poner': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'seguir': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'llevar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'dejar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'parecer': {'type': 'irregular', 'level': 1, 'difficulty': 'medium'},
    'quedar': {'type': 'regular-ar', 'level': 1, 'difficulty': 'easy'},
    'creer': {'type': 'regular-er', 'level': 1, 'difficulty': 'easy'},
    
    # Топ 31-50 - популярные глаголы
    'conocer': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'sentir': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'deber': {'type': 'regular-er', 'level': 2, 'difficulty': 'easy'},
    'entrar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'escribir': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'leer': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'beber': {'type': 'regular-er', 'level': 2, 'difficulty': 'easy'},
    'comprar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'abrir': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'cerrar': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'empezar': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'terminar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'buscar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'entender': {'type': 'irregular', 'level': 2, 'difficulty': 'medium'},
    'escuchar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'mirar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'usar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'ayudar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'necesitar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    'preguntar': {'type': 'regular-ar', 'level': 2, 'difficulty': 'easy'},
    
    # Топ 51-80 - дополнительные популярные глаголы
    'responder': {'type': 'regular-er', 'level': 3, 'difficulty': 'easy'},
    'jugar': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'dormir': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'ganar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'perder': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'amar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'cantar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'bailar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'tocar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'cambiar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'mover': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'caminar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'correr': {'type': 'regular-er', 'level': 3, 'difficulty': 'easy'},
    'subir': {'type': 'regular-ir', 'level': 3, 'difficulty': 'easy'},
    'bajar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'explicar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'recordar': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'olvidar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'aprender': {'type': 'regular-er', 'level': 3, 'difficulty': 'easy'},
    'enseñar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'viajar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'volar': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'conducir': {'type': 'irregular', 'level': 3, 'difficulty': 'hard'},
    'cocinar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'lavar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'limpiar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'construir': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'romper': {'type': 'irregular', 'level': 3, 'difficulty': 'medium'},
    'crear': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    'imaginar': {'type': 'regular-ar', 'level': 3, 'difficulty': 'easy'},
    
    # Топ 81-100 - расширенный словарь
    'soñar': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'despertar': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'levantar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'sentar': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'acostar': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'vestir': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'casar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'nacer': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'morir': {'type': 'irregular', 'level': 4, 'difficulty': 'hard'},
    'reír': {'type': 'irregular', 'level': 4, 'difficulty': 'medium'},
    'llorar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'gritar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'susurrar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'cuidar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'odiar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'manejar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'reparar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'duchar': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'divorciarse': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'},
    'levantarse': {'type': 'regular-ar', 'level': 4, 'difficulty': 'easy'}
}

PRONOUNS = ['yo', 'tú', 'él/ella', 'nosotros', 'vosotros', 'ellos/ellas']

# Расширенные спряжения (добавлены новые глаголы)
CONJUGATIONS = {
    'presente': {
        # Основные глаголы (1-30)
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
        
        # Глаголы 31-50
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
        'terminar': ['termino', 'terminas', 'termina', 'terminamos', 'termináis', 'terminan'],
        'buscar': ['busco', 'buscas', 'busca', 'buscamos', 'buscáis', 'buscan'],
        'entender': ['entiendo', 'entiendes', 'entiende', 'entendemos', 'entendéis', 'entienden'],
        'escuchar': ['escucho', 'escuchas', 'escucha', 'escuchamos', 'escucháis', 'escuchan'],
        'mirar': ['miro', 'miras', 'mira', 'miramos', 'miráis', 'miran'],
        'usar': ['uso', 'usas', 'usa', 'usamos', 'usáis', 'usan'],
        'ayudar': ['ayudo', 'ayudas', 'ayuda', 'ayudamos', 'ayudáis', 'ayudan'],
        'necesitar': ['necesito', 'necesitas', 'necesita', 'necesitamos', 'necesitáis', 'necesitan'],
        'preguntar': ['pregunto', 'preguntas', 'pregunta', 'preguntamos', 'preguntáis', 'preguntan'],
        
        # Глаголы 51-80
        'responder': ['respondo', 'respondes', 'responde', 'respondemos', 'respondéis', 'responden'],
        'jugar': ['juego', 'juegas', 'juega', 'jugamos', 'jugáis', 'juegan'],
        'dormir': ['duermo', 'duermes', 'duerme', 'dormimos', 'dormís', 'duermen'],
        'ganar': ['gano', 'ganas', 'gana', 'ganamos', 'ganáis', 'ganan'],
        'perder': ['pierdo', 'pierdes', 'pierde', 'perdemos', 'perdéis', 'pierden'],
        'amar': ['amo', 'amas', 'ama', 'amamos', 'amáis', 'aman'],
        'cantar': ['canto', 'cantas', 'canta', 'cantamos', 'cantáis', 'cantan'],
        'bailar': ['bailo', 'bailas', 'baila', 'bailamos', 'bailáis', 'bailan'],
        'tocar': ['toco', 'tocas', 'toca', 'tocamos', 'tocáis', 'tocan'],
        'cambiar': ['cambio', 'cambias', 'cambia', 'cambiamos', 'cambiáis', 'cambian'],
        'mover': ['muevo', 'mueves', 'mueve', 'movemos', 'movéis', 'mueven'],
        'caminar': ['camino', 'caminas', 'camina', 'caminamos', 'camináis', 'caminan'],
        'correr': ['corro', 'corres', 'corre', 'corremos', 'corréis', 'corren'],
        'subir': ['subo', 'subes', 'sube', 'subimos', 'subís', 'suben'],
        'bajar': ['bajo', 'bajas', 'baja', 'bajamos', 'bajáis', 'bajan'],
        'explicar': ['explico', 'explicas', 'explica', 'explicamos', 'explicáis', 'explican'],
        'recordar': ['recuerdo', 'recuerdas', 'recuerda', 'recordamos', 'recordáis', 'recuerdan'],
        'olvidar': ['olvido', 'olvidas', 'olvida', 'olvidamos', 'olvidáis', 'olvidan'],
        'aprender': ['aprendo', 'aprendes', 'aprende', 'aprendemos', 'aprendéis', 'aprenden'],
        'enseñar': ['enseño', 'enseñas', 'enseña', 'enseñamos', 'enseñáis', 'enseñan'],
        'viajar': ['viajo', 'viajas', 'viaja', 'viajamos', 'viajáis', 'viajan'],
        'volar': ['vuelo', 'vuelas', 'vuela', 'volamos', 'voláis', 'vuelan'],
        'conducir': ['conduzco', 'conduces', 'conduce', 'conducimos', 'conducís', 'conducen'],
        'cocinar': ['cocino', 'cocinas', 'cocina', 'cocinamos', 'cocináis', 'cocinan'],
        'lavar': ['lavo', 'lavas', 'lava', 'lavamos', 'laváis', 'lavan'],
        'limpiar': ['limpio', 'limpias', 'limpia', 'limpiamos', 'limpiáis', 'limpian'],
        'construir': ['construyo', 'construyes', 'construye', 'construimos', 'construís', 'construyen'],
        'romper': ['rompo', 'rompes', 'rompe', 'rompemos', 'rompéis', 'rompen'],
        'crear': ['creo', 'creas', 'crea', 'creamos', 'creáis', 'crean'],
        'imaginar': ['imagino', 'imaginas', 'imagina', 'imaginamos', 'imagináis', 'imaginan'],
        
        # Глаголы 81-100
        'soñar': ['sueño', 'sueñas', 'sueña', 'soñamos', 'soñáis', 'sueñan'],
        'despertar': ['despierto', 'despiertas', 'despierta', 'despertamos', 'despertáis', 'despiertan'],
        'levantar': ['levanto', 'levantas', 'levanta', 'levantamos', 'levantáis', 'levantan'],
        'sentar': ['siento', 'sientas', 'sienta', 'sentamos', 'sentáis', 'sientan'],
        'acostar': ['acuesto', 'acuestas', 'acuesta', 'acostamos', 'acostáis', 'acuestan'],
        'vestir': ['visto', 'vistes', 'viste', 'vestimos', 'vestís', 'visten'],
        'casar': ['caso', 'casas', 'casa', 'casamos', 'casáis', 'casan'],
        'nacer': ['nazco', 'naces', 'nace', 'nacemos', 'nacéis', 'nacen'],
        'morir': ['muero', 'mueres', 'muere', 'morimos', 'morís', 'mueren'],
        'reír': ['río', 'ríes', 'ríe', 'reímos', 'reís', 'ríen'],
        'llorar': ['lloro', 'lloras', 'llora', 'lloramos', 'lloráis', 'lloran'],
        'gritar': ['grito', 'gritas', 'grita', 'gritamos', 'gritáis', 'gritan'],
        'susurrar': ['susurro', 'susurras', 'susurra', 'susurramos', 'susurráis', 'susurran'],
        'cuidar': ['cuido', 'cuidas', 'cuida', 'cuidamos', 'cuidáis', 'cuidan'],
        'odiar': ['odio', 'odias', 'odia', 'odiamos', 'odiáis', 'odian'],
        'manejar': ['manejo', 'manejas', 'maneja', 'manejamos', 'manejáis', 'manejan'],
        'reparar': ['reparo', 'reparas', 'repara', 'reparamos', 'reparáis', 'reparan'],
        'duchar': ['ducho', 'duchas', 'ducha', 'duchamos', 'ducháis', 'duchan'],
        'divorciarse': ['me divorcio', 'te divorcias', 'se divorcia', 'nos divorciamos', 'os divorciáis', 'se divorcian'],
        'levantarse': ['me levanto', 'te levantas', 'se levanta', 'nos levantamos', 'os levantáis', 'se levantan']
    },
    # Для экономии места включаю только основные спряжения других времен
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
        'trabajar': ['trabajé', 'trabajaste', 'trabajó', 'trabajamos', 'trabajasteis', 'trabajaron'],
        'estudiar': ['estudié', 'estudiaste', 'estudió', 'estudiamos', 'estudiasteis', 'estudiaron']
    },
    'subjuntivo': {
        'ser': ['sea', 'seas', 'sea', 'seamos', 'seáis', 'sean'],
        'estar': ['esté', 'estés', 'esté', 'estemos', 'estéis', 'estén'],
        'tener': ['tenga', 'tengas', 'tenga', 'tengamos', 'tengáis', 'tengan'],
        'hacer': ['haga', 'hagas', 'haga', 'hagamos', 'hagáis', 'hagan'],
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
    30: {'name': 'vocabulary_30', 'verbs': 30, 'description': 'vocab_30_desc'},
    50: {'name': 'vocabulary_50', 'verbs': 50, 'description': 'vocab_50_desc'},
    100: {'name': 'vocabulary_100', 'verbs': 100, 'description': 'vocab_100_desc'}
}

def get_verbs_for_level(vocab_size: int) -> Dict:
    """Получить глаголы для выбранного размера словаря"""
    all_verbs = list(VERBS.keys())
    
    if vocab_size == 30:
        # Первые 30 самых популярных глаголов
        selected_verbs = all_verbs[:30]
    elif vocab_size == 50:
        # Первые 50 глаголов
        selected_verbs = all_verbs[:50]
    else:  # 100
        # Все 100 глаголов
        selected_verbs = all_verbs
    
    return {verb: VERBS[verb] for verb in selected_verbs}

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

def show_vocabulary_size_selector():
    """Показывает селектор размера словаря"""
    st.markdown("### " + t('vocabulary_size'))
    
    current_size = st.session_state.settings.get('vocabulary_size', 30)
    
    # Создаем selectbox для выбора размера словаря
    selected_size = st.selectbox(
        label=t('vocabulary_size'),
        options=list(VOCABULARY_SIZES.keys()),
        format_func=lambda x: f"{VOCABULARY_SIZES[x]['verbs']} {t('verbs')} - {t(VOCABULARY_SIZES[x]['name'])}",
        index=list(VOCABULARY_SIZES.keys()).index(current_size),
        key="vocab_size_selector",
        label_visibility="collapsed"
    )
    
    # Показываем описание выбранного размера словаря
    vocab_info = VOCABULARY_SIZES[selected_size]
    st.markdown(f"""
    <div class="vocab-size-info">
        <strong>{t(vocab_info['name'])}</strong><br>
        {t(vocab_info['description'])}
    </div>
    """, unsafe_allow_html=True)
    
    return selected_size

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
    
    # Новая секция о размерах словаря
    st.markdown("---")
    st.markdown(f"## {t('choose_vocabulary_size')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 1rem; margin: 0.5rem 0;">
            <h4 style="color: #0c4a6e; margin-bottom: 1rem;">📚 {t('vocabulary_30')}</h4>
            <p style="color: #0c4a6e; font-size: 0.9rem;">{t('vocab_30_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: #fef3c7; border: 2px solid #f59e0b; border-radius: 1rem; margin: 0.5rem 0;">
            <h4 style="color: #92400e; margin-bottom: 1rem;">📖 {t('vocabulary_50')}</h4>
            <p style="color: #92400e; font-size: 0.9rem;">{t('vocab_50_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: #f0fdf4; border: 2px solid #22c55e; border-radius: 1rem; margin: 0.5rem 0;">
            <h4 style="color: #166534; margin-bottom: 1rem;">📚 {t('vocabulary_100')}</h4>
            <p style="color: #166534; font-size: 0.9rem;">{t('vocab_100_desc')}</p>
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
        'new_cards_per_day': st.session_state.settings['new_cards_per_day'],
        'vocabulary_size': st.session_state.settings.get('vocabulary_size', 30)
    }
    
    # Выбор размера словаря
    new_vocab_size = show_vocabulary_size_selector()
    
    st.markdown("---")
    
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
        current_settings['new_cards_per_day'] != new_cards_per_day or
        current_settings['vocabulary_size'] != new_vocab_size
    )
    
    # Кнопка применить (показывается только если настройки изменились)
    if settings_changed:
        if st.button(t('apply_settings'), key="apply_settings", use_container_width=True, type="primary"):
            # Применяем настройки
            st.session_state.settings['selected_tenses'] = new_selected_tenses
            st.session_state.settings['new_cards_per_day'] = new_cards_per_day
            st.session_state.settings['vocabulary_size'] = new_vocab_size
            
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
    
    # Информация о текущем словаре
    current_vocab_size = st.session_state.settings.get('vocabulary_size', 30)
    st.markdown(f"📚 **{t('current_vocabulary')}:** {current_vocab_size} {t('verbs')}")

def show_verb_card():
    """Показывает карточку глагола с поддержкой языков"""
    card = st.session_state.current_card
    
    # Получаем доступные глаголы для текущего размера словаря
    vocab_size = st.session_state.settings.get('vocabulary_size', 30)
    available_verbs = get_verbs_for_level(vocab_size)
    
    if (card.verb not in available_verbs or 
        card.tense not in CONJUGATIONS or 
        card.verb not in CONJUGATIONS[card.tense]):
        st.error(t('card_data_corrupted'))
        next_card()
        return
    
    verb_translation = get_verb_translation(card.verb)
    is_revealed = st.session_state.is_revealed
    
    # Отображаем карточку
    if not is_revealed:
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
            <div class="click-hint">
                {t('click_to_reveal')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопка для показа ответа
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
                ✓ {conjugation}
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

def get_new_cards() -> List[Tuple[str, int, str]]:
    """Получает новые карточки с учетом размера словаря"""
    new_cards = []
    existing_keys = set(st.session_state.cards.keys())
    
    # Получаем доступные глаголы для текущего размера словаря
    vocab_size = st.session_state.settings.get('vocabulary_size', 30)
    available_verbs = get_verbs_for_level(vocab_size)
    
    for tense in st.session_state.settings['selected_tenses']:
        if tense not in CONJUGATIONS:
            continue
            
        for verb in available_verbs:
            if verb not in CONJUGATIONS[tense]:
                continue
                
            for pronoun_index in range(6):
                key = get_card_key(verb, pronoun_index, tense)
                if key not in existing_keys:
                    new_cards.append((verb, pronoun_index, tense))
    
    random.shuffle(new_cards)
    return new_cards

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
            'auto_save': True,
            'vocabulary_size': 30  # Новая настройка для размера словаря
        }
    if 'recent_combinations' not in st.session_state:
        st.session_state.recent_combinations = []

# Остальные функции остаются теми же...
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
    
    # Получаем доступные глаголы для текущего размера словаря
    vocab_size = st.session_state.settings.get('vocabulary_size', 30)
    available_verbs = get_verbs_for_level(vocab_size)
    
    due_cards = []
    for card in st.session_state.cards.values():
        if (card.next_review_date <= today and 
            card.tense in st.session_state.settings['selected_tenses'] and
            card.verb in available_verbs):
            due_cards.append(card)
    
    return sorted(due_cards, key=lambda x: x.next_review_date)

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
