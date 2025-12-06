import sqlite3

conn = sqlite3.connect("labels.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM masters")
masters = cursor.fetchall()

cursor.execute("SELECT * FROM houses")
houses = cursor.fetchall()

print("MAWBS:")
for m in masters:
    print(m)

print("\nHAWBS:")
for h in houses:
    print(h)

conn.close()
