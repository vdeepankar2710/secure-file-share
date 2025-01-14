# Use Python 3.8 as the base image
FROM python:3.8

WORKDIR /code

COPY secureFileShare/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY secureFileShare/ /code/secureFileShare

COPY certificates/ /code/certificates

WORKDIR /code/secureFileShare
CMD ["python", "./run_dev_secure.py"]
