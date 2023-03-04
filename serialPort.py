import serial
import serial.tools.list_ports
import time

import configparser

class Seriale():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.zona = ""
        self.id = ""
        self.portName = ""
        self.buffer = []
        self.connect = False # non connesso al broker MQTT
        self.ser = None

    def setupSerial(self, port):        
        try:
            # apre la porta seriale
            self.ser = serial.Serial(port.device, 9600, timeout=2)
            time.sleep(2)
            # scrive un messaggio sull'Arduino
            self.ser.write(b'\xff')
            # legge la risposta dell'Arduino
            response = self.ser.read()
            # verifica se l'Arduino ha risposto correttamente
            if response == b'\xfe':
                print(f"Arduino connesso alla porta {port.device}")
                # se l'Arduino è stato trovato aggiungi il suo id al dizionario con il buffer associato, esci dal ciclo
                size_zona = int(self.ser.read().decode())
                self.zona = self.ser.read(size_zona)
                size_id = int(self.ser.read().decode())
                self.id = self.ser.read(size_id)
                self.portName = port.device
                return True
            else:
                # se l'Arduino non ha risposto correttamente, chiude la porta seriale
                self.ser.close()
                print('Errore nella connessione')
                return False
        except (OSError, serial.SerialException):
            pass