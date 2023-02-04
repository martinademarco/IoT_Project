import serial
import serial.tools.list_ports
import requests
import configparser


class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.setupSerial()


	def setupSerial(self):
		# open serial port
		self.ser = None

		if self.config.get("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM1")
		else:
			print("list of available ports: ")
			ports = serial.tools.list_ports.comports()

			for port in ports:
				print (port.device)
				print (port.description)
				if self.config.get("Serial","PortDescription", fallback="arduino").lower() \
						in port.description.lower():
					self.portname = port.device

		try:
			if self.portname is not None:
				print ("connecting to " + self.portname)
				self.ser = serial.Serial(self.portname, 9600, timeout=1)
				print('Connection good')
		except:
			self.ser = None
			print('Connection bad')
		# self.ser.open()

		# internal input buffer from serial
		self.inbuffer = []

	def postdata(self, val):
		sensor = 'Temperature' # differisci tra tre sensori: Temperature, Weight1, Weight2
		url = self.config.get("HTTP","Url") + "/newdata" + f"/{sensor}" + f"/{val}"
		# headers = {'X-AIO-Key': 'aio_WmfO50SOelmkqksWHc19TQjBeVsd'}
		print(url)
		try:
			requests.post(url)
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)

	def loop(self):
		# infinite loop for serial managing
		#
		while (True):
			#look for a byte from serial
			if not self.ser is None:

				if self.ser.in_waiting>0:
					# data available from the serial port
					lastchar=self.ser.read(1)

					if lastchar==b'\xfe': #EOL
						print("\nValue received")
						self.useData()
						self.inbuffer =[]
					else:
						# append
						self.inbuffer.append (lastchar)

	def useData(self):
		print(self.inbuffer)
		# I have received a packet from the serial port. I can use it
		if len(self.inbuffer)<3:   # at least header, size, footer
			return False
		# split parts

		if self.inbuffer[0] != b'\xff':
			return False
		numval = int(self.inbuffer[1].decode())
		val = ''
		for i in range (numval):
			val = val + self.inbuffer[i+2].decode()
		self.postdata(val)


if __name__ == '__main__':
	br=Bridge()
	br.loop()