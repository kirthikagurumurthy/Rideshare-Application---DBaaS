FROM python:3.7-slim-stretch

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir -p /project
COPY ./requirements.txt /project/requirements.txt
RUN pip install -r /project/requirements.txt
COPY . /project
WORKDIR /project
