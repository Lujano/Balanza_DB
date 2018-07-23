#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep
import datetime
import os
import logging
from hx711 import HX711	
import sqlite3
import sys
from flask import Flask, render_template, Response
from flask import request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('Balanza.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
global last_caldata, last_caldate, envivo


# Funcion para agregar datos a la tabla 
def add_data (medida, tara, calibdata, calibdate):
    conn=sqlite3.connect('celdaData.db')
    curs=conn.cursor()
    curs.execute("INSERT INTO Scale_data values(datetime('now'), (?), (?), (?), (?))", (medida, tara, calibdata, calibdate))
    conn.commit()
    conn.close()     # cierra la base de datos despues de usarla.

def tarar():
    result = hx.zero(times=10)
    if result:			
        logger.debug('Tara de usuario= {}'.format(hx.get_current_offset(channel='A', gain_A=64)))
    else:
        logger.debug('No se pudo realizar la tara inicial')
    add_data (result, hx.get_current_offset(channel='A', gain_A=64), last_caldata, last_caldate)


def calibrar():  
    input('Coloque peso de 1KG y pulse enter')
    data = hx.get_data_mean(times=10)
    global last_caldata, last_caldate
    if data != False:
        known_weight_grams = 1000
        # Ajusta el radio para el canal y ganancia particular,  
        # este valor se usa para calcular la unidad de conversion. para
        #ajustarlo se debe ingresar un peso conocido de 1000gramos.
        last_caldata = data / known_weight_grams	# calcula el radio para canal A ganancia 64
        last_caldate = datetime.datetime.now()
        hx.set_scale_ratio(scale_ratio=last_caldata)	# ajusta el radio
        add_data (last_caldata, hx.get_current_offset(channel='A', gain_A=64), last_caldata, last_caldate)
        logger.debug("calibrado a: {}".format(last_caldata))
        
def pesar():
    global last_caldata, last_caldate
    peso = hx.get_data_mean(times=10)
    add_data (peso, hx.get_current_offset(channel='A', gain_A=64), last_caldata, last_caldate)
    logger.debug('Valor pesado: {}'.format(peso))

# Flask app

app = Flask(__name__)

@app.route('/')
def index():
    """Pagina principal"""
    return render_template('index.html')



@app.route('/Balanza/Tara',  methods = ['GET', 'POST'])
def Form():
    time_now = time.asctime(time.localtime(time.time()))
    template_data = {
        'time': time_now
    }
    return render_template('TaraPage.html', **template_data)

if __name__ == '__main__':
    app.run(host = '127.1.1.1', debug= True, threaded=True, port= 5000)
