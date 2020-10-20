pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
sqlite3 db.sqlite3 < companies.txt