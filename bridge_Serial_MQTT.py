import serial
import serial.tools.list_ports
import socket

import configparser
import requests
import paho.mqtt.client as mqtt
import time

class Bridge():

	def __init__(self, port):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.buffer = []
		self.datiZona = {}
		self.ser = None
		self.setupSerial(port)
		self.setupMQTT()


	def setupMQTT(self):
		self.clientMQTT = mqtt.Client()
		self.clientMQTT.on_connect = self.on_connect
		self.clientMQTT.on_message = self.on_message
		print("connecting to MQTT broker...")
		self.clientMQTT.connect(
			self.config.get("MQTT","Server", fallback= "broker.hivemq.com"),
			self.config.getint("MQTT","Port", fallback= 1883),
			60)
		self.clientMQTT.loop_start()


	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		self.clientMQTT.subscribe(self.zona + '/' + self.id + '/' + "Tsensor_0")
		self.clientMQTT.subscribe(self.zona + '/' + self.id + '/' + "LvLsensor_0")
		self.clientMQTT.subscribe(self.zona + '/' + self.id + '/' + "LvLsensor_1")
		self.clientMQTT.subscribe(self.zona + '/+/Tsensor_0')

    # The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic + " " + str(msg.payload))
		if msg.topic == self.zona + '/' + self.id + '/' + "LvLsensor_0":
			if float(msg.payload.decode())<15:
					self.ser.write(b'A0')
			else:
				self.ser.write(b'S0')
		elif msg.topic == self.zona + '/' + self.id + '/' + "Tsensor_0":
			dati = list(self.datiZona.values())
			media = sum(dati) / len(dati)
			if float(msg.payload.decode())>media + 3:
					self.ser.write(b'A1')
			else:
				self.ser.write(b'S1')
		elif msg.topic == self.zona + '/' + self.id + '/' + "LvLsensor_1":
			if float(msg.payload.decode())<15:
					self.ser.write(b'A2')
			else:
				self.ser.write(b'S2')
		elif msg.topic == self.zona + '/+/Tsensor_0':
			string = msg.payload.decode()
			id, temperatura = string.strip(',')
			self.datiZona[id] = temperatura
		hostname = socket.gethostname()    
		IPAddr = socket.gethostbyname(hostname)
		url = IPAddr + "/newdata" + f"/{msg.topic}" + f"/{msg.payload.decode()}"
		try:
			requests.post(url)
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)

	def readData(self):
		#look for a byte from serial
		if self.ser.in_waiting>0:
			# data available from the serial port
			lastchar=self.ser.read(1)

			if lastchar==b'\xfe': #EOL
				print("\nValue received")
				self.useData()
				self.buffer = []
			else:
				# append
				self.buffer.append(lastchar)

	def useData(self):
		print(self.buffer)
		# I have received a packet from the serial port. I can use it

		if self.buffer[0] != b'\xff':
			print('Pacchetto errato')
			return False
		numval = int(self.buffer[1].decode()) # legge size del pacchetto
		val = ''
		for i in range (numval):
			val = val + self.buffer[i+2].decode() # legge valore del pacchetto
		sensor_name = ''
		SoN = numval + 2
		sensorLen = len(self.buffer) - (SoN)
		for j in range (sensorLen):
			sensor_name = sensor_name + str(self.buffer[j + SoN].decode())
		self.clientMQTT.publish(self.zona + '/' + self.id + '/' + sensor_name, val)
		if sensor_name == 'TSensor_0':
			self.clientMQTT.publish(self.zona + '/+/' + sensor_name, self.id + ',' + str(val))

	def setupSerial(self, port):        
		try:
			# apre la porta seriale
			self.ser = serial.Serial(port.device, 9600, timeout=2)
			time.sleep(2)
			# scrive un messaggio sull'self
			self.ser.write(b'\xff')
			# legge la risposta dell'self
			response = self.ser.read()
			# verifica se l'self ha risposto correttamente
			if response == b'\xfe':
				print(f"self connesso alla porta {port.device}")
				# se l'self è stato trovato aggiungi il suo id al dizionario con il buffer associato, esci dal ciclo
				size_zona = int(self.ser.read().decode())
				self.zona = self.ser.read(size_zona)
				#size_id = int(self.ser.read().decode())
				self.id = self.ser.read(3)
				self.portName = port.device
				return True
			else:
				# se l'self non ha risposto correttamente, chiude la porta seriale
				self.ser.close()
				print('Errore nella connessione')
				return False
		except (OSError, serial.SerialException):
			pass
