#!/bin/sh

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start
sleep 5

# Pull the required model
ollama pull deepseek-r1:1.5b

# Start the Flask server
python /app/app.py
