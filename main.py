from flask import Flask
from flask import render_template
from flask_swagger import swagger
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

appname = "IOT - sample1"
app = Flask(appname)
url = 'http://localhost:8086'
token = 'jeNhl3BOgS7G9-1RP0F3i9BwjAFOP1VB4WA4H9FQgmOjZjJBauIL-XsKos-xNOb620x3PgN5xQv8JOUA44TeGg=='
org = 'IoT_Project'
bucket = 'IoT_Project'
client = influxdb_client.InfluxDBClient(url=url,
   token=token,
   org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

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
    query = f'from(bucket:"{bucket}")\
    |> range(start: -1h)\
    |> filter(fn:(r) => r._measurement == "new_measurement")\
    |> filter(fn:(r) => r.sensor == "{sensor}")\
    |> filter(fn:(r) => r._field == "value")'
    result = query_api.query(org=org, query=query)
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_value(), record.get_time()))
    return render_template('lista3.html', lista=results)

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
          description: float
          required: true
    responses:
      200:
        description: List
    """
    measure = influxdb_client.Point("new_measurement").tag("sensor", sensor).field("value", int(value))
    write_api.write(bucket=bucket, org=org, record=measure)
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