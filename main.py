from flask import Flask
from flask import render_template
from flask_swagger import swagger
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import configparser
import requests

def on_connect(clientMQTT, userdata, flags, rc):
        #print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        clientMQTT.subscribe("Tsensor_0")
        clientMQTT.subscribe("LvLsensor_0")
        clientMQTT.subscribe("LvLsensor_1")

def on_message(clientMQTT, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    url = config.get("HTTP","Url") + "/newdata" + f"/{msg.topic}" + f"/{msg.payload.decode()}"
    try:
        requests.post(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


appname = "IOT - sample1"
app = Flask(appname)
config = configparser.ConfigParser()
config.read('config.ini')
client = influxdb_client.InfluxDBClient(url=config.get("InfluxDBClient","Url"),
   token=config.get("InfluxDBClient","Token"),
   org=config.get("InfluxDBClient","Org"))

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/spec'  # Our API url (can of course be a local resource)

@app.errorhandler(404)
def page_not_found(error):
    return 'Errore pagina non trovata', 404

@app.route('/')
def testoHTML():
    return render_template('main.html')


@app.route('/lista/<sensor>', methods=['GET'])
def stampalista(sensor):
    """
    Print the list
    ---
    parameters:
        - in: path
          name: sensor
          description: arg
          required: true
    responses:
      200:
        description: List
    """
    query_api = client.query_api()
    query = f'from(bucket:"{config.get("InfluxDBClient","Bucket")}")\
    |> range(start: -1h)\
    |> filter(fn:(r) => r._measurement == "new_measurement")\
    |> filter(fn:(r) => r.sensor == "{sensor}")\
    |> filter(fn:(r) => r._field == "value")'
    result = query_api.query(org=config.get("InfluxDBClient","Org"), query=query)
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_value(), record.get_time()))
    return render_template('lista3.html', lista=results)

@app.route('/newdata/<sensor>/<value>', methods=['POST'])
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
    write_api = client.write_api(write_options=SYNCHRONOUS)
    measure = influxdb_client.Point("new_measurement").tag("sensor", sensor).field("value", float(value))
    write_api.write(bucket=config.get("InfluxDBClient","Bucket"), org=config.get("InfluxDBClient","Org"), record=measure)
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

    clientMQTT = mqtt.Client()
    clientMQTT.on_connect = on_connect
    clientMQTT.on_message = on_message
    print("connecting to MQTT broker...")
    clientMQTT.connect(
        config.get("MQTT","Server", fallback= "broker.hivemq.com"),
        config.getint("MQTT","Port", fallback= 1883),
        60)

    clientMQTT.loop_start()
    
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