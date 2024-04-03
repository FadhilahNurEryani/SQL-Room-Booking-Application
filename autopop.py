import sqlite3
import random


conn = sqlite3.connect('master.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        Location TEXT,
        Number TEXT UNIQUE,
        Desks INTEGER,
        Type TEXT,
        Auth INTEGER,
        PRIMARY KEY(Number)
    )
''')

location = "Gymnasium"
room_prefix = "G."
room_numbers = [f"{room_prefix}{i:02d}" for i in range(4, 28)]
types = ["Closed Classroom"]

for room_number in room_numbers:
    desks = random.randint(12,15)
    room_type = random.choice(types)
    auth = 1

    cursor.execute('''
        INSERT OR IGNORE INTO rooms (Location, Number, Desks, Type, Auth)
        VALUES (?, ?, ?, ?, ?)
    ''', (location, room_number, desks, room_type, auth))

conn.commit()
conn.close()
