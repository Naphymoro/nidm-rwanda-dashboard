FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY pyproject.toml ./
COPY ndim_mcp ./ndim_mcp
RUN pip install --no-cache-dir . && mkdir /audit && chown nobody /audit

# No authentication: reachable only on the compose networks, never publish this port on the host.
EXPOSE 8766
USER nobody
CMD ["python", "-m", "ndim_mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8766"]
