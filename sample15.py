from flask import Flask
from flask import request
from config import Config
from flask import render_template
from flask_swagger import swagger
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from influxdb import InfluxDBClient

appname = "IOT - sample1"
app = Flask(appname)
myconfig = Config
app.config.from_object(myconfig)
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('sensors') 

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/spec'  # Our API url (can of course be a local resource)

@app.errorhandler(404)
def page_not_found(error):
    return 'Errore pagina non trovata', 404

@app.route('/')
def testoHTML():
    # db.create_all()
    return render_template('main.html')


@app.route('/lista/<sensor>', methods=['GET'])
def stampalista(sensor):
    """
    Print the list
    ---
 
    responses:
      200:
        description: List
    """
    # elenco=Sensorfeed.query.order_by(Sensorfeed.id.asc()).all()
    # return render_template('lista3.html', lista=elenco)
    result = client.query("SELECT value FROM temperature WHERE sensor = '{}'".format(sensor))
    points = result.get_points()
    temperatures = [point['value'] for point in points]
    return jsonify(temperatures)

@app.route('/addinlista/<sensor>/<value>', methods=['POST'])
def addinlista(sensor, value):
    """
    Add element to the list
    ---
    parameters:
        - in: path
          name: sensor
          description: arg
          required: true
        - in: path
          name: value
          description: integer
          required: true
    responses:
      200:
        description: List
    """
    json_body = [
        {
            "measurement": "temperature",
            "tags": {
                "sensor": sensor
            },
            "fields": {
                "value": value
            }
        }
    ]
    client.write_points(json_body)
    return "Data added"
    

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