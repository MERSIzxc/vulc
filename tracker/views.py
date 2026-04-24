from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserProfile, Grade
import json

def index(request):
    return redirect('dashboard')

def dashboard(request):
    # Получаем или создаем единственного пользователя
    user, created = User.objects.get_or_create(username='default_user')
    if created:
        UserProfile.objects.create(user=user, vulcan_email='', vulcan_password='')

    # Автоматически добавляем вручную введенные оценки если их нет
    from datetime import datetime
    manual_grades = [
        {'subject': 'Język polski', 'value': '4.75/18', 'date': '04.12.2025'},
        {'subject': 'Język polski', 'value': '4/12', 'date': '04.12.2025'},
        {'subject': 'Język polski', 'value': '8/17', 'date': '28.11.2025'},
        {'subject': 'Geografia', 'value': '11.5/15', 'date': '15.12.2025'},
        {'subject': 'Geografia', 'value': '14/30', 'date': '24.11.2025'},
        {'subject': 'Geografia', 'value': '8.5/12', 'date': '05.11.2025'},
        {'subject': 'Geografia', 'value': '9/15', 'date': '22.10.2025'},
    ]

    for g in manual_grades:
        grade_date = datetime.strptime(g['date'], '%d.%m.%Y')
        grade_date = timezone.make_aware(grade_date)

        if not Grade.objects.filter(user=user, subject=g['subject'], value=g['value'], date=grade_date).exists():
            Grade.objects.create(
                user=user,
                subject=g['subject'],
                value=g['value'],
                weight=1,
                date=grade_date,
                description='',
                teacher=''
            )

    grades = Grade.objects.filter(user=user).order_by('subject', '-date')

    subjects = {}
    for grade in grades:
        if grade.subject not in subjects:
            subjects[grade.subject] = {
                'grades': [],
                'average': 0
            }
        subjects[grade.subject]['grades'].append(grade)

    # Вычисляем средний балл для каждого предмета (суммарный метод)
    for subject_name, subject_data in subjects.items():
        total_received = 0
        total_maximum = 0
        for grade in subject_data['grades']:
            try:
                # Пропускаем оценки с весом 0 (не влияют на итоговую оценку)
                if grade.weight == 0:
                    continue

                # Парсим оценку (например "5/6" -> 5 и 6)
                parts = grade.value.split('/')
                if len(parts) == 2:
                    received = float(parts[0])
                    maximum = float(parts[1])
                    if maximum > 0:
                        total_received += received
                        total_maximum += maximum
            except:
                pass

        if total_maximum > 0:
            subject_data['average'] = round((total_received / total_maximum) * 100, 1)
            subject_data['total_received'] = total_received
            subject_data['total_maximum'] = total_maximum

    # Сортируем предметы по проценту для диаграммы (от большего к меньшему)
    subjects_sorted = sorted(subjects.items(), key=lambda x: x[1]['average'], reverse=True)

    # Вычисляем средний процент по всем предметам и общую сумму баллов
    if subjects:
        total_avg = sum(s[1]['average'] for s in subjects.items()) / len(subjects)
        overall_average = round(total_avg, 1)

        # Суммируем все баллы
        overall_received = sum(s[1].get('total_received', 0) for s in subjects.items())
        overall_maximum = sum(s[1].get('total_maximum', 0) for s in subjects.items())

        # Строим график исторической средней оценки
        # Группируем оценки по месяцам и считаем средний процент на каждую дату
        from collections import defaultdict
        from datetime import datetime

        all_grades = Grade.objects.filter(user=user).order_by('date')

        # Группируем оценки по датам и считаем кумулятивный средний
        from collections import defaultdict
        grades_by_date = defaultdict(list)

        total_received_cumulative = 0
        total_maximum_cumulative = 0

        for grade in all_grades:
            if grade.weight == 0:
                continue

            try:
                parts = grade.value.split('/')
                if len(parts) == 2:
                    received = float(parts[0])
                    maximum = float(parts[1])
                    if maximum > 0:
                        total_received_cumulative += received
                        total_maximum_cumulative += maximum

                        date_str = grade.date.strftime('%d.%m.%Y')
                        grades_by_date[date_str].append({
                            'subject': grade.subject,
                            'value': grade.value,
                            'description': grade.description,
                            'cumulative_received': total_received_cumulative,
                            'cumulative_maximum': total_maximum_cumulative
                        })
            except:
                pass

        # Создаем точки графика - одна точка на дату
        cumulative_data = []
        # Ширина графика в пикселях (примерно, будет масштабироваться)
        graph_width = 900

        for i, date_str in enumerate(sorted(grades_by_date.keys(), key=lambda d: tuple(map(int, d.split('.')[::-1])))):
            # Берем последнее кумулятивное значение для этой даты
            last_grade = grades_by_date[date_str][-1]
            avg = round((last_grade['cumulative_received'] / last_grade['cumulative_maximum']) * 100, 1)
            # Y координата: 100% -> y=50, 0% -> y=350
            y_coord = round(50 + (100 - avg) * 300 / 100, 1)

            cumulative_data.append({
                'date': date_str,
                'average': avg,
                'y': y_coord,
                'index': i,
                'grades': [{'subject': g['subject'], 'value': g['value'], 'description': g['description']}
                          for g in grades_by_date[date_str]]
            })

        # Вычисляем X координаты в пикселях
        total_points = len(cumulative_data)
        if total_points > 1:
            for i, point in enumerate(cumulative_data):
                point['x'] = round(50 + i * graph_width / (total_points - 1), 1)
        elif total_points == 1:
            cumulative_data[0]['x'] = 500

        # Находим границы месяцев для вертикальных линий
        from datetime import datetime
        month_boundaries = []
        prev_month = None

        # Русские названия месяцев
        month_names_ru = {
            1: 'Янв', 2: 'Фев', 3: 'Мар', 4: 'Апр', 5: 'Май', 6: 'Июн',
            7: 'Июл', 8: 'Авг', 9: 'Сен', 10: 'Окт', 11: 'Ноя', 12: 'Дек'
        }

        for i, point in enumerate(cumulative_data):
            date_obj = datetime.strptime(point['date'], '%d.%m.%Y')
            current_month = (date_obj.year, date_obj.month)

            if prev_month and current_month != prev_month:
                # Граница месяца
                month_label = f"{month_names_ru[date_obj.month]} {date_obj.year}"
                month_boundaries.append({
                    'x': point['x'],
                    'label': month_label
                })

            prev_month = current_month

        history_data = cumulative_data
        month_lines = month_boundaries

        # Строим графики по предметам
        subject_history = {}
        for subject_name in subjects.keys():
            subject_grades = Grade.objects.filter(user=user, subject=subject_name).exclude(weight=0).order_by('date')

            subject_data = []
            total_r = 0
            total_m = 0

            for grade in subject_grades:
                try:
                    parts = grade.value.split('/')
                    if len(parts) == 2:
                        received = float(parts[0])
                        maximum = float(parts[1])
                        if maximum > 0:
                            total_r += received
                            total_m += maximum

                            if total_m > 0:
                                avg = round((total_r / total_m) * 100, 1)
                                y_coord = round(50 + (100 - avg) * 300 / 100, 1)
                                date_str = grade.date.strftime('%d.%m.%Y')

                                # Находим X координату по дате из общего графика
                                x_coord = 50
                                for hist_point in cumulative_data:
                                    if hist_point['date'] == date_str:
                                        x_coord = hist_point['x']
                                        break

                                # Добавляем точку только если нашли соответствующую дату
                                if x_coord != 50 or date_str == cumulative_data[0]['date']:
                                    subject_data.append({
                                        'x': x_coord,
                                        'y': y_coord,
                                        'average': avg,
                                        'date': date_str
                                    })
                except:
                    pass

            if subject_data:
                subject_history[subject_name] = subject_data

        # Назначаем цвета предметам
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7', '#a29bfe',
                  '#fd79a8', '#fdcb6e', '#00b894', '#e17055', '#74b9ff', '#55efc4']
        subject_lines = []
        for i, (subject_name, data) in enumerate(subject_history.items()):
            subject_lines.append({
                'subject': subject_name,
                'data': data,
                'color': colors[i % len(colors)]
            })

        # Сортируем по Y координате последней точки для правильного размещения подписей
        subject_lines.sort(key=lambda x: x['data'][-1]['y'] if x['data'] else 0)

        # Корректируем позиции подписей чтобы они не накладывались
        min_spacing = 15  # Минимальное расстояние между подписями
        for i in range(len(subject_lines)):
            if i > 0:
                prev_y = subject_lines[i-1]['data'][-1]['y']
                curr_y = subject_lines[i]['data'][-1]['y']
                if abs(curr_y - prev_y) < min_spacing:
                    # Сдвигаем текущую подпись вниз
                    subject_lines[i]['label_y'] = prev_y + min_spacing
                else:
                    subject_lines[i]['label_y'] = curr_y
            else:
                subject_lines[i]['label_y'] = subject_lines[i]['data'][-1]['y']

    else:
        overall_average = 0
        overall_received = 0
        overall_maximum = 0
        history_data = []
        month_lines = []
        subject_lines = []

    try:
        profile = UserProfile.objects.get(user=user)
    except:
        profile = UserProfile.objects.create(user=user, vulcan_email='', vulcan_password='')

    # Генерируем API ключ если его нет
    if not hasattr(profile, 'api_key') or not profile.api_key:
        import secrets
        profile.api_key = secrets.token_urlsafe(32)
        profile.save()

    return render(request, 'tracker/dashboard.html', {
        'subjects': subjects,
        'subjects_sorted': subjects_sorted,
        'overall_average': overall_average,
        'overall_received': overall_received,
        'overall_maximum': overall_maximum,
        'history_data': history_data,
        'month_lines': month_lines,
        'subject_lines': subject_lines,
        'last_sync': profile.last_sync,
        'api_key': getattr(profile, 'api_key', '')
    })

@csrf_exempt
def import_grades(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

    try:
        api_key = request.headers.get('X-API-Key')
        print(f"Received API key: {api_key}")

        if not api_key:
            return JsonResponse({'success': False, 'error': 'API key required'}, status=401)

        # Всегда используем default_user
        user, created = User.objects.get_or_create(username='default_user')
        print(f"Using user: {user.username}")

        # Получаем или создаем профиль
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user, vulcan_email='', vulcan_password='')

        data = json.loads(request.body)
        grades_data = data.get('grades', [])
        print(f"Received {len(grades_data)} grades")

        if not grades_data:
            return JsonResponse({'success': False, 'error': 'No grades provided'})

        # Сохраняем новые оценки, избегая дублей
        saved_count = 0
        skipped_count = 0
        for grade_data in grades_data:
            try:
                weight = int(grade_data.get('weight', '1'))
            except:
                weight = 1

            # Парсим дату если есть
            grade_date = None
            date_str = grade_data.get('date', '').strip()
            if date_str:
                try:
                    # Формат: DD.MM.YYYY
                    from datetime import datetime
                    grade_date = datetime.strptime(date_str, '%d.%m.%Y')
                    grade_date = timezone.make_aware(grade_date)
                except:
                    grade_date = timezone.now()
            else:
                grade_date = timezone.now()

            # Проверяем, существует ли уже такая оценка (избегаем дублей)
            existing = Grade.objects.filter(
                user=user,
                subject=grade_data.get('subject', 'Неизвестный предмет'),
                value=grade_data.get('value', ''),
                date=grade_date
            ).first()

            if existing:
                skipped_count += 1
                continue

            grade = Grade.objects.create(
                user=user,
                subject=grade_data.get('subject', 'Неизвестный предмет'),
                value=grade_data.get('value', ''),
                weight=weight,
                description=grade_data.get('description', ''),
                date=grade_date,
                teacher=grade_data.get('teacher', '')
            )
            saved_count += 1

        profile.last_sync = timezone.now()
        profile.save()

        print(f"Total saved: {saved_count} grades, skipped: {skipped_count} duplicates")

        return JsonResponse({
            'success': True,
            'count': saved_count,
            'skipped': skipped_count,
            'message': f'Saved {saved_count} new grades, skipped {skipped_count} duplicates'
        })

    except Exception as e:
        print(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
