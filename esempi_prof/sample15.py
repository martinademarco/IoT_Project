# sample9
# errors

from flask import Flask
from config import Config
from flask import render_template
# pip install flask_swagger
# pip install flask-swagger-ui
from flask_swagger import swagger
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint

appname = "IOT - sample1"
app = Flask(appname)
myconfig = Config
app.config.from_object(myconfig)

elenco=[]
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/spec'  # Our API url (can of course be a local resource)


@app.errorhandler(404)
def page_not_found(error):
    return 'Errore pagina non trovata', 404

@app.route('/')
def testoHTML():
    return '<h1>I love IoT</h1>'


@app.route('/lista', methods=['GET'])
def stampalista():
    """
    Print the list
    ---
 
    responses:
      200:
        description: List
    """

    return render_template('lista2.html', lista=elenco)

@app.route('/addinlista/<name>', methods=['POST'])
def addinlista(name):
    """
    Add element to the list
    ---
    parameters:
        - in: path
          name: name 
          description: arg
          required: true
    responses:
      200:
        description: List
    """
    
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
    
    
    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Test application"
        }
    )

    app.register_blueprint(swaggerui_blueprint)

   
    
    app.run(host=interface,port=port)