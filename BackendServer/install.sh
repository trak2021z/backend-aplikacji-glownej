pip install -r requirements.txt
python manage.py makemigrations BackendServer
python manage.py migrate
python manage.py createsuperuser