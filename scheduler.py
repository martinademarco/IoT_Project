import serial
import serial.tools.list_ports
from bridge_Serial_MQTT import Bridge

class Scheduler():

    def __init__(self):
        self.arduini = []
        self.bridges = []

    def loop(self):
        while(True):
            self.checkConnection()
            for bridge in self.bridges:
                if bridge.ser.isOpen():
                    bridge.readData()
                else:
                    self.bridges.remove(bridge)
                    self.arduini.remove(bridge.port.device)

    
    def checkConnection(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino Uno' in port.description:
                if port.device not in self.arduini:
                    self.arduini.append(port.device)
                    self.bridges.append(Bridge(port))

    
if __name__ == '__main__':
    sc = Scheduler()
    sc.loop()