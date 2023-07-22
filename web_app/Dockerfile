# syntax=docker/dockerfile:1
FROM python:3

WORKDIR /usr/src/app

COPY web_app/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy database folder as code dependancy
COPY database ./database
COPY web_app ./web_app

EXPOSE 8000

# Running commands for the startup of a container.
CMD python web_app/main.py