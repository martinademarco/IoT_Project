import serial
import serial.tools.list_ports
import time

import configparser

class Seriale():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.ports = {}
        self.setupSerial()

    def setupSerial(self):        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                # apre la porta seriale
                ser = serial.Serial(port.device, 9600, timeout=2)
                print(port.device)
                time.sleep(2)
                # scrive un messaggio sull'Arduino
                ser.write(b'\xff')
                # legge la risposta dell'Arduino
                response = ser.read()
                print(response)
                # verifica se l'Arduino ha risposto correttamente
                if response == b'\xfe':
                    print(f"Arduino connesso alla porta {port.device}")
                    # se l'Arduino è stato trovato aggiungi il suo id al dizionario con il buffer associato, esci dal ciclo
                    size = int(ser.read(1).decode())
                    val = ser.read(size)
                    self.ports[val.decode()] = ser
                else:
                    # se l'Arduino non ha risposto correttamente, chiude la porta seriale
                    ser.close()
                    print('Errore nella connessione')
            except (OSError, serial.SerialException):
                print('Qualcosa è andato storto...')

        
        