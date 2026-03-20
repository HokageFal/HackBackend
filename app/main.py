from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
import os

from app.routers.user_router import router as user_router
from app.routers.psychologist_router import router as psychologist_router
from app.init_admin import init_admin
import logging

logger = logging.getLogger(__name__)


app = FastAPI(
    title="ПрофДНК API",
    version="1.0.0",
    description="API для платформы психологических тестов ПрофДНК",
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)


@app.on_event("startup")
def startup_event():
    """Выполняется при запуске приложения."""
    logger.info("Запуск приложения...")
    try:
        init_admin()
    except Exception as e:
        logger.error(f"Ошибка инициализации админа: {e}", exc_info=True)


@app.on_event("shutdown")
def shutdown_event():
    """Выполняется при остановке приложения."""
    logger.info("Остановка приложения...")


# Добавляем схему безопасности для JWT
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ПрофДНК API",
        version="1.0.0",
        description="API для платформы психологических тестов ПрофДНК",
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите JWT токен (без префикса 'Bearer')"
        }
    }
    
    # Применяем security ко всем эндпоинтам кроме login и health
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if path not in ["/users/login", "/health"] and method != "parameters":
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS должен быть первым
origins = [
    "https://landify-ai.ru",
    "https://dev.landify-ai.ru",
    "http://193.168.46.155/api",
    "http://193.168.46.155:3000",
    "http://193.168.46.155:8000",
    "http://193.168.46.155:3001",
    "http://193.168.46.155:8001",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:3001",
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware после CORS
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY"),
    session_cookie="session",
    max_age=3600,  # 1 час
    same_site="lax",  # Lax для OAuth redirects
    https_only=os.environ.get("ENVIRONMENT") == "production"
)

# API routes
app.include_router(user_router, tags=["Users"])
app.include_router(psychologist_router, tags=["Admin - Psychologists"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    translated_errors = []

    for err in exc.errors():
        msg = err.get("msg", "")
        ctx = err.get("ctx", {}) or {}

        msg_ru = msg
        if "String should have at least" in msg:
            msg_ru = "Строка должна содержать минимум {min_length} символов".format(**err.get("ctx", {}))
        elif "String should have at most" in msg:
            msg_ru = "Строка должна содержать максимум {max_length} символов".format(**err.get("ctx", {}))
        elif "value is not a valid email address" in msg:
            msg_ru = "Некорректный формат email"
        elif "Field required" in msg:
            msg_ru = "Поле обязательно для заполнения"

        safe_ctx = {k: str(v) for k, v in ctx.items()}

        translated_errors.append({
            "type": err.get("type"),
            "loc": err.get("loc"),
            "msg": msg_ru,
            "input": err.get("input"),
            "ctx": safe_ctx
        })

    return JSONResponse(
        status_code=422,
        content={"detail": translated_errors},
    )


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "ПрофДНК API"
    }


app.mount("/static", StaticFiles(directory="static"), name="static")
