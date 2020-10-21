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
    companies = Company.objects.all()
    for company in companies:
        all_company_stocks = stocks.filter(company=company)
        company_stocks_count = len(all_company_stocks)
        company_stocks_prices = list(map(lambda x: x.price, all_company_stocks))
        new_items_count = randrange(MAX_STOCKS - company_stocks_count)
        if len(company_stocks_prices) == 0:
            avg_price = randrange(5, 250)
        else:
            avg_price = sum(company_stocks_prices) / len(company_stocks_prices)
        new_price = randrange(8, 12) * avg_price / Decimal(10.0)
        new_stock = Stock(company=company,
                          name=company.name + " - generated automatically",
                          price=new_price,
                          avail_amount=new_items_count)
        new_stock.save()
