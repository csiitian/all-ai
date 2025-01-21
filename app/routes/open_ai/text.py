from flask import Blueprint, jsonify, request, send_file
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os, io, tempfile, requests, json
from datetime import datetime

open_ai_text_blueprint = Blueprint('open_ai_text', __name__, url_prefix='/open_ai')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0125"]

@open_ai_text_blueprint.route('/moderate', methods=['POST'])
def moderate_content():
  data = request.json
  prompt = data['prompt']
  try:
    response = client.moderations.create(
      model = "omni-moderation-latest",
      input = prompt
    )
    result = response.results[0].categories.json()
    return jsonify({'response': result})
  except OpenAIError as e:
    return jsonify({'error': e.message})

@open_ai_text_blueprint.route('/text', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data['prompt']
    model = data['model'] if 'model' in data and data['model'] in models else "gpt-3.5-turbo"
    try:
      response = client.chat.completions.create(
        model = model,
        messages = [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": prompt}
        ]
      )
      result = response.choices[0].message.content
      return jsonify({'response': result})
    except OpenAIError as e:
      return jsonify({'error': e.message})

@open_ai_text_blueprint.route("/fine-tuned-completion", methods=["POST"])
def fine_tuned_completion():
  data = request.json
  prompt = data["prompt"]
  fine_tuned_model = data["model"]
  if not prompt or not fine_tuned_model:
    return jsonify({"error": "Both prompt and model are required"}), 400

  try:
    response = client.chat.completions.create(
      model=fine_tuned_model,  # Use your fine-tuned model ID
      messages = [
        {"role": "user", "content": prompt}
      ]
    )
    
    result = response.choices[0].message.content
    return jsonify({'response': result})
  except Exception as e:
    return jsonify({"error": str(e)}), 500
