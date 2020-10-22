from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
from .serializers import StockSerializer, BuyOfferSerializer, SellOfferSerializer, CompanySerializer, \
    SingleCompanySerializer, UserStockSerializer, UserWalletSerializer
from .models import Stock, BuyOffer, SellOffer, Profile, UserStock, Company
from .tasks import recalculate_prices, regenerate_stocks

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
            stocks = Stock.objects.all().filter(company=company)
            serializer = self.single_company_serializer_class(company)
        else:
            companies = Company.objects.all()
            serializer = self.company_serializer_class(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BuyOfferView(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            currentUser = Profile.objects.get(id=request.user.id)
            payloadStock = Stock.objects.get(id=payload["stock"])
            buyOffer = BuyOffer.objects.create(
                user=currentUser,
                stock=payloadStock,
                unit_price=payload["unit_price"],
                status=1,
                stock_amount=payload["stock_amount"])
            serializer = BuyOfferSerializer(buyOffer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something terrible went wrong'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellOfferView(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            currentUser = Profile.objects.get(id=request.user.id)
            userStock = UserStock.objects.get(id=payload["user_stock"])
            if (userStock.user.id == currentUser.id and userStock.stock_amount >= payload["stock_amount"]):
                sellOffer = SellOffer.objects.create(
                    user_stock=userStock,
                    unit_price=payload["unit_price"],
                    stock_amount=payload["stock_amount"],
                    status=1)
                serializer = SellOfferSerializer(sellOffer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'error': 'Conditions not met!'}, safe=False,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something terrible went wrong.'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStockView(APIView):
    serializer_class = UserStockSerializer
    def get(self, request):
        current_user = Profile.objects.get(id=request.user.id)
        stocks = UserStock.objects.all().filter(user=current_user)
        serializer = self.serializer_class(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserWalletView(APIView):
    serializer_class = UserWalletSerializer
    def get(self, request):
        current_user = Profile.objects.get(id=request.user.id)
        serializer = self.serializer_class(current_user)
        return Response(serializer.data, status=status.HTTP_200_OK)