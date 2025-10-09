from django.contrib.auth import get_user_model

def run():
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("ram", "ram@gmail.com", "123")
        print("Superuser created")
    else:
        print("Superuser already exists")
