from django.urls import path
from api import views

urlpatterns = [
    path('weather/', views.weather_view, name='api_weather'),
    path('stocks/', views.stocks_view, name='api_stocks'),
    path('stock-history/', views.stock_history_view, name='api_stock_history'),
    path('news/', views.news_view, name='api_news'),
    path('signals/', views.signals_view, name='api_signals'),
    path('geo/', views.geo_view, name='api_geo'),
]
