# Установка MongoDB на Windows

## Скачать и установить:
1. Скачай MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Выбери Windows, MSI installer
3. Запусти установщик, выбери "Complete"
4. Отметь "Install MongoDB as a Service"

## Проверка установки:
```bash
mongod --version
```

## Запуск MongoDB:
MongoDB запустится автоматически как служба Windows.

Проверить статус:
```bash
net start MongoDB
```

## Альтернатива - MongoDB Atlas (облачная):
Если не хочешь устанавливать локально, используй бесплатный MongoDB Atlas:
1. Зарегистрируйся на https://www.mongodb.com/cloud/atlas
2. Создай бесплатный кластер
3. Получи connection string
4. Вставь его в .env как MONGODB_URI

---

# Установка проекта

```bash
cd vulcan_tracker
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открой: http://localhost:8000
