import sqlite3 as lite
import sys
con = lite.connect('celdaData.db')
with con: 
    cur = con.cursor() 
    cur.execute("DROP TABLE IF EXISTS Scale_data")
    cur.execute("CREATE TABLE Scale_data(timestamp DATETIME, peso NUMERIC, tara NUMERIC, caldata NUMERIC, caldate DATETIME)")
con.close()
print("BASE DE DATOS DE BALANZA INICIALIZADA CORRECTAMENTE")


