# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MY_VAR=my_value

# Set the working directory to /django-app
WORKDIR /django-app

# Copy the current directory contents into the container at /django-app
COPY . /django-app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
        pip install gunicorn
        
RUN python manage.py collectstatic --no-input        

# Make port 8000 available to the world outside this container
RUN chmod +x gunicorn.sh
EXPOSE 8000
ENTRYPOINT ["./gunicorn.sh"]
# Run command to start the application
# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
