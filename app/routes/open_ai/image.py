from flask import Blueprint, jsonify, request, send_file
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os, io, tempfile, requests, json
from datetime import datetime

open_ai_image_blueprint = Blueprint('open_ai_image', __name__, url_prefix='/open_ai')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

image_models = ["dall-e-2", "dall-e-3"]

@open_ai_image_blueprint.route('/image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data['prompt']
    size = data['size'] if 'size' in data else "256x256"
    model = data['model'] if 'model' in data and data['model'] in image_models else "dall-e-2"
    n = data['n'] if 'n' in data else 1
    try:
      response = client.images.generate(     
        model = model,
        prompt = prompt,
        n = n,
        size = size,
      )
      result = [data.url for data in response.data]
      # store these images in static directory at root
      for i, url in enumerate(result):
        response = requests.get(url)
        timestamp = int(datetime.now().timestamp())
        with open(f"static/tmp/{timestamp}.png", 'wb') as f:
          f.write(response.content)

      return jsonify({'response': result})
    except OpenAIError as e:
      return jsonify({'error': e.message})
