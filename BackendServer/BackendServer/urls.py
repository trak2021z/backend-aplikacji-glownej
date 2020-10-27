"""BackendServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi

import Exchange.views as v

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^foo/$', v.DummyView.as_view(), name='dummy_view'),
    url(r'^bar/$', v.TestView.as_view(), name='test_view'),
    url(r'^baz/$', v.MatchView.as_view(), name='match_view'),
    url(r'^stocks/$', v.StocksView.as_view(), name='stocks_view'),
    url(r'^company/$', v.CompanyView.as_view(), name='company_view'),
    url(r'^company/(?P<pk>\d+)/$', v.CompanyView.as_view(), name='company_detail_view'),
    url(r'^buyoffer/$', v.BuyOfferView.as_view(), name='buy_offer_view'),
    url(r'^selloffer/$', v.SellOfferView.as_view(), name='sell_offer_view'),
    url(r'^buyoffer/(?P<pk>\d+)/$', v.BuyOfferView.as_view(), name='buy_offer_view'),
    url(r'^selloffer/(?P<pk>\d+)/$', v.SellOfferView.as_view(), name='sell_offer_view'),
    url(r'^user/stocks/$', v.UserStockView.as_view(), name='user_stocks_view'),
    url(r'^user/wallet/$', v.UserWalletView.as_view(), name='user_wallet_view'),
    url(r'^user/history/$', v.UserTransactionView.as_view(), name='user_history_view'),
    url(r'^user/offers/$', v.UserOffersView.as_view({'get': 'get'}), name='user_offers_view'),
    url(r'^stocks/(?P<pk>\d+)/buy/$', v.StockBuyView.as_view(), name='stock_buy_view'),
    url(r'^transaction/(?P<pk>\d+)/$', v.TransactionView.as_view(), name='transaction_stock_view'),
    url(r'^transaction/$', v.TransactionView.as_view(), name='transaction_view'),
    url(r'^user/stocks/(?P<pk>\d+)/sell/$', v.StockSellView.as_view(), name='stock_sell_view'),
]
