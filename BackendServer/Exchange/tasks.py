from django.conf import settings
from .celery import app
from .models import *
from decimal import *
from random import *
from datetime import datetime as dt

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


@app.task
def match_sell_buy_offers():
    buy_offers = BuyOffer.objects.all().filter(status=1)
    sell_offers = SellOffer.objects.all().filter(status=1)
    for buy_offer in buy_offers:
        stock = buy_offer.stock
        profile = buy_offer.user.profile
        balance = profile.balance
        if buy_offer.unit_price > stock.price:
            if (stock.avail_amount < buy_offer.stock_amount):
                total_price = stock.avail_amount * stock.price
                if (total_price > balance):
                    amount = int(balance / stock.price)
                else:
                    amount = stock.avail_amount
            else:
                amount = buy_offer.stock_amount
            stock.avail_amount -= amount
            buy_offer.stock_amount -= amount
            if buy_offer.stock_amount == 0:
                buy_offer.status = 3
            buy_offer.save()
            stock.save()
            profile.balance -= amount * stock.price
            profile.save()
            new_transaction = Transaction(
                sell=None,
                buy=buy_offer,
                stock=stock,
                user=None,
                amount=amount,
                unit_price=stock.price,
                date=dt.now,
                is_sell=False,
            )
            new_transaction.save()
    for sell_offer in sell_offers:
        stock = sell_offer.stock
        profile = sell_offer.user.profile
        if sell_offer.unit_price < stock.price:
            stock.avail_amount += sell_offer.stock_amount
            profile.balance += sell_offer.stock_amount * stock.price
            stock.save()
            profile.save()
            sell_offer.status = 3
            sell_offer.save()
            new_transaction = Transaction(
                sell=sell_offer,
                buy=None,
                stock=stock,
                user=None,
                amount=sell_offer.stock_amount,
                unit_price=stock.price,
                date=dt.now,
                is_sell=True,
            )
            new_transaction.save()
