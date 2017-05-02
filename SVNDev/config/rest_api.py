from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from config.serializers import ConfigSerializer
from config.models import Config

import json


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# @login_required
# @permission_required('backend_admin.view_groupconfigeach')
# @api_view(['GET', 'POST'])
# def config_groups_list_api(request):
#     if request.method == 'GET':
#         groups = Config.objects.all()
#         serializer = ConfigSerializer(groups, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ConfigSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfigGroupsListApi(APIView):
    def get(self, request, format=None):
        groups = Config.objects.all()
        serializer = ConfigSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
