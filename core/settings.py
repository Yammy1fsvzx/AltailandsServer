from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', "django-insecure-%p^+6)6sa+g8bw_gwq=jmm7n5c%$j8fgw&aa#455dw31qa8uhf")
DEBUG = True

ALLOWED_HOSTS = ['altailands.ru', 'www.altailands.ru', '89.111.169.36', 'localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    # Unfold admin theme must be before django.contrib.admin
    "unfold",
    "unfold.contrib.filters", # Optional, if you want unfold filters
    "unfold.contrib.forms",   # Optional, if you want unfold forms
    # ... other unfold contrib apps if needed ...
    # Standard Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "corsheaders",
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    # Local apps
    "contacts",
    "authentication",
    "news",
    "catalog",
    "quizzes",
    "requests_app",
    "analytics_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware", # CORS Middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Директория, куда будет выполняться сбор статики командой collectstatic
STATIC_ROOT = BASE_DIR / 'static_root'

# Дополнительные директории со статикой (если есть)
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Папка media в корне проекта

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF Spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Altailands API',
    'DESCRIPTION': 'API для сайта недвижимости Altailands',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://altailands.ru",
    "https://www.altailands.ru",
    "http://frontend",
    "https://frontend",
]
CORS_ALLOW_CREDENTIALS = True # Разрешаем передачу cookies (если понадобятся для других целей)

# Simple JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60), # Время жизни Access токена (например, 1 час)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),    # Время жизни Refresh токена (например, 7 дней)
    "ROTATE_REFRESH_TOKENS": True, # Обновлять refresh токен при каждом запросе /api/token/refresh/
    "BLACKLIST_AFTER_ROTATION": True, # Добавлять старый refresh токен в черный список после обновления
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY, # Используем SECRET_KEY из Django
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# Unfold Theme Settings
UNFOLD = {
    "SITE_TITLE": "Altailands Admin",
    "SITE_HEADER": "Altailands Admin Panel",
    # "SITE_URL": "/", # URL для кнопки "View site"
    # "SITE_ICON": lambda request: "static/favicon.ico", # Путь к фавиконке
    "COLORS": {
        "primary": {
            "50": "#ecfdf5",
            "100": "#d1fae5",
            "200": "#a7f3d0",
            "300": "#6ee7b7",
            "400": "#34d399",
            "500": "#10b981", # Основной зеленый (Emerald 500)
            "600": "#059669",
            "700": "#047857",
            "800": "#065f46",
            "900": "#064e3b",
            "950": "#022c22",
        }
    },
    "SIDEBAR": {
        "show_search": True, # Поиск по меню
        "show_all_applications": False, # Скрыть автоматический список приложений
        "navigation": [
            {
                "title": "Аналитика", # Пример отдельного пункта
                "icon": "heroicons-outline-chart-bar",
                "items": [
                    # Ссылки на страницы аналитики, если они есть в админке
                ]
            },
            {
                "title": "Каталог: Участки",
                "icon": "heroicons-outline-map",
                "items": [
                    {"title": "Земельные участки", "link": "/admin/catalog/landplot/"},
                    {"title": "Категории земель", "link": "/admin/catalog/landcategory/"},
                    {"title": "Виды разреш. исп.", "link": "/admin/catalog/landusetype/"},
                ]
            },
            {
                "title": "Каталог: Другие объекты",
                "icon": "heroicons-outline-building-office-2",
                "items": [
                    {"title": "Объекты", "link": "/admin/catalog/genericproperty/"},
                    {"title": "Типы объектов", "link": "/admin/catalog/propertytype/"},
                ]
            },
            {
                "title": "Каталог: Справочники",
                "icon": "heroicons-outline-book-open",
                "items": [
                    {"title": "Местоположения", "link": "/admin/catalog/location/"},
                    {"title": "Характеристики", "link": "/admin/catalog/feature/"},
                    # MediaFile обычно не нужно выносить сюда
                ]
            },
            {
                "title": "Контент",
                "icon": "heroicons-outline-newspaper",
                "items": [
                    {"title": "Новости", "link": "/admin/news/newsarticle/"},
                    {"title": "Категории новостей", "link": "/admin/news/category/"},
                ]
            },
             {
                "title": "Обратная связь",
                "icon": "heroicons-outline-inbox-arrow-down",
                "items": [
                    {"title": "Заявки", "link": "/admin/requests_app/request/"},
                    {"title": "Обращения (контакты)", "link": "/admin/contacts/contactsubmission/"},
                    {"title": "Контакты компании", "link": "/admin/contacts/contact/"},
                ]
            },
            {
                "title": "Квизы",
                "icon": "heroicons-outline-question-mark-circle",
                "items": [
                    {"title": "Квизы", "link": "/admin/quizzes/quiz/"},
                    {"title": "Вопросы", "link": "/admin/quizzes/question/"},
                    {"title": "Ответы", "link": "/admin/quizzes/answer/"},
                ]
            },
            {
                "title": "Управление доступом",
                "icon": "heroicons-outline-users",
                "items": [
                    {"title": "Пользователи", "link": "/admin/auth/user/"},
                    {"title": "Группы", "link": "/admin/auth/group/"},
                ]
            },
        ]
    }
}
