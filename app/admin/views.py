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
        "full_name",
        "email",
        "phone",
        "role",
        "is_admin",
        "is_blocked",
        "access_until",
        "created_at"
    ]
    
    # Колонки с возможностью поиска
    column_searchable_list = ["full_name", "email", "phone"]
    
    # Сортировка по умолчанию (новые сверху)
    column_default_sort = [("created_at", True)]
    
    # Колонки для детального просмотра
    column_details_list = [
        "id",
        "full_name",
        "email",
        "phone",
        "password",
        "photo_url",
        "about_markdown",
        "public_card_token",
        "role",
        "is_admin",
        "is_blocked",
        "access_until",
        "created_at"
    ]
    
    # Поля для создания/редактирования
    form_columns = [
        "full_name",
        "email",
        "phone",
        "password",
        "photo_url",
        "about_markdown",
        "role",
        "is_admin",
        "is_blocked",
        "access_until"
    ]
    
    # Лейблы для полей на русском
    column_labels = {
        "id": "ID",
        "full_name": "ФИО",
        "email": "Email",
        "phone": "Телефон",
        "password": "Пароль (хеш)",
        "photo_url": "Фото",
        "about_markdown": "О себе",
        "public_card_token": "Токен визитки",
        "role": "Роль",
        "is_admin": "Администратор",
        "is_blocked": "Заблокирован",
        "access_until": "Доступ до",
        "created_at": "Дата создания"
    }
    
    # Форматирование колонок
    column_formatters = {
        "password": lambda m, a: "••••••••" if m.password else None,
        "photo_url": lambda m, a: m.photo_url[:50] + "..." if m.photo_url and len(m.photo_url) > 50 else m.photo_url,
        "about_markdown": lambda m, a: m.about_markdown[:50] + "..." if m.about_markdown and len(m.about_markdown) > 50 else m.about_markdown
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
