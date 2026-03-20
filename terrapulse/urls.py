from django.urls import path, include

urlpatterns = [
    path('', include('dashboard.urls')),
    path('api/', include('api.urls')),
]
