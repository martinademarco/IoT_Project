from serialPort import Seriale
import serial
import serial.tools.list_ports
import socket

import configparser
import requests
import paho.mqtt.client as mqtt
import time

class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.arduino = []

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
		arduino = self.arduino[-1]
		self.clientMQTT.subscribe(arduino.zona + '/' + arduino.id + '/' + "Tsensor_0")
		self.clientMQTT.subscribe(arduino.zona + '/' + arduino.id + '/' + "LvLsensor_0")
		self.clientMQTT.subscribe(arduino.zona + '/' + arduino.id + '/' + "LvLsensor_1")

    # The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic + " " + str(msg.payload))
		for port in self.seriale.ports.keys():
			if msg.topic == port + "LvLsensor_0":
				if float(msg.payload.decode())<15:
						self.seriale.ports[port].write(b'A0')
				else:
					self.seriale.ports[port].write(b'S0')
			elif msg.topic == port + "Tsensor_0":
				if float(msg.payload.decode())>15:
						self.seriale.ports[port].write(b'A1')
				else:
					self.seriale.ports[port].write(b'S1')
			elif msg.topic == port + "LvLsensor_1":
				if float(msg.payload.decode())<15:
						self.seriale.ports[port].write(b'A2')
				else:
					self.seriale.ports[port].write(b'S2')
		hostname = socket.gethostname()    
		IPAddr = socket.gethostbyname(hostname)
		url = IPAddr + "/newdata" + f"/{msg.topic}" + f"/{msg.payload.decode()}"
		try:
			requests.post(url)
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)

	def loop(self):
		# infinite loop for serial managing
		#
		while (True):
			#look for a byte from serial
			for arduino in self.arduino:
				port = arduino.ser
				if port.isOpen():
					if port.in_waiting>0:
						# data available from the serial port
						lastchar=port.read(1)

						if lastchar==b'\xfe': #EOL
							print("\nValue received")
							self.useData(arduino)
							arduino.buffer = []
						else:
							# append
							arduino.buffer.append(lastchar)
				else:
					self.arduino.remove(arduino)
					print(port + " è stata rimossa")
			self.checkConnection()
				

	def useData(self, arduino):
		inbuffer = arduino.buffer
		print(inbuffer)
		# I have received a packet from the serial port. I can use it

		if inbuffer[0] != b'\xff':
			print('Pacchetto errato')
			return False
		numval = int(inbuffer[1].decode()) # legge size del pacchetto
		val = ''
		for i in range (numval):
			val = val + inbuffer[i+2].decode() # legge valore del pacchetto
		sensor_name = ''
		SoN = numval + 2
		sensorLen = len(inbuffer) - (SoN)
		for j in range (sensorLen):
			sensor_name = sensor_name + str(inbuffer[j + SoN].decode())
		self.clientMQTT.publish(arduino.zona + '/' + arduino.id + '/' + sensor_name, val)
	
	def checkConnection(self):
		ports = serial.tools.list_ports.comports()
		for port in ports:
			if 'Arduino Uno' in port.description:
				if port.device not in self.arduino.portName: # valutare se funziona sennò ciclo for
					seriale = Seriale()
					if seriale.setupSerial(port):
						self.arduino.append(seriale)
						self.setupMQTT()
						time.sleep(1) # controlla se funziona anche senza

if __name__ == '__main__':
	br = Bridge()
	br.loop()
