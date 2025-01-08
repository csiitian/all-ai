from flask import Flask, request, jsonify, send_file
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os, io, tempfile

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
client = OpenAI(api_key=api_key)

models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0125"]
voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
image_models = ["dall-e-2", "dall-e-3"]
audio_models = ["tts-1", "tts-1-hd"]

@app.route('/ai/moderate', methods=['POST'])
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

@app.route('/ai/transcript', methods=['POST'])
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

@app.route('/ai/audio', methods=['POST'])
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

      print(f"temp_path: {temp_path}")

      return send_file(
          temp_path,
          mimetype='audio/mpeg',
          as_attachment=True,
          download_name='output.mp3'
      )
  except OpenAIError as e:
    return jsonify({'error': e.message})

@app.route('/ai/image', methods=['POST'])
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
      return jsonify({'response': result})
    except OpenAIError as e:
      return jsonify({'error': e.message})

@app.route('/ai/text', methods=['POST'])
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

# test endpoint
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Hello World!'})    

if __name__ == '__main__':
    app.run(debug=True, port=3000)
