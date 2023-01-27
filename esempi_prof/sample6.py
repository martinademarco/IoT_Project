#POST GET

from flask import Flask
from config import Config


appname = "IOT - sample1"
app = Flask(appname)
myconfig = Config
app.config.from_object(myconfig)

elenco=[]

@app.route('/')
def testoHTML():
    return '<h1>I love IoT</h1>'


@app.route('/lista', methods=['GET'])
def stampalista():
    txt = ";".join(elenco)
    return txt

@app.route('/addinlista/<name>', methods=['POST'])
def addinlista(name):
    elenco.append(name)
    return str(len(elenco))


if __name__ == '__main__':
    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)