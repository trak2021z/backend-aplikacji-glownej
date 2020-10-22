from rest_framework import serializers
from .models import Stock, BuyOffer, SellOffer, Profile, Company, UserStock
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('pk', 'balance', 'created')


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'groups', 'profile',
                  'first_name', 'last_name')
        read_only_fields = ('profile', 'groups')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['pk', 'name']


class StockSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Stock
        fields = ['pk', 'company', 'name', 'price', 'avail_amount']


class SingleCompanySerializer(serializers.ModelSerializer):
    stocks = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['pk', 'name', 'stocks']


class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = ['pk', 'user', 'stock', 'unit_price', 'status', 'stock_amount', 'created']


class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['pk', 'user_stock', 'unit_price', 'stock_amount', 'status', 'created']

class UserStockSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    class Meta:
        model = UserStock
        fields = ['pk', 'stock', 'stock_amount']

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['balance']
