from django.conf import settings
from celery import task
from .models import *


@task
def recalculate_prices():
    stocks = Stock.objects.all()
    for stock in stocks:
        last_transaction = Transaction.objects.filter(stock=stock).last()
        stock.price = last_transaction.price
        stock.save()
