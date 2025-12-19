FROM python:3.13-slim

ENV PATH="/etc/poetry/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/gateway-service/src"

WORKDIR /gateway-service

RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/

RUN python3 -m pip install --upgrade pip \
    && pip install poetry==2.2.1
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock* /gateway-service/
RUN poetry install --no-interaction --no-root

COPY . /gateway-service
