from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Stock

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
