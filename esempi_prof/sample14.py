# sample9
# errors

from flask import Flask
from config import Config
from flask import render_template
# pip install flask_swagger
from flask_swagger import swagger
from flask import jsonify

appname = "IOT - sample1"
app = Flask(appname)
myconfig = Config
app.config.from_object(myconfig)

elenco=[]


@app.errorhandler(404)
def page_not_found(error):
    return 'Errore pagina non trovata', 404

@app.route('/')
def testoHTML():
    return '<h1>I love IoT</h1>'


@app.route('/lista', methods=['GET'])
def stampalista():
    """
    Create a new user
    ---
    tags:
      - users
    definitions:
      - schema:
          id: Group
          properties:
            name:
             type: string
             description: the group's name
    parameters:
      - in: body
        name: body
        schema:
          id: User
          required:
            - email
            - name
          properties:
            email:
              type: string
              description: email for user
            name:
              type: string
              description: name for user
            address:
              description: address for user
              schema:
                id: Address
                properties:
                  street:
                    type: string
                  state:
                    type: string
                  country:
                    type: string
                  postalcode:
                    type: string
            groups:
              type: array
              description: list of groups
              items:
                $ref: "#/definitions/Group"
    responses:
      201:
        description: User created
    """

    return render_template('lista2.html', lista=elenco)

@app.route('/addinlista/<name>', methods=['POST'])
def addinlista(name):
    elenco.append(name)
    return str(len(elenco))

@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "My API"
    
    return jsonify(swag)

if __name__ == '__main__':
    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port)