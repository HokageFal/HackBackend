#!/bin/bash

# Скрипт для создания администратора через Docker

echo "🚀 Создание администратора ПрофДНК..."
docker-compose exec web python create_admin.py
