from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'balance', 'created')

class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        fields = ('id', 'username', 'email', 'groups', 'profile',
                  'first_name', 'last_name')
        read_only_fields = ('profile', 'groups')
