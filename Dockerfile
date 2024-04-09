# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /AccuKnox_Assignment/

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run `python manage.py runserver 0.0.0.0:8000` when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
