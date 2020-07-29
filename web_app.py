from flask import Flask, request, render_template, redirect
import base64
import io
import numpy as np    
from PIL import Image
import os
import time
import json
import requests

IMGUR_URL = 'https://api.imgur.com/3/'
CLIENT_ID = '853e92d46b2081a'
CLIENT_SECRET = '5c77e3cad7f64553ce00913309896c4482ed0c79'
RAGIC_ID = 'WGhod3FVU0lmNHNjaXVyTmpXbUJhVjlKMUNxTGVZM2JJejk2K2FHRW5XT3I2dXB5bXY0UythaWVQbUd6MXUrS293TjZKT1VBYStBPQ=='

app = Flask(__name__, template_folder='./templates/')

@app.route('/')
def main():
  return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
  if request.method == 'POST':
    f = request.files['file']
    f.save('./static/img.jpg') # hack
    img_bytes = open('./static/img.jpg', 'rb').read()

    # save to img store
    print('Save to image store')

    res = requests.post(
      url= IMGUR_URL + 'upload.json',
      data={
        'image': base64.b64encode(img_bytes),
        'type': 'base64',
      },
      headers={
        'Authorization': 'Client-ID ' + CLIENT_ID,
      }
    )

    data = json.loads(res.content.decode("utf-8"))['data']

    # save to database
    print('Save to database')

    res = requests.post(
      url='https://na3.ragic.com/weewoowarrior/hairygan/2?v=3&api', 
      params={
          '1000014': data['link'],
          '1000015': data['height'],
          '1000016': data['width'], 
          '1000017': '', # predicted url
          '1000018': 0, # processed
          '1000020': 1, # eyeglasses
      },
      headers={
          'Authorization': 'Basic ' + RAGIC_ID
      }
  )

  return redirect('/')

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

    return render_template('index.html')

app.run(host='0.0.0.0', port=8080)