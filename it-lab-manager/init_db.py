import sqlite3

connection = sqlite3.connect("lab.db")

with open("schema.sql") as file:
    connection.executescript(file.read())

connection.close()

print("Database created successfully.")