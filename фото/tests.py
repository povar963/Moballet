import sqlite3

sqlite_connection = sqlite3.connect('../transactions.sqlite')
cursor = sqlite_connection.cursor()
print("Подключен к SQLite")

sqlite_insert_with_param = """INSERT INTO spendings
                      (names, summs, time)
                      VALUES (?, ?, ?);"""

data_tuple = ("gops", 342, "32.z34.534f")
cursor.execute(sqlite_insert_with_param, data_tuple)
sqlite_connection.commit()
print("Переменные Python успешно вставлены в таблицу sqlitedb_developers")

cursor.close()