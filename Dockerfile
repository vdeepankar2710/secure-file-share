# Use Python 3.12.3 as the base image
FROM python:3.12.3

# Set working directory
WORKDIR /code

# Copy requirements file first to leverage Docker cache
COPY secureFileShare/requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code and other necessary files
COPY secureFileShare/ /code/secureFileShare
COPY certificates/ /code/certificates
COPY .env /code/

# Set the working directory to where the application code is
WORKDIR /code/secureFileShare

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python", "run_dev.py"]