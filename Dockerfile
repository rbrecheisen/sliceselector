FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src/sliceselector /app/src/
COPY pyproject.toml /app/
COPY README.md /app/
#RUN pip install --no-cache-dir mosamatic-sliceselector
RUN pip install -e /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]