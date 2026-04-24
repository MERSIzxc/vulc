from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib.auth.models import User
from tracker.models import UserProfile
from tracker.vulcan_service import VulcanService

scheduler = BackgroundScheduler()

def sync_all_users():
    users = User.objects.all()
    for user in users:
        try:
            VulcanService.sync_user_grades(user)
            print(f"Synced grades for {user.username}")
        except Exception as e:
            print(f"Error syncing {user.username}: {e}")

def start():
    if not scheduler.running:
        scheduler.add_job(sync_all_users, 'interval', hours=1, id='sync_all_grades')
        scheduler.start()
        print("Scheduler started!")
