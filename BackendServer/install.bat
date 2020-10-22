pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata companies
python manage.py createsuperuser
python manage.py shell < seed_stocks.py