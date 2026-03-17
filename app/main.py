from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import os

from app.routers.user_router import router as user_router
from app.routers.otp_router import router as otp_router
from app.routers.google_router import router as google_router
from app.routers.telegram_router import router as telegram_router
from app.routers.github_router import router as github_router
from app.routers.password_reset_router import router as password_reset_router
from app.routers.subscription_router import router as subs_router

# Импорты для админки
from sqladmin import Admin
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.admin.views import UserAdmin, SubscriptionPlanAdmin, UserSubscriptionAdmin, TokenTransactionAdmin
from app.admin.auth import AdminAuth
import logging

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения экземпляра Admin
admin_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")

    try:
        setup_admin(app)
        logger.info("Админ-панель инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации админ-панели: {e}")

    yield

    logger.info("Остановка приложения...")


app = FastAPI(
    title="AI Landing Generator API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    description="API для генерации лендингов с системой аутентификации и OTP верификации",
    lifespan=lifespan
)

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
app.include_router(otp_router, tags=["OTP"])
app.include_router(password_reset_router, tags=["Password Reset"])
app.include_router(google_router, tags=["OAuth"])
app.include_router(telegram_router, tags=["OAuth"])
app.include_router(github_router, tags=["OAuth"])
app.include_router(subs_router, tags=["SubsPlans"])


def setup_admin(app: FastAPI):
    try:
        logger.info("Настройка админ-панели...")

        if settings.DATABASE_URL.startswith("postgresql+asyncpg"):
            admin_engine = create_async_engine(settings.DATABASE_URL, echo=False)
        elif "postgresql" in settings.DATABASE_URL:
            # Если URL содержит psycopg2 или другой синхронный драйвер, заменяем на asyncpg
            admin_engine = create_async_engine(
                settings.DATABASE_URL.replace("psycopg2", "asyncpg"),
                echo=False
            )
        else:
            # Или создаем напрямую с asyncpg
            admin_engine = create_async_engine(
                f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
                echo=False
            )

        logger.info("Движок админ-панели создан")

        authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

        logger.info("Бэкенд аутентификации для админки создан")

        # Инициализируем админку
        admin = Admin(
            app=app,
            engine=admin_engine,
            title="AI Landing Generator Admin",
            base_url="/admin",
            authentication_backend=authentication_backend
        )

        logger.info("Экземпляр админ-панели создан")

        admin.add_view(UserAdmin)
        admin.add_view(SubscriptionPlanAdmin)
        admin.add_view(UserSubscriptionAdmin)
        admin.add_view(TokenTransactionAdmin)

        global admin_instance
        admin_instance = admin

        logger.info("Админ-панель настроена и доступна по пути /admin")

        return admin
    except Exception as e:
        logger.error(f"Ошибка настройки админ-панели: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


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
        "service": "AI Landing Generator API",
        "admin_available": admin_instance is not None
    }


APIDOG_DOCS_URL = "https://app.apidog.com/project/1080151"


@app.get("/docs", include_in_schema=False)
def redirect_to_apidog():
    return RedirectResponse(url=APIDOG_DOCS_URL)


app.mount("/static", StaticFiles(directory="static"), name="static")