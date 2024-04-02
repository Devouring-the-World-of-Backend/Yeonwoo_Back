import sqlite3

con=sqlite3.connect('library.db')

cur=con.cursor()

con.execute=("CREATE TABLE lang(name, first_appeared)")

con.commit()
con.close()