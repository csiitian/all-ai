from flask import Blueprint, jsonify, request, send_file
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os, io, tempfile, requests, json
from datetime import datetime

open_ai_audio_blueprint = Blueprint('open_ai_audio', __name__, url_prefix='/open_ai')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0125"]
voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
image_models = ["dall-e-2", "dall-e-3"]
audio_models = ["tts-1", "tts-1-hd"]

@open_ai_audio_blueprint.route('/transcript', methods=['POST'])
def generate_transcript():
  audio_file = request.files['file']
  file_data = audio_file.read()
  file_stream = io.BytesIO(file_data)
  file_stream.name = "input.mp3"

  try:
    response = client.audio.transcriptions.create(
      file = file_stream,
      model = "whisper-1",
      response_format = "text",
    )
    return jsonify({'response': response})
  except OpenAIError as e:
    return jsonify({'error': e.message})

@open_ai_audio_blueprint.route('/audio', methods=['POST'])
def generate_audio():
  data = request.json
  prompt = data['prompt']
  voice = data['voice'] if 'voice' in data and data['voice'] in voices else "alloy"
  model = data['model'] if 'model' in data and data['model'] in audio_models else "tts-1"
  try:
    response = client.audio.speech.create(
      model = model,
      voice = voice,
      input = prompt
    )
    
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_file:
      response.stream_to_file(tmp_file.name)
      tmp_file.flush()
      temp_path = tmp_file.name

      return send_file(
        temp_path,
        mimetype='audio/mpeg',
        as_attachment=True,
        download_name='output.mp3'
      )
  except OpenAIError as e:
    return jsonify({'error': e.message})

