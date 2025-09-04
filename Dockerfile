# Use an official Python runtime as a parent image.
# We choose a lightweight version to keep the image small.
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Set the timezone inside the container to Asia/Bangkok
# This ensures that all timestamps inside the container will match local time.
ENV TZ=Asia/Bangkok

# Copy the requirements.txt file and install Python dependencies.
# This step is cached, which speeds up future builds if dependencies don't change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file to the root of the working directory
COPY .env .

# Copy the entire application code into the container
COPY . .

# Expose the port on which the FastAPI application will run
EXPOSE 8000

# Command to run the application using Uvicorn
# We use the host "0.0.0.0" to make the service accessible from outside the container
# We explicitly set the PYTHONPATH to include the parent directory of our app package.
CMD ["/usr/local/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
