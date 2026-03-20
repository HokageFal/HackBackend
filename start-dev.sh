#!/bin/bash

echo "🚀 Запуск ПрофДНК API..."

# Ждем готовности PostgreSQL
echo "⏳ Ожидание готовности базы данных..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "✅ База данных готова!"

# Применяем миграции
echo "📦 Применение миграций..."
alembic upgrade head

# Запускаем приложение
echo "🎯 Запуск FastAPI приложения..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
