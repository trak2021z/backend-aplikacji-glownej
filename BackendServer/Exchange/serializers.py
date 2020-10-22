from rest_framework import serializers
from .models import Stock, BuyOffer, SellOffer

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['company', 'name', 'price', 'avail_amount']
        
class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = ['user', 'stock', 'unit_price', 'status', 'stock_amount', 'created']
        
class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['user_stock', 'unit_price', 'stock_amount', 'status', 'created']