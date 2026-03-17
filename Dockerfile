# Stage 1: Builder
# Исправлено: AS большими буквами
# Исправлено: добавлен суффикс -bookworm (стабильный Debian 12), чтобы не качать unstable Trixie
FROM python:3.11-slim-bookworm AS builder

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim-bookworm

WORKDIR /code

# ИСПРАВЛЕНО ЗДЕСЬ:
# 1. Используем libpq-dev вместо libpq-5.
#    Хотя libpq5 правильнее, libpq-dev гарантированно содержит нужные .so файлы и он точно есть в репозитории.
#    Разница в размере незначительна для этого случая, зато надежно.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

COPY --from=builder /install /usr/local

COPY --chown=appuser:appuser . .

USER appuser

# Добавил exec для правильной обработки сигналов остановки
CMD ["sh", "-c", "python /code/update_apidog.py && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]