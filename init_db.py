import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO sensor_data (temperatura, humedad, intensidad_luz, humedad_suelo) VALUES (?, ?, ?, ?)",
            (24.5, 50, 18, 26)
            )

cur.execute("INSERT INTO sensor_data (temperatura, humedad, intensidad_luz, humedad_suelo) VALUES (?, ?, ?, ?)",
            (24.9, 51, 19, 21)
            )

cur.execute("INSERT INTO limite (temperatura, humedad, intensidad_luz, humedad_suelo) VALUES (?, ?, ?, ?)",
            (24, 60, 50, 800)
            )

connection.commit()
connection.close()
