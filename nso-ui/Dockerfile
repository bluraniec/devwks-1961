# Pull base image
FROM python:3

# Set environment varibles
ENV PYTHONUNBUFFERED 1
RUN mkdir /nso-ui

# Set work directory
WORKDIR /nso-ui
COPY requirements.txt /nso-ui

# Install dependencies
RUN pip install -r requirements.txt

COPY . /nso-ui
COPY manage.py /nso-ui