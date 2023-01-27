# sample4
# vector

from flask import Flask


appname = "IOT - sample4"
app = Flask(appname)

elenco=[]

@app.route('/')
def testoHTML():
    return '<h1>I love IoT</h1>'


@app.route('/lista')
def stampalsita():
    txt = ";".join(elenco)
    return txt

@app.route('/addinlista/<name>')
def addinlista(name):
    if name == 'juve':
        pass
    else:
        elenco.append(name)
    return str(len(elenco))


if __name__ == '__main__':
    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)