# pull official base image
FROM python:3.9-slim-buster

ARG TARGET
# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql libpq-dev \
  && apt-get clean

# install python dependencies
COPY poetry.lock pyproject.toml ./
RUN pip3 install poetry && poetry config virtualenvs.create false

# add app
RUN if ["$TARGET" = "debug"]; then poetry install; else poetry install --no-dev; fi
ENV TARGET=$TARGET
COPY . .
EXPOSE 8000
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
