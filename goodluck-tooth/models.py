import sqlite3
from datetime import date
from config import DATABASE_PATH


def get_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS thoughts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            emotion TEXT,
            ai_response TEXT NOT NULL,
            flower_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, type)
        );

        CREATE TABLE IF NOT EXISTS flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thought_id INTEGER,
            flower_type TEXT NOT NULL,
            position_x REAL,
            position_y REAL,
            size REAL DEFAULT 1.0,
            color_variant TEXT,
            planted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (thought_id) REFERENCES thoughts(id)
        );

        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            thought_count INTEGER DEFAULT 0,
            flower_count INTEGER DEFAULT 0
        );
    """)
    db.commit()
    db.close()


def save_thought(content, emotion, ai_response, flower_type):
    db = get_db()
    cur = db.execute(
        "INSERT INTO thoughts (content, emotion, ai_response, flower_type) VALUES (?, ?, ?, ?)",
        (content, emotion, ai_response, flower_type),
    )
    thought_id = cur.lastrowid

    today = date.today().isoformat()
    db.execute(
        "INSERT INTO daily_stats (date, thought_count, flower_count) "
        "VALUES (?, 1, 1) ON CONFLICT(date) DO UPDATE SET "
        "thought_count = thought_count + 1, flower_count = flower_count + 1",
        (today,),
    )
    db.commit()
    db.close()
    return thought_id


def get_todays_thoughts():
    db = get_db()
    today = date.today().isoformat()
    rows = db.execute(
        "SELECT * FROM thoughts WHERE date(created_at) = ? ORDER BY created_at ASC",
        (today,),
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_thoughts_page(page=1, limit=20):
    db = get_db()
    offset = (page - 1) * limit
    rows = db.execute(
        "SELECT * FROM thoughts ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    total = db.execute("SELECT COUNT(*) as cnt FROM thoughts").fetchone()["cnt"]
    db.close()
    return [dict(r) for r in rows], total


def get_thought_by_id(thought_id):
    db = get_db()
    row = db.execute("SELECT * FROM thoughts WHERE id = ?", (thought_id,)).fetchone()
    db.close()
    return dict(row) if row else None


def get_or_create_daily_message(msg_type, content=None):
    db = get_db()
    today = date.today().isoformat()
    if content:
        db.execute(
            "INSERT OR IGNORE INTO daily_messages (date, type, content) VALUES (?, ?, ?)",
            (today, msg_type, content),
        )
        db.commit()
    row = db.execute(
        "SELECT * FROM daily_messages WHERE date = ? AND type = ?",
        (today, msg_type),
    ).fetchone()
    db.close()
    return dict(row) if row else None


def add_flower(thought_id, flower_type, position_x, position_y, size, color_variant):
    db = get_db()
    cur = db.execute(
        "INSERT INTO flowers (thought_id, flower_type, position_x, position_y, size, color_variant) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (thought_id, flower_type, position_x, position_y, size, color_variant),
    )
    flower_id = cur.lastrowid
    db.commit()
    db.close()
    return flower_id


def get_all_flowers():
    db = get_db()
    rows = db.execute("SELECT * FROM flowers ORDER BY planted_at ASC").fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_stats():
    db = get_db()
    today = date.today().isoformat()
    total_thoughts = db.execute("SELECT COUNT(*) as cnt FROM thoughts").fetchone()["cnt"]
    total_flowers = db.execute("SELECT COUNT(*) as cnt FROM flowers").fetchone()["cnt"]
    today_row = db.execute(
        "SELECT * FROM daily_stats WHERE date = ?", (today,)
    ).fetchone()
    today_count = today_row["thought_count"] if today_row else 0
    today_flowers = today_row["flower_count"] if today_row else 0

    streak = 0
    rows = db.execute(
        "SELECT date FROM daily_stats ORDER BY date DESC"
    ).fetchall()
    from datetime import timedelta
    check_date = date.today()
    for r in rows:
        if r["date"] == check_date.isoformat():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    db.close()
    return {
        "total_thoughts": total_thoughts,
        "total_flowers": total_flowers,
        "today_count": today_count,
        "today_flowers": today_flowers,
        "streak_days": streak,
    }


def garden_level(total_flowers):
    if total_flowers <= 4:
        return "小萌芽花园"
    elif total_flowers <= 14:
        return "成长草地"
    elif total_flowers <= 29:
        return "盛开花园"
    elif total_flowers <= 49:
        return "繁茂花园"
    elif total_flowers <= 99:
        return "壮观花园"
    else:
        return "传奇好运牙花园"
