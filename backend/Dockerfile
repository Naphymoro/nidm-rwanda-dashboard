FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NDIM_DEPLOYMENT_MODE=cloud \
    NDIM_MAX_UPLOAD_MB=20 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10

COPY backend/requirements.lock.txt ./requirements.lock.txt
# CPU-only torch first, at the locked version, so the lockfile's torch pin is already met and pip skips the CUDA build.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu "$(grep '^torch==' requirements.lock.txt)" \
 && pip install --no-cache-dir -r requirements.lock.txt

COPY backend/app ./app
COPY docs ./docs
COPY stress_test_corpus ./stress_test_corpus
COPY VERSION ./VERSION
# The sentiment classifier when present at build time (models/README.md); otherwise sentiment stays keyword-based.
COPY models ./models
ENV NDIM_SENTIMENT_MODEL=/app/models/sentiment

EXPOSE 8080

# JSON form (no build warning); the shell is still needed to expand PORT, and exec hands signals to uvicorn.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-8080}\""]
