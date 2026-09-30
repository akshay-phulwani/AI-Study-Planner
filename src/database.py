import os
import sqlite3
from typing import Dict, List, Optional, Any
from src.models import UserProfileInput, Roadmap

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "study_planner.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                weekday_hours REAL NOT NULL,
                weekend_hours REAL NOT NULL,
                busy_times TEXT,
                free_times TEXT,
                preferred_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                goal TEXT NOT NULL,
                estimated_weeks INTEGER NOT NULL,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile (id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_id INTEGER NOT NULL,
                phase_number INTEGER NOT NULL,
                phase_title TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (roadmap_id) REFERENCES roadmap (id) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                estimated_hours REAL NOT NULL,
                FOREIGN KEY (phase_id) REFERENCES phases (id) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                day_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                suggested_duration_minutes INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
            );
        """)
        conn.commit()


def save_roadmap(profile: UserProfileInput, roadmap: Roadmap) -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM daily_tasks;")
        cursor.execute("DELETE FROM topics;")
        cursor.execute("DELETE FROM phases;")
        cursor.execute("DELETE FROM roadmap;")
        cursor.execute("DELETE FROM user_profile;")
        
        cursor.execute("""
            INSERT INTO user_profile (goal, weekday_hours, weekend_hours, busy_times, free_times, preferred_time)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (profile.goal, profile.weekday_hours, profile.weekend_hours, profile.busy_times, profile.free_times, profile.preferred_time))
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO roadmap (user_id, goal, estimated_weeks, summary)
            VALUES (?, ?, ?, ?);
        """, (user_id, roadmap.goal, roadmap.estimated_weeks, roadmap.summary))
        roadmap_id = cursor.lastrowid

        for phase in roadmap.phases:
            cursor.execute("""
                INSERT INTO phases (roadmap_id, phase_number, phase_title, description)
                VALUES (?, ?, ?, ?);
            """, (roadmap_id, phase.phase_number, phase.phase_title, phase.description))
            phase_id = cursor.lastrowid

            for topic in phase.topics:
                cursor.execute("""
                    INSERT INTO topics (phase_id, topic_name, estimated_hours)
                    VALUES (?, ?, ?);
                """, (phase_id, topic.topic_name, topic.estimated_hours))
                topic_id = cursor.lastrowid

                for task in topic.daily_tasks:
                    cursor.execute("""
                        INSERT INTO daily_tasks (topic_id, day_number, title, description, suggested_duration_minutes)
                        VALUES (?, ?, ?, ?, ?);
                    """, (topic_id, task.day_number, task.title, task.description, task.suggested_duration_minutes))

        conn.commit()
        return roadmap_id


def get_active_profile() -> Optional[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        return dict(row) if row else None


def get_roadmap_summary() -> Optional[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roadmap ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        return dict(row) if row else None


def get_full_roadmap_tree() -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM roadmap ORDER BY id DESC LIMIT 1;")
        rm = cursor.fetchone()
        if not rm:
            return []
        
        roadmap_id = rm["id"]
        cursor.execute("SELECT * FROM phases WHERE roadmap_id = ? ORDER BY phase_number ASC;", (roadmap_id,))
        phases = [dict(p) for p in cursor.fetchall()]

        for phase in phases:
            cursor.execute("SELECT * FROM topics WHERE phase_id = ? ORDER BY id ASC;", (phase["id"],))
            topics = [dict(t) for t in cursor.fetchall()]
            
            for topic in topics:
                cursor.execute("SELECT * FROM daily_tasks WHERE topic_id = ? ORDER BY day_number ASC, id ASC;", (topic["id"],))
                topic["daily_tasks"] = [dict(dt) for dt in cursor.fetchall()]
            
            phase["topics"] = topics

        return phases


def get_all_tasks() -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                dt.id AS task_id,
                dt.day_number,
                dt.title AS task_title,
                dt.description AS task_description,
                dt.suggested_duration_minutes,
                dt.completed,
                dt.completed_at,
                t.topic_name,
                p.phase_title,
                p.phase_number
            FROM daily_tasks dt
            JOIN topics t ON dt.topic_id = t.id
            JOIN phases p ON t.phase_id = p.id
            ORDER BY dt.day_number ASC, dt.id ASC;
        """)
        return [dict(row) for row in cursor.fetchall()]


def mark_task_status(task_id: int, completed: bool) -> None:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        if completed:
            cursor.execute("""
                UPDATE daily_tasks
                SET completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (task_id,))
        else:
            cursor.execute("""
                UPDATE daily_tasks
                SET completed = 0, completed_at = NULL
                WHERE id = ?;
            """, (task_id,))
        conn.commit()


def reset_planner() -> None:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_tasks;")
        cursor.execute("DELETE FROM topics;")
        cursor.execute("DELETE FROM phases;")
        cursor.execute("DELETE FROM roadmap;")
        cursor.execute("DELETE FROM user_profile;")
        conn.commit()
