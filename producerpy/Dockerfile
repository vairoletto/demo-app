# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY main.py .

# Copy New Relic configuration to the container
COPY newrelic.ini .

# Copy the start script
COPY start.sh .

# Set execute permissions for the script
RUN chmod +x start.sh

# Install dependencies (if any)
RUN pip install fastapi uvicorn pydantic pika newrelic

# Expose the port that the application will run on
EXPOSE 3004

# Define the command to run the application
CMD ["./start.sh"]