# Use the base image with Python 3.11
FROM python:3.11-slim

# Install Git
RUN apt-get update && apt-get install -y git && apt-get clean

# Set the working directory
WORKDIR /app

# Install FastAPI and Uvicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application into the image
COPY . .

# Set the default command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

