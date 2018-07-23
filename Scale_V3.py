#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep
import datetime
import os
import logging
from hx711 import HX711	
import sqlite3
import sys

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

        
if __name__=='__main__':
    try: 
        logger.debug("Comenzando...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Configura boton tara
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Configura boton pesa
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Configura boton calibra

        hx = HX711(dout_pin=5, pd_sck_pin=6, gain_channel_A=128, select_channel='B')
        
        result = hx.reset()
        if result:			
            logger.debug('Modulo HX711 Inicializado correctamente')
        else:
            logger.debug('No se pudo inicializar el modulo HX711')
        
        hx.set_gain_A(gain=64)		# Selecciona la ganancia del modulo HX711
        hx.select_channel(channel='A')	# Para el canal A
        
        # Realiza tara inical y la guarda como offset del canal y ganancia seleccionado
        result = hx.zero(times=10)
        if result:			
            logger.debug('Tara inicial = {}'.format(hx.get_current_offset(channel='A', gain_A=64)))
        else:
            logger.debug('No se pudo realizar la tara inicial')
        
        conn = sqlite3.connect('celdaData.db')
        curs = conn.cursor()
        dato = (curs.execute ("SELECT * FROM Scale_data ORDER BY timestamp DESC LIMIT 1;")).fetchone()
        global last_caldata
        global last_caldate
        last_caldata = dato[3]     
        hx.set_scale_ratio("A", 64, last_caldata)     #Carga la ultima calibracion registrada
        last_caldate = dato[4]
        conn.close()     # cierra la base de datos despues de usarla.
        
        GPIO.add_event_detect(22, GPIO.FALLING, callback=calibrar, bouncetime=300)  
        GPIO.add_event_detect(17, GPIO.FALLING, callback=tarar, bouncetime=300) 
        GPIO.add_event_detect(27, GPIO.FALLING, callback=pesar, bouncetime=300) 
        

        while (True):
            #envivo = hx.get_data_mean(times=10)
            #print(envivo)
            pesar()
            
                

    except KeyboardInterrupt:
        logger.debug("Programa terminado por usuario")
        exit(0)
    except Exception as e:
        logger.error("Error durante ejecucion:")
        logger.exception(e)            
    finally:
        GPIO.cleanup()
        GPIO.cleanup()
        conn.close()
        exit(1)       


