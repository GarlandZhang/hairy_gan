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
DB_URL = 'https://na3.ragic.com/weewoowarrior/hairygan/2?v=3&api'

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
      url=DB_URL, 
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

    entry_id = json.loads(res.content)['data']['_ragicId']

    # stall until dont
    while True:
      db_data_retrieval_res = requests.get(
        url=DB_URL,
        headers={
          'Authorization': 'Basic ' + RAGIC_ID
        }
      )
      retrieved_data = json.loads(db_data_retrieval_res.content)

      entry = retrieved_data[str(entry_id)]

      if int(entry['processed']) == 1:
        break
      
      time.sleep(1)


  return redirect('/predictions/' + str(entry_id))

@app.route('/predictions/<int:entry_id>') # GET for user, POST for receiving predictions from model
def predictions(entry_id):
  db_data_retrieval_res = requests.get(
    url=DB_URL,
    headers={
      'Authorization': 'Basic ' + RAGIC_ID
    }
  )
  retrieved_data = json.loads(db_data_retrieval_res.content)

  entry = retrieved_data[str(entry_id)]

  original_image_url = entry['original_image_url']

  prediction_image_url = entry['prediction_image_url']

  return render_template('predictions.html', original_image_url=original_image_url, prediction_image_url=prediction_image_url)

app.run(host='0.0.0.0', port=8080)