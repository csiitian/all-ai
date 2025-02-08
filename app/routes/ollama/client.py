from flask import Blueprint, request
import json, os, requests
from dotenv import load_dotenv
from .helper import parseDeepseekResponse

ollama_blueprint = Blueprint('ollama', __name__, url_prefix='/ollama')

load_dotenv()
ollama_base_url = os.getenv("OLLAMA_BASE_URL")

models = ["deepseek-r1:1.5b"]

@ollama_blueprint.route('/text', methods=['POST'])
def generate_text():
  url = f"{ollama_base_url}/api/generate"
  headers = {"Content-Type": "application/json"}
  data = request.json
  model = data['model'] if 'model' in data and data['model'] in models else "deepseek-r1:1.5b"
  prompt = data['prompt']
  data = {"model": model, "prompt": prompt, "stream": False}

  response = requests.post(url, headers=headers, json=data)

  if response.status_code == 200:
    return parseDeepseekResponse(response.json()['response'])
  else:
    return {"error": response.text}