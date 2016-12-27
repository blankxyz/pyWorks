from django.contrib.auth.models import User, Group
from rest_framework import serializers
from appWeibo.models import User



# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ('url', 'username', 'email', 'groups')


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Group
#         fields = ('url', 'name')


class UserSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        # If you don't have a json serializable object
        # you can do the transformations here
        return obj
    # uid = serializers.CharField()
    # status_count = serializers.IntegerField()
    # timestamp = serializers.IntegerField()
    # lid = serializers.IntegerField()