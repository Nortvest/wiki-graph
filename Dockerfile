FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync  \
  --no-install-project \
  --frozen \
  --compile-bytecode

COPY main.py /app
COPY app /app/app
