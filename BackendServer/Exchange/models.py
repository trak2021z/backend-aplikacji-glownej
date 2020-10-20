from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    created = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Company(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "companies"


class Stock(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='stocks')
    name = models.CharField(max_length=50, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    avail_amount = models.PositiveIntegerField(default=0)


class UserStock(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='userstocks')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='userstocks')
    stock_amount = models.PositiveIntegerField(default=0)


class BuyOffer(models.Model):
    OPEN = 1
    EXPIRED = 2
    CLOSED = 3
    STATUS_TYPES = [
        (OPEN, 'open'),
        (EXPIRED, 'expired'),
        (CLOSED, 'closed')
    ]

    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='buyoffers')
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='buyoffers')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.PositiveSmallIntegerField(choices=STATUS_TYPES, default=OPEN)
    stock_amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)


class SellOffer(models.Model):
    OPEN = 1
    EXPIRED = 2
    CLOSED = 3
    STATUS_TYPES = [
        (OPEN, 'open'),
        (EXPIRED, 'expired'),
        (CLOSED, 'closed')
    ]

    user_stock = models.ForeignKey('UserStock', on_delete=models.CASCADE, related_name='selloffers')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_amount = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=STATUS_TYPES, default=OPEN)
    created = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    sell = models.ForeignKey('SellOffer', on_delete=models.CASCADE, related_name='transactions', null=True)
    buy = models.ForeignKey('BuyOffer', on_delete=models.CASCADE, related_name='transactions', null=True)
    stock = models.ForeignKey('Stock', on_delete = momdels.CASCADE, related_name='transactions', null=True)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='transactions', null=True)
    amount = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
