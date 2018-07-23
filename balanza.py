import sqlite3
import sys
conn=sqlite3.connect('celdaData.db')
curs=conn.cursor()


# Funcion para agregar datos a la tabla 
def add_data (medida, tara, calibdata, calibdate):
    curs.execute("INSERT INTO Scale_data values(datetime('now'), (?), (?), (?), (?))", (medida, tara, calibdata, calibdate))
    conn.commit()

#agraga datos a la db
add_data (20.5, 30, 888, "2018-07-05 12:40:05")


# Muestra el contenido de la base de datos
print ("\nContenido completo de la base de datos:\n")
for row in curs.execute("SELECT * FROM Scale_data"):
    print (row)

# cierra la base de datos despues de usarla.
conn.close()