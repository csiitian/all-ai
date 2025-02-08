# Use an official Python base image
FROM python:3.9

# Install required system dependencies
RUN apt-get update && apt-get install -y curl

COPY requirements.txt requirements.txt

# Update pip
RUN pip install --upgrade pip

# Install Flask and requests
RUN pip install -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set the working directory
WORKDIR /app

# Copy Flask app into the container
COPY main.py main.py

RUN ollama serve & ollama pull deepseek-r1:1.5b

# Expose Flask and Ollama ports
EXPOSE 5000 11434

RUN python3 main.py
