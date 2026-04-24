# Vulcan Tracker - Django

Веб-приложение для отслеживания оценок из польского электронного дневника eduVULCAN.

## Установка MongoDB

### Вариант 1: Локальная установка
1. Скачай MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Выбери Windows, MSI installer
3. Запусти установщик, выбери "Complete"
4. Отметь "Install MongoDB as a Service"

Проверка:
```bash
mongod --version
net start MongoDB
```

### Вариант 2: MongoDB Atlas (облачная, бесплатная)
1. Зарегистрируйся на https://www.mongodb.com/cloud/atlas
2. Создай бесплатный кластер
3. Получи connection string
4. Вставь его в .env как MONGODB_URI

## Установка проекта

```bash
cd vulcan_tracker
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открой: http://localhost:8000

## Функции

- Автоматическая синхронизация оценок каждый час
- Безопасное хранение данных в MongoDB
- Ручное обновление по кнопке
- Отображение оценок по предметам
- Админ-панель Django

## Требования

- Python 3.8+
- MongoDB
- Аккаунт eduVULCAN
