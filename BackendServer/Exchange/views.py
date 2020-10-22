from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
from .serializers import *
from .models import Stock, BuyOffer, SellOffer, Profile, UserStock, Company, Transaction
from .tasks import recalculate_prices, regenerate_stocks
from datetime import datetime as dt
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
            currentUser = request.user.profile
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
            currentUser = request.user.profile
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
        current_user = request.user.profile
        stocks = UserStock.objects.all().filter(user=current_user)
        serializer = self.serializer_class(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWalletView(APIView):
    serializer_class = UserWalletSerializer

    def get(self, request):
        current_user = request.user.profile
        serializer = self.serializer_class(current_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StockBuyView(APIView):
    serializer_class = TransactionSerializer

    def post(self, request, pk=None):
        current_user = request.user.profile
        stock = Stock.objects.get(pk=pk)
        balance = current_user.balance
        payload = json.loads(request.body)
        quantity = payload["quantity"]
        total_price = stock.price * quantity
        stock_quantity = stock.avail_amount
        if stock_quantity < quantity:
            return Response({'error': 'Quantity exceeds available amount!'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif total_price > balance:
            return Response({'error': 'Insufficient funds!'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            new_user_stock = UserStock(
                user=current_user,
                stock=stock,
                stock_amount=quantity,
            )
            current_user.balance -= total_price
            current_user.save()
            stock.avail_amount -= quantity
            stock.save()
            new_user_stock.save()
            transaction = Transaction(
                sell=None,
                buy=None,
                stock=stock,
                user=current_user,
                amount=quantity,
                unit_price=stock.price,
                date=dt.now,
                is_sell=False,
            )
            transaction.save()
            serializer = self.serializer_class(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)


class StockSellView(APIView):
    serializer_class = TransactionSerializer

    def post(self, request, pk=None):
        current_user = request.user.profile
        payload = json.loads(request.body)
        quantity = payload["quantity"]
        current_user = request.user.profile
        user_stock = UserStock.objects.get(pk=pk)
        stock = user_stock.stock
        total_price = stock.price * quantity
        stock_quantity = user_stock.stock_amount
        if stock_quantity < quantity:
            return Response({'error': 'Quantity exceeds owned amount!'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            current_user.balance += total_price
            current_user.save()
            stock.avail_amount += quantity
            stock.save()
            if stock_quantity == quantity:
                user_stock.delete()
            else:
                user_stock.stock_amount -= quantity
                user_stock.save()
            transaction = Transaction(
                sell=None,
                buy=None,
                stock=stock,
                user=current_user,
                amount=quantity,
                unit_price=stock.price,
                date=dt.now,
                is_sell=True,
            )
            transaction.save()
            serializer = self.serializer_class(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
