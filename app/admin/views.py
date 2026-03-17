from sqladmin import ModelView
from app.database.models.users import User
from app.database.models.subscription_plans import SubscriptionPlan
from app.database.models.user_subscriptions import UserSubscription
from app.database.models.token_ledger import TokenTransaction


class UserAdmin(ModelView, model=User):
    """Админ-панель для управления пользователями"""
    
    # Основные настройки
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    
    # Колонки для отображения в списке
    column_list = [
        "id",
        "username",
        "email",
        "auth_provider",
        "token_balance",
        "is_admin",
        "email_verified",
        "created_at"
    ]
    
    # Колонки с возможностью поиска
    column_searchable_list = ["username", "email"]
    
    # Сортировка по умолчанию (новые сверху)
    column_default_sort = [("created_at", True)]
    
    # Колонки для детального просмотра
    column_details_list = [
        "id",
        "username",
        "email",
        "password",
        "avatar_url",
        "auth_provider",
        "google_id",
        "telegram_id",
        "github_id",
        "token_balance",
        "is_admin",
        "email_verified",
        "created_at"
    ]
    
    # Поля для создания/редактирования
    form_columns = [
        "username",
        "email",
        "password",
        "avatar_url",
        "auth_provider",
        "google_id",
        "telegram_id",
        "github_id",
        "token_balance",
        "is_admin",
        "email_verified"
    ]
    
    # Лейблы для полей на русском
    column_labels = {
        "id": "ID",
        "username": "Имя пользователя",
        "email": "Email",
        "password": "Пароль (хеш)",
        "avatar_url": "Аватар",
        "auth_provider": "Провайдер",
        "google_id": "Google ID",
        "telegram_id": "Telegram ID",
        "github_id": "GitHub ID",
        "token_balance": "Баланс токенов",
        "is_admin": "Администратор",
        "email_verified": "Email подтвержден",
        "created_at": "Дата создания"
    }
    
    # Форматирование колонок
    column_formatters = {
        "password": lambda m, a: "••••••••" if m.password else None,
        "avatar_url": lambda m, a: m.avatar_url[:50] + "..." if m.avatar_url and len(m.avatar_url) > 50 else m.avatar_url
    }
    
    # Настройки пагинации
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    
    # Разрешения
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True



class SubscriptionPlanAdmin(ModelView, model=SubscriptionPlan):
    """Админ-панель для управления тарифными планами"""
    
    name = "Тарифный план"
    name_plural = "Тарифные планы"
    icon = "fa-solid fa-credit-card"
    
    column_list = [
        "id",
        "name",
        "price_cents",
        "duration_days",
        "tokens_per_period",
        "is_active"
    ]
    
    column_searchable_list = ["name"]
    column_default_sort = [("duration_days", False), ("price_cents", False)]
    
    column_details_list = [
        "id",
        "name",
        "description",
        "price_cents",
        "duration_days",
        "tokens_per_period",
        "feature_labels",
        "is_active"
    ]
    
    form_columns = [
        "name",
        "description",
        "price_cents",
        "duration_days",
        "tokens_per_period",
        "feature_labels",
        "is_active"
    ]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "description": "Описание",
        "price_cents": "Цена (центы)",
        "duration_days": "Длительность (дни)",
        "tokens_per_period": "Токенов за период",
        "feature_labels": "Список возможностей (JSON)",
        "is_active": "Активен"
    }
    
    # Форматирование колонок
    column_formatters = {
        "price_cents": lambda m, a: f"{m.price_cents / 100:.2f} ₽" if m.price_cents else "0.00 ₽",
        "feature_labels": lambda m, a: ", ".join(m.feature_labels) if m.feature_labels else "Нет"
    }
    
    # Подсказки для полей формы
    form_args = {
        "name": {
            "description": "Уникальное название тарифа, например: 'Basic Monthly'"
        },
        "description": {
            "description": "Подробное описание тарифного плана"
        },
        "price_cents": {
            "description": "Цена в центах (копейках). Например: 99900 = 999 рублей"
        },
        "duration_days": {
            "description": "Длительность подписки в днях. 30 = месяц, 365 = год"
        },
        "tokens_per_period": {
            "description": "Количество токенов, которые получит пользователь"
        },
        "feature_labels": {
            "description": 'Список возможностей в формате JSON массива. Пример: ["10,000 токенов", "Email поддержка", "API доступ"]'
        },
        "is_active": {
            "description": "Отображать ли этот тариф пользователям"
        }
    }
    
    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class UserSubscriptionAdmin(ModelView, model=UserSubscription):
    name = "Подписка"
    name_plural = "Подписки пользователей"
    icon = "fa-solid fa-calendar-check"
    
    column_list = [
        "id",
        "user_id",
        "plan_id",
        "started_at",
        "expires_at",
        "is_active",
        "auto_renew"
    ]
    
    column_default_sort = [("started_at", True)]
    
    column_details_list = [
        "id",
        "user_id",
        "plan_id",
        "started_at",
        "expires_at",
        "is_active",
        "auto_renew"
    ]
    
    form_columns = [
        "user_id",
        "plan_id",
        "started_at",
        "expires_at",
        "is_active",
        "auto_renew"
    ]
    
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "plan_id": "ID тарифа",
        "started_at": "Начало",
        "expires_at": "Окончание",
        "is_active": "Активна",
        "auto_renew": "Автопродление"
    }
    
    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class TokenTransactionAdmin(ModelView, model=TokenTransaction):
    """Админ-панель для управления транзакциями токенов
    
    Типы транзакций:
    - subscription: начисление токенов по подписке
    - purchase: покупка токенов
    - usage: списание токенов за использование
    - refund: возврат токенов (отмена операции)
    - admin_adjustment: ручная корректировка администратором
    
    amount: количество токенов (+1000 начисление, -20 списание)
    """
    
    name = "Транзакция"
    name_plural = "Транзакции токенов"
    icon = "fa-solid fa-coins"
    
    column_list = [
        "id",
        "user_id",
        "amount",
        "type",
        "description",
        "created_at"
    ]
    
    column_default_sort = [("created_at", True)]
    
    column_details_list = [
        "id",
        "user_id",
        "amount",
        "type",
        "description",
        "created_at"
    ]
    
    form_columns = [
        "user_id",
        "amount",
        "type",
        "description"
    ]
    
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "amount": "Количество токенов (+начисление / -списание)",
        "type": "Тип транзакции",
        "description": "Описание",
        "created_at": "Дата создания"
    }
    
    # Подсказки для полей
    form_args = {
        "amount": {
            "description": "Положительное число для начисления, отрицательное для списания. Например: 1000 или -50"
        },
        "type": {
            "description": "subscription=подписка, purchase=покупка, usage=использование, refund=возврат, admin_adjustment=корректировка"
        },
        "description": {
            "description": "Причина транзакции, например: 'Возврат за отмененную генерацию'"
        }
    }
    
    page_size = 100
    can_create = True
    can_edit = False
    can_delete = True
    can_view_details = True
