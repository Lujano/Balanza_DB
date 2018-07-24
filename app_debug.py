#!/usr/bin/python3
#https://stackoverflow.com/questions/13386681/streaming-data-with-python-and-flask
#http://flask.pocoo.org/docs/1.0/patterns/streaming/#streaming-from-templates
import time
import datetime
import os
import logging
import sqlite3
import sys
from flask import Flask, render_template, Response, stream_with_context, flash
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
    result = 0
    if result:			
        logger.debug('Tara de usuario= {}'.format(hx.get_current_offset(channel='A', gain_A=64)))
    else:
        logger.debug('No se pudo realizar la tara inicial')
    add_data (result, hx.get_current_offset(channel='A', gain_A=64), last_caldata, last_caldate)


def calibrar():  
    #input('Coloque peso de 1KG y pulse enter')
    data = 10
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
    peso = 15
    add_data (peso, hx.get_current_offset(channel='A', gain_A=64), last_caldata, last_caldate)
    logger.debug('Valor pesado: {}'.format(peso))

# Flask app
def stream_template(template_name, **context):
    # http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv

app = Flask(__name__)

@app.route('/')
def index():
    """Pagina principal"""
    return render_template('index.html')



@app.route('/Balanza/Tarar')
def tarar():
    time_now = time.asctime(time.localtime(time.time()))
    tara = 10
    template_data = {
        'time': time_now,
        'tara_out': tara
    }
    return render_template('TararPage.html', **template_data)

@app.route('/Balanza/PesarWindow')
def pesar_window():
    def g():
        num = 0
        while True:
            time.sleep(1)  # an artificial delay
            num +=2
            yield num
    return Response(stream_with_context(stream_template('PesarWindow.html', data=g())))

@app.route('/Balanza/Pesar')
def pesar():
    return render_template('PesarPage.html')

@app.route('/Balanza/Calibrar')
def calibrar_page():
    return render_template('CalibrarPage.html')

@app.route('/Balanza/CalibrarEXE', methods=['POST'])
def calibrar():
    forward_message = "Moving Forward..."
    templateData = {
        'data': "da"
    }
    return render_template('CalibrarPage.html', **templateData)

if __name__ == '__main__':
    app.run(host = '127.1.1.1', debug= True, threaded=True, port= 5000)
