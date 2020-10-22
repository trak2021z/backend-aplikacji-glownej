from rest_framework import serializers
from .models import Stock, BuyOffer, SellOffer, Profile, Company
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'balance', 'created')


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups', 'profile',
                  'first_name', 'last_name')
        read_only_fields = ('profile', 'groups')


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['company', 'name', 'price', 'avail_amount']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['pk', 'name']


class SingleCompanySerializer(serializers.ModelSerializer):
    stocks = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['name', 'stocks']


class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = ['user', 'stock', 'unit_price', 'status', 'stock_amount', 'created']


class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['user_stock', 'unit_price', 'stock_amount', 'status', 'created']
