from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .tasks import recalculate_prices, regenerate_stocks, seed_stocks


class DummyView(APIView):
    def get(self, request, pk=None, format=None):
        recalculate_prices()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestView(APIView):
    def get(self, request, pk=None, format=None):
        regenerate_stocks()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SeedView(APIView):
    def get(self, request, pk=None, format=None):
        seed_stocks()
        return Response(status=status.HTTP_204_NO_CONTENT)
