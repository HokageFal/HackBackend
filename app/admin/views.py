from sqladmin import ModelView
from app.database.models.users import User


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
