from junction import junctionModel
from flask import Flask, request

#from flask_json import FlaskJSON, JsonError, json_response, as_json

app = Flask(__name__)
#json= FlaskJSON(app)

model = None

# Define simulation parameters
@app.route("/setup", methods=['POST'])
def setup():
    cars = (request.values.get('cars'))
    width = (request.values.get('width'))
    height = (request.values.get('height'))
    
    err = str()
    if not cars or not cars.isdigit() or int(cars) < 5:
        err += "Invalid cars (min. 5)\n"
    if not width or not width.isdigit() or int(width) < 7:
        err += "Invalid width (min. 7)\n"
    if not height or not height.isdigit() or int(height) < 7:
        err += "Invalid height (min. 7)\n"
    if len(err) > 0:
        return err, 400

    parameters = {
    'cars': int(cars),
    'width': int(width),
    'height': int(height),
    }

    global model
    model = junctionModel(parameters=parameters)
    model.setup()
    
    positions = dict()
    for agent in model['agents'].select(model['agents'].status < 20):
        positions[agent['id']] = model['ground'].positions[agent]

    return positions, 200

@app.route("/step", methods = ['GET'])
def get_step():
    if model == None:
        return "Model has not yet been instantiated\n", 400

    model.step()

    positions = dict()
    for agent in model['agents'].select(model['agents'].status < 20):
        positions[agent['id']] = model['ground'].positions[agent]

    return positions, 200
