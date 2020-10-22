from Exchange.models import *
from random import *
seed()
companies = Company.objects.all()
stocks = Stock.objects.all()
for company in companies:
    already_exists = bool(len(stocks.filter(company=company)))
    if not already_exists:
        price = randrange(5, 250)
        count = randrange(500, 1000)
        new_stock = Stock(company=company,
                          name=company.name + " - generated automatically",
                          price=price,
                          avail_amount=count)
        new_stock.save()


