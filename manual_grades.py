"""
Вручную добавленные оценки для польского языка и географии
Эти оценки не парсятся расширением, поэтому добавляются вручную

Запуск: python manage.py shell < manual_grades.py
"""

from tracker.models import Grade, User
from django.utils import timezone
from datetime import datetime

user, _ = User.objects.get_or_create(username='default_user')

# Польский язык - оценки которые расширение не находит
polish_grades = [
    {'value': '4.75/18', 'date': '04.12.2025'},
    {'value': '4/12', 'date': '04.12.2025'},
    {'value': '8/17', 'date': '28.11.2025'},
]

# География - оценки которые расширение не находит
geo_grades = [
    {'value': '11.5/15', 'date': '15.12.2025'},
    {'value': '14/30', 'date': '24.11.2025'},
    {'value': '8.5/12', 'date': '05.11.2025'},
    {'value': '9/15', 'date': '22.10.2025'},
]

added_count = 0

for g in polish_grades:
    grade_date = datetime.strptime(g['date'], '%d.%m.%Y')
    grade_date = timezone.make_aware(grade_date)

    # Проверяем что такой оценки еще нет
    existing = Grade.objects.filter(
        user=user,
        subject='Język polski',
        value=g['value'],
        date=grade_date
    ).first()

    if not existing:
        Grade.objects.create(
            user=user,
            subject='Język polski',
            value=g['value'],
            weight=1,
            date=grade_date,
            description='',
            teacher=''
        )
        added_count += 1
        print(f"Added Polish: {g['value']}")

for g in geo_grades:
    grade_date = datetime.strptime(g['date'], '%d.%m.%Y')
    grade_date = timezone.make_aware(grade_date)

    # Проверяем что такой оценки еще нет
    existing = Grade.objects.filter(
        user=user,
        subject='Geografia',
        value=g['value'],
        date=grade_date
    ).first()

    if not existing:
        Grade.objects.create(
            user=user,
            subject='Geografia',
            value=g['value'],
            weight=1,
            date=grade_date,
            description='',
            teacher=''
        )
        added_count += 1
        print(f"Added Geography: {g['value']}")

print(f'\nTotal added: {added_count} grades')
print('Done!')
