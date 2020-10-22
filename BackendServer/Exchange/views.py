from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from .tasks import recalculate_prices, regenerate_stocks

from .serializers import StockSerializer, CompanySerializer, SingleCompanySerializer
from .models import Stock, Company
from .pagination import PaginationHandlerMixin


class DummyView(APIView):
    def get(self, request, pk=None, format=None):
        recalculate_prices()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestView(APIView):
    def get(self, request, pk=None, format=None):
        regenerate_stocks()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StocksView(APIView, PaginationHandlerMixin):
    page_size_query_param = 'limit'
    pagination_class = LimitOffsetPagination
    serializer_class = StockSerializer

    def get(self, request, format=None):
        stocks = Stock.objects.all()
        page = self.paginate_queryset(stocks)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyView(APIView):
    company_serializer_class = CompanySerializer
    single_company_serializer_class = SingleCompanySerializer

    def get(self, request, pk=None, format=None):
        if pk:
            company = Company.objects.get(id=pk)
            stocks = Stock.objects.all().filter(company = company)
            serializer = self.single_company_serializer_class(company)
        else:
            companies = Company.objects.all()
            serializer = self.company_serializer_class(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
