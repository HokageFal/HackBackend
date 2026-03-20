# Тестирование автоматического создания администратора

Write-Host "🧪 Тестирование автоматического создания администратора" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Получаем переменные окружения из .env
$envFile = Get-Content .env
$POSTGRES_USER = ($envFile | Select-String "POSTGRES_USER=(.+)").Matches.Groups[1].Value
$POSTGRES_DB = ($envFile | Select-String "POSTGRES_DB=(.+)").Matches.Groups[1].Value

if (-not $POSTGRES_USER) { $POSTGRES_USER = "postgres" }
if (-not $POSTGRES_DB) { $POSTGRES_DB = "ai_landing_db" }

# Удаляем всех админов из БД
Write-Host ""
Write-Host "🗑️  Удаление существующих администраторов..." -ForegroundColor Yellow
docker-compose exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "DELETE FROM users WHERE role = 'admin';"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Администраторы удалены" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка при удалении администраторов" -ForegroundColor Red
    exit 1
}

# Перезапускаем контейнер FastAPI
Write-Host ""
Write-Host "🔄 Перезапуск контейнера FastAPI..." -ForegroundColor Yellow
docker-compose restart web

Write-Host ""
Write-Host "⏳ Ожидание запуска приложения (10 секунд)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "📋 Логи создания администратора:" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
docker-compose logs web | Select-String -Pattern "НОВЫЙ АДМИНИСТРАТОР" -Context 0,10

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "✅ Тест завершен!" -ForegroundColor Green
Write-Host "Проверьте логи выше для получения данных администратора" -ForegroundColor Yellow
