# 2FA App

Учебный проект с регистрацией, входом и двухфакторной аутентификацией.

## Возможности

- Регистрация пользователей с хешированием паролей (bcrypt)
- Вход с проверкой пароля
- Двухфакторная аутентификация (2FA) двумя способами:
  - **TOTP** (Time-based One-Time Password) через генератор кодов
  - **Email** с отправкой кода на почту
- Безопасное хранение конфигурации через переменные окружения

## Требования

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- bcrypt
- pyotp
- qrcode
- python-dotenv

## Установка

1. Клонируй репозиторий:
```bash
git clone https://github.com/Jude51/2FA_app.git
cd 2FA_app
```

2. Установи зависимости:
```bash
python -m pip install -r requirements.txt
```

3. Создай файл `.env` в корне проекта:
```bash
cp .env.example .env
```

## Настройка

Отредактируй файл `.env` и добавь свои значения:

```env
SECRET_KEY=your-secret-key-here
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password
DATABASE_URI=sqlite:///users.db
```

**Важно:**
- `SECRET_KEY` — случайная строка для Flask
- `EMAIL_SENDER` — Gmail адрес для отправки кодов
- `EMAIL_PASSWORD` — пароль приложения Gmail (не главный пароль)

## Запуск

Используй **безопасную версию** приложения:

```bash
python app_safe.py
```

Приложение откроется на `http://127.0.0.1:5000`

## Структура проекта

```
2FA_app/
├── app_safe.py              # Безопасная версия (для GitHub)
├── app.py                   # Локальная версия с секретами (не пушить)
├── requirements.txt         # Зависимости проекта
├── .env                     # Переменные окружения (не пушить)
├── .gitignore              # Правила исключения файлов
├── templates/              # HTML-шаблоны
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── setup_2fa.html
│   └── verify_2fa.html
└── static/
    └── style.css           # CSS стили
```

## Что не хранить в Git

Файлы, которые исключены из репозитория:
- `.env` — переменные окружения и секреты
- `app.py` — локальная оригинальная версия
- `test_app.py` — тесты
- `instance/users.db` — база данных
- `static/qrcode.png` — генерируемые QR-коды
- `__pycache__/` — кеш Python
- `.coverage` — отчёты тестов

## Безопасность

- ✅ Пароли хешируются с помощью bcrypt
- ✅ Секреты хранятся в `.env`, а не в коде
- ✅ Используется HTTPS для SMTP
- ✅ `app_safe.py` проверяет наличие необходимых переменных окружения при запуске
- ⚠️ Для production используй полноценный сервис аутентификации

## Используемые библиотеки

- **Flask** — веб-фреймворк
- **Flask-SQLAlchemy** — ORM для работы с БД
- **bcrypt** — хеширование паролей
- **pyotp** — TOTP аутентификация
- **qrcode** — генерация QR-кодов для TOTP
- **python-dotenv** — загрузка переменных окружения

## Лицензия

MIT

## Автор

Jude51
