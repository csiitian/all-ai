from flask import Flask, render_template
from app.routes import register_routes
import os

app = Flask(__name__)

register_routes(app)

# test endpoint
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Hello World!'})

@app.route('/gallery')
def gallery():
    image_folder = os.path.join(app.static_folder, 'images')  # Path to static/images
    image_files = [f"images/{file}" for file in os.listdir(image_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]  # List image files
    return render_template("gallery.html", images=image_files)  # Pass image paths to template

if __name__ == '__main__':
    app.run(debug=True, port=3000)
