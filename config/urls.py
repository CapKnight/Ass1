from django.contrib import admin
from django.urls import path
from energy import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('country/<int:pk>/', views.country_detail, name='country_detail'),
]