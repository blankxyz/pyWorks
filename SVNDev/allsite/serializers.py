# coding:utf-8
from rest_framework import serializers
from .models import XPathEntity


class XPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPathEntity
        fields = ['username', 'url', 'title_xpath', 'content_xpath', 'ctime_xpath', 'source_xpath', 'page_xpath']
