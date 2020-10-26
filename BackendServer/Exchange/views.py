from django.shortcuts import render

# Create your views here.
from drf_yasg2.utils import swagger_auto_schema, is_list_view
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

    @swagger_auto_schema(responses={200: serializer_class(many=True)})
    def get(self, request, format=None):
        stocks = Stock.objects.all()
        page = self.paginate_queryset(stocks)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyView(APIView):
    serializer_class = CompanySerializer

    @swagger_auto_schema(responses={200: serializer_class()})
    def get(self, request, pk=None, format=None):
        if pk:
            serializer = self.get_single(request, pk, format)
        else:
            serializer = self.get_many(request, format)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_single(self, request, pk, format=None):
        company = Company.objects.get(id=pk)
        return self.serializer_class(company)

    def get_many(self, request, format=None):
        companies = Company.objects.all()
        return self.serializer_class(companies, many=True, fields=('pk', 'name'))


class BuyOfferView(APIView):
    @swagger_auto_schema(request_body=BuyOfferInputSerializer(), responses={201: BuyOfferSerializer()})
    def post(self, request):
        try:
            currentUser = request.user.profile
            serializer = BuyOfferInputSerializer(data=request.data, fields=('stock', 'unit_price', 'stock_amount'))
            if serializer.is_valid():
                payloadStock = serializer.validated_data['stock']
                buyOffer = BuyOffer.objects.create(
                    user=currentUser,
                    stock=payloadStock,
                    unit_price=serializer.validated_data["unit_price"],
                    status=1,
                    stock_amount=serializer.validated_data["stock_amount"]
                )
                save_serializer = BuyOfferSerializer(buyOffer)
                return Response(save_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something terrible went wrong'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellOfferView(APIView):
    @swagger_auto_schema(request_body=SellOfferInputSerializer(), responses={201: SellOfferSerializer()})
    def post(self, request):
        try:
            currentUser = request.user.profile
            serializer = SellOfferInputSerializer(data=request.data)
            if serializer.is_valid():
                userStock = serializer.validated_data['user_stock']
                if userStock.user.id == currentUser.id and userStock.stock_amount >= serializer.validated_data["stock_amount"]:
                    sellOffer = SellOffer.objects.create(
                        user_stock=userStock,
                        unit_price=serializer.validated_data["unit_price"],
                        status=1,
                        stock_amount=serializer.validated_data["stock_amount"]
                    )
                    save_serializer = SellOfferSerializer(sellOffer)
                    return Response(save_serializer.data, status=status.HTTP_201_CREATED)
                return JsonResponse({'error': 'Conditions not met!'}, safe=False,
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, safe=False, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return JsonResponse({'error': 'Something terrible went wrong.'}, safe=False,
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStockView(APIView):
    serializer_class = UserStockSerializer

    @swagger_auto_schema(responses={200: serializer_class(many=True)})
    def get(self, request):
        current_user = request.user.profile
        stocks = UserStock.objects.all().filter(user=current_user)
        serializer = self.serializer_class(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWalletView(APIView):
    serializer_class = UserWalletSerializer

    @swagger_auto_schema(responses={200: serializer_class()})
    def get(self, request):
        current_user = request.user.profile
        serializer = self.serializer_class(current_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StockBuyView(APIView):
    serializer_class = TransactionSerializer

    @swagger_auto_schema(request_body=BuySellInputSerializer(), responses={201: serializer_class()})
    def post(self, request, pk=None):
        current_user = request.user.profile
        stock = Stock.objects.get(pk=pk)
        balance = current_user.balance
        s = BuySellInputSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data
        quantity = payload["quantity"]
        total_price = stock.price * quantity
        stock_quantity = stock.avail_amount
        if stock_quantity < quantity:
            return Response({'error': 'Quantity exceeds available amount!'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        elif total_price > balance:
            return Response({'error': 'Insufficient funds!'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            current_user.balance -= total_price
            current_user.save()
            stock.avail_amount -= quantity
            stock.save()
            try:
                user_stock = UserStock.objects.get(stock=stock, user=current_user)
            except UserStock.DoesNotExist:
                user_stock = {}
            if user_stock:
                user_stock.stock_amount += quantity
                user_stock.save()
            else:
                new_user_stock = UserStock(
                    user=current_user,
                    stock=stock,
                    stock_amount=quantity,
                )
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
            if transaction.pk % 5 == 0:
                recalculate_prices.delay()
            serializer = self.serializer_class(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)


class StockSellView(APIView):
    serializer_class = TransactionSerializer

    @swagger_auto_schema(request_body=BuySellInputSerializer(), responses={201: serializer_class()})
    def post(self, request, pk=None):
        current_user = request.user.profile
        s = BuySellInputSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
        payload = s.validated_data
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
            if transaction.pk % 5 == 0:
                recalculate_prices.delay()
            serializer = self.serializer_class(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
