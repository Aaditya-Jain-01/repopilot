import sqlite3

def get_user_data(user_id):
    conn = sqlite3.connect("users.db")
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def calculate_rate(total_requests, time_elapsed):
    if time_elapsed == 0:
        return 0.0
    return total_requests / time_elapsed