from flask import Flask
from flask import request
import base64

app = Flask('app')

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/predictions', methods=['GET', 'POST']) # GET for user, POST for receiving predictions from model
def predictions():
  if request.method == 'GET':
    return 'Display predictions'
  elif request.method == 'POST':
    predictions_enc = request.form.get('predictions')
    predictions = base64.b64decode(predictions_enc)
    return 'Received'

app.run(host='0.0.0.0', port=8080)