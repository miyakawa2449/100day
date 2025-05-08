import sqlite3

DB_NAME = "face_database.db"

def reset_persons_table():
    """persons テーブルをリセットする"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # persons テーブルを削除
        cursor.execute("DROP TABLE IF EXISTS persons")
        # persons テーブルを再作成
        cursor.execute('''
            CREATE TABLE persons (
                person_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("persons テーブルをリセットしました。")
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        conn.close()

# 実行
reset_persons_table()