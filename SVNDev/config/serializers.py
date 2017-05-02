from rest_framework import serializers
from config.models import Config


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('id', 'author', 'savename')