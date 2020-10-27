from rest_framework import serializers
from .models import Stock, BuyOffer, SellOffer, Profile, Company, UserStock, Transaction
from django.contrib.auth.models import User


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProfileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Profile
        fields = ('pk', 'balance', 'created')


class UserDetailSerializer(DynamicFieldsModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'groups', 'profile',
                  'first_name', 'last_name')
        read_only_fields = ('profile', 'groups')


class CompanySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Company
        fields = ['pk', 'name']


class StockSerializer(DynamicFieldsModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Stock
        fields = ['pk', 'company', 'name', 'price', 'avail_amount']

class SingleCompanySerializer(DynamicFieldsModelSerializer):
    stocks = StockSerializer(many=True)

    class Meta:
        model = Company
        fields = ['pk', 'name', 'stocks']


class BuyOfferInputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BuyOffer
        fields = ['stock', 'unit_price', 'stock_amount']


class BuyOfferSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BuyOffer
        fields = ['pk', 'user', 'stock', 'unit_price', 'status', 'stock_amount', 'created']


class SellOfferInputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['user_stock', 'unit_price', 'stock_amount']


class SellOfferSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['pk', 'user_stock', 'unit_price', 'stock_amount', 'status', 'created']


class OfferSerializer(serializers.Serializer):
    buy_offers = BuyOfferSerializer(many=True)
    sell_offers = SellOfferSerializer(many=True)

class UserStockSerializer(DynamicFieldsModelSerializer):
    stock = StockSerializer(read_only=True)

    class Meta:
        model = UserStock
        fields = ['pk', 'stock', 'stock_amount']


class UserWalletSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Profile
        fields = ['balance']


class TransactionSerializer(DynamicFieldsModelSerializer):
    stock = StockSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['sell', 'buy', 'stock', 'amount', 'unit_price', 'date', 'is_sell']


class BuySellInputSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()