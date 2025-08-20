# inspect_db.py
import sqlite3

DB_FILE = "habits.db"

# Connect to the database
con = sqlite3.connect(DB_FILE)
cur = con.cursor()

print("--- Habits ---")
for row in cur.execute("SELECT * FROM habits ORDER BY name;"):
    print(row)

print("\n--- Recent Logs (Last 10) ---")
for row in cur.execute("SELECT * FROM logs ORDER BY log_date DESC LIMIT 10;"):
    print(row)

# Close the connection
con.close()