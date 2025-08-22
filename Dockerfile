# Imagem base enxuta
FROM python:3.13-slim AS app

# Ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/opt/poetry/bin:/app/.venv/bin:$PATH"

# Instala o Poetry (sem toolchain pesada; usamos psycopg2-binary)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && curl -sSL https://install.python-poetry.org | python3 - \
 && poetry --version \
 && apt-get purge -y --auto-remove curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia só os manifestos (cache amigo)
COPY pyproject.toml poetry.lock ./

# Sincroniza o lock (se mudou) e instala deps de runtime
RUN poetry lock --no-update \
 && poetry install --only main --no-root --no-ansi

# Agora copia o código
COPY . .

EXPOSE 8000

# Python já vem do venv (/app/.venv/bin está no PATH)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
