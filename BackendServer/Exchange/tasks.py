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

def seed_stocks():
    seed()
    companies = Company.objects.all()
    for company in companies:
        price = randrange(5, 250)
        count = randrange(500, 1000)
        new_stock = Stock(company=company,
                          name=company.name + " - generated automatically",
                          price=price,
                          avail_amount=count)
        new_stock.save()
