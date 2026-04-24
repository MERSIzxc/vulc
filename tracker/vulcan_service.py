from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .models import UserProfile, Grade
from datetime import datetime
import time

class VulcanService:
    @staticmethod
    def get_driver():
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    @staticmethod
    def fetch_grades(email, password):
        driver = None
        try:
            driver = VulcanService.get_driver()

            # Переходим на главную страницу
            print(f"Opening Vulcan login page...")
            driver.get('https://uonetplus.vulcan.net.pl/')
            time.sleep(2)

            print(f"Current URL: {driver.current_url}")
            print(f"Page title: {driver.title}")

            # Сохраняем скриншот для отладки
            try:
                driver.save_screenshot('C:/Users/Компьютер/Desktop/vulcan_debug.png')
                print("Screenshot saved")
            except:
                pass

            # Ищем форму входа с разными вариантами
            wait = WebDriverWait(driver, 10)

            try:
                # Вариант 1: стандартная форма
                email_input = driver.find_element(By.NAME, 'LoginName')
            except:
                try:
                    # Вариант 2: по ID
                    email_input = driver.find_element(By.ID, 'LoginName')
                except:
                    try:
                        # Вариант 3: по типу email
                        email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
                    except:
                        print("ERROR: Cannot find email input field")
                        print("Page source:", driver.page_source[:500])
                        return []

            email_input.send_keys(email)
            print(f"Email entered")

            password_input = driver.find_element(By.NAME, 'Password')
            password_input.send_keys(password)
            print(f"Password entered")

            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            print(f"Login button clicked")

            # Ждем загрузки
            time.sleep(5)

            print(f"After login URL: {driver.current_url}")

            # Проверяем успешность входа
            if 'uonetplus' not in driver.current_url:
                print("ERROR: Login failed - not redirected to uonetplus")
                return []

            # Переходим на страницу оценок
            grades_url = driver.current_url.replace('/Start/Index', '/Uczen/Oceny')
            print(f"Going to grades page: {grades_url}")
            driver.get(grades_url)
            time.sleep(3)

            # Парсим оценки
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            grades = []

            # Ищем таблицы с оценками
            grade_tables = soup.find_all('table', class_='ocenySzczegoly-table')
            print(f"Found {len(grade_tables)} grade tables")

            for table in grade_tables:
                subject = table.find_previous('h2')
                subject_name = subject.text.strip() if subject else 'Неизвестный предмет'

                rows = table.find_all('tr')[1:]  # Пропускаем заголовок
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        grades.append({
                            'subject': subject_name,
                            'value': cols[0].text.strip(),
                            'weight': cols[1].text.strip() or '1',
                            'description': cols[2].text.strip(),
                            'date': cols[3].text.strip(),
                            'teacher': cols[4].text.strip()
                        })

            print(f"Parsed {len(grades)} grades")
            return grades

        except Exception as e:
            print(f"Error fetching grades: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if driver:
                driver.quit()

    @staticmethod
    def sync_user_grades(user):
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"Syncing grades for {user.username}")

            grades = VulcanService.fetch_grades(
                profile.vulcan_email,
                profile.vulcan_password
            )

            print(f"Fetched {len(grades)} grades")

            Grade.objects.filter(user=user).delete()

            for grade_data in grades:
                try:
                    weight = int(grade_data['weight']) if grade_data['weight'].isdigit() else 1
                except:
                    weight = 1

                Grade.objects.create(
                    user=user,
                    subject=grade_data['subject'],
                    value=grade_data['value'],
                    weight=weight,
                    description=grade_data['description'],
                    date=datetime.now(),
                    teacher=grade_data['teacher']
                )
                print(f"Created grade: {grade_data['subject']} - {grade_data['value']}")

            profile.last_sync = datetime.now()
            profile.save()

            return True
        except Exception as e:
            print(f"Error syncing grades: {e}")
            import traceback
            traceback.print_exc()
            return False
