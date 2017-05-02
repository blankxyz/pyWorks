# coding=utf-8
from django.db import models


class XPathEntity(models.Model):
    username = models.CharField(max_length=50, db_index=True)
    url = models.CharField(max_length=255, db_index=True)
    title_xpath = models.CharField(max_length=255, null=True)
    content_xpath = models.CharField(max_length=255, null=True)
    ctime_xpath = models.CharField(max_length=255, null=True)
    source_xpath = models.CharField(max_length=255, null=True)
    page_xpath = models.CharField(max_length=255, null=True)