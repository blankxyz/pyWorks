from django.test import TestCase

# Create your tests here.
from models import SiteList
from djangTest.settings import DBNAME,DBHOST,ALLSITE_TAB
import datetime

# Create your views here.
import time


def test(request):

    siteList = SiteList(name=ALLSITE_TAB)

    # Get all posts from DB
    print siteList

if __name__ == 'main':
    test()