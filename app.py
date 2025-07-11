# ===== ДОПОЛНЕНИЯ К ВАШЕМУ СУЩЕСТВУЮЩЕМУ OAuth ТРЕНАЖЕРУ =====
# Добавьте эти функции к вашему рабочему OAuth коду для Railway + PostgreSQL

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Tuple, Optional
import datetime

# ===== КОНФИГУРАЦИЯ БАЗЫ ДАННЫХ =====

# Конфигурация PostgreSQL для Railway
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('DATABASE_PRIVATE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# ===== ФУНКЦИИ БАЗЫ ДАННЫХ =====

def get_db_connection():
    """Получение подключения к PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)

def init_database():
    """Инициализация PostgreSQL базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица пользователей с поддержкой Google OAuth
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            google_id VARCHAR(255) UNIQUE,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            avatar_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            settings TEXT DEFAULT '{}'
        )
    ''')
    
    # Таблица карточек с SRS данными
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            verb VARCHAR(100) NOT NULL,
            pronoun_index INTEGER NOT NULL,
            tense VARCHAR(50) NOT NULL,
            easiness_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review_date DATE NOT NULL,
            last_review_date DATE,
            total_reviews INTEGER DEFAULT 0,
            correct_reviews INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, verb, pronoun_index, tense)
        )
    ''')
    
    # Таблица дневной статистики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            reviews_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            new_cards_count INTEGER DEFAULT 0,
            study_time_minutes INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, date)
        )
    ''')
    
    # Создаем индексы для оптимизации
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_cards_user_next_review 
        ON cards(user_id, next_review_date)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date 
        ON daily_stats(user_id, date)
    ''')
    
    conn.commit()
    conn.close()

def create_or_update_user(google_user_info: dict) -> dict:
    """Создание или обновление пользователя из Google OAuth"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        google_id = google_user_info.get('id')
        email = google_user_info.get('email')
        name = google_user_info.get('name')
        avatar_url = google_user_info.get('picture')
        
        # Пытаемся найти пользователя по Google ID или email
        cursor.execute('''
            SELECT id, email, name, settings FROM users 
            WHERE google_id = %s OR email = %s
        ''', (google_id, email))
        
        user = cursor.fetchone()
        
        if user:
            # Обновляем существующего пользователя
            cursor.execute('''
                UPDATE users SET 
                    google_id = %s, 
                    email = %s, 
                    name = %s, 
                    avatar_url = %s,
                    last_login = CURRENT_TIMESTAMP 
                WHERE id = %s
            ''', (google_id, email, name, avatar_url, user[0]))
            
            user_data = {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'avatar_url': avatar_url,
                'settings': json.loads(user[3] or '{}')
            }
        else:
            # Создаем нового пользователя
            cursor.execute('''
                INSERT INTO users (google_id, email, name, avatar_url, last_login)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            ''', (google_id, email, name, avatar_url))
            
            new_user_id = cursor.fetchone()[0]
            
            user_data = {
                'id': new_user_id,
                'email': email,
                'name': name,
                'avatar_url': avatar_url,
                'settings': {}
            }
        
        conn.commit()
        conn.close()
        return user_data
    except Exception as e:
        st.error(f"Ошибка создания/обновления пользователя: {e}")
        return None

def save_user_settings(user_id: int, settings: dict):
    """Сохранение настроек пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET settings = %s WHERE id = %s",
            (json.dumps(settings), user_id)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Ошибка сохранения настроек: {e}")

def load_user_cards(user_id: int) -> Dict[str, Card]:
    """Загрузка карточек пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT verb, pronoun_index, tense, easiness_factor, interval_days,
                   repetitions, next_review_date, last_review_date,
                   total_reviews, correct_reviews
            FROM cards WHERE user_id = %s
        ''', (user_id,))
        
        cards = {}
        for row in cursor.fetchall():
            card = Card(
                verb=row[0],
                pronoun_index=row[1],
                tense=row[2],
                easiness_factor=row[3],
                interval=row[4],
                repetitions=row[5],
                next_review_date=str(row[6]),
                last_review_date=str(row[7]) if row[7] else None,
                total_reviews=row[8],
                correct_reviews=row[9]
            )
            key = f"{row[0]}_{row[1]}_{row[2]}"
            cards[key] = card
        
        conn.close()
        return cards
    except Exception as e:
        st.error(f"Ошибка загрузки карточек: {e}")
        return {}

def save_card(user_id: int, card: Card):
    """Сохранение карточки в PostgreSQL"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cards 
            (user_id, verb, pronoun_index, tense, easiness_factor, interval_days,
             repetitions, next_review_date, last_review_date, total_reviews, 
             correct_reviews, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, verb, pronoun_index, tense) 
            DO UPDATE SET
