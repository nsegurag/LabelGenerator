import sqlite3

conn = sqlite3.connect("labels.db")
cursor = conn.cursor()

cursor.execute("SELECT id, mawb_number, origin, destination, total_pieces FROM masters ORDER BY id DESC")
rows = cursor.fetchall()

print("\nMAWBs guardadas:\n")
for r in rows:
    print(r)

conn.close()
