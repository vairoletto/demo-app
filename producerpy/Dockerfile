# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY main.py .

# Install dependencies (if any)
RUN pip install fastapi uvicorn pydantic pika 

# Expose the port that the application will run on
EXPOSE 3004

# Define the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3004"]
