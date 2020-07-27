from flask import Flask, request, render_template
import base64
import io
import numpy as np    
from PIL import Image
import os

app = Flask(__name__, template_folder='./templates/')

@app.route('/')
def main():
  prediction_path = './static/prediction.png'
  return render_template('index.html', prediction_path=prediction_path)

@app.route('/upload', methods=['POST'])
def upload():
  if request.method == 'POST':
    f = request.files['file']
    f.save('./static/input.png')

    if os.path.exists('./static/prediction.png'):
      os.remove('./static/prediction.png') # TEMP CONDITION 

  return render_template('index.html')

@app.route('/predictions', methods=['POST']) # GET for user, POST for receiving predictions from model
def predictions():
  if request.method == 'POST':
    img_prop_enc = request.form.get('img_props')
    img_prop = list(base64.b64decode(img_prop_enc))

    img_enc = request.form.get('predictions')
    img_dec = base64.b64decode(img_enc)
    img = Image.frombytes('RGB', (img_prop[1], img_prop[0]), img_dec, 'raw')

    prediction_path = './static/prediction.png'
    img.save(prediction_path)

    return render_template('index.html', prediction_path=prediction_path)

app.run(host='0.0.0.0', port=8080)