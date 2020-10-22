from django.conf import settings
from .celery import app
from .models import *
from decimal import *
from random import *

MAX_STOCKS = 1000


def logical_xor(a, b):
    if bool(a) == bool(b):
        return False
    else:
        return a or b


@app.task
def recalculate_prices():
    stocks = Stock.objects.all()
    for stock in stocks:
        last_transaction: Transaction = Transaction.objects.filter(stock=stock).last()
        if logical_xor(last_transaction.sell, last_transaction.is_sell):
            stock.price -= last_transaction.amount * Decimal('0.2')
            stock.save()
        else:
            stock.price += last_transaction.amount * Decimal('0.2')
            stock.save()


@app.task
def recalculate_prices_interval():
    stocks = Stock.objects.all()
    for stock in stocks:
        last_transaction: Transaction = Transaction.objects.filter(stock=stock).last()
        stock.price -= last_transaction.amount * Decimal('0.1')
        stock.save()


@app.task
def regenerate_stocks():
    seed()
    stocks = Stock.objects.all()
    for stock in stocks:
        new_items_count = stock.avail_amount + randrange(MAX_STOCKS - stock.avail_amount)
        stock.avail_amount = new_items_count
        stock.save()
