from django.urls import path
from . import views

urlpatterns = [
    path("",views.main,name="main"),
    path("request_ticker/<str:company_name>", views.request_ticker,name="ticker_get"),
    path("request_financial_yearly/<str:company_name>", views.request_financial_yearly,name="yearly_get"),
]



