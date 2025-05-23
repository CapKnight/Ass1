from django.contrib import admin
from django.urls import path, include
from energy import views

app_name = 'energy'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(
        ([
            path('', views.index, name='index'),
            path('country/<int:pk>/', views.country_detail, name='country_detail'),
            path('map/', views.map_view, name='map'),
            path('compare/', views.compare_countries, name='compare'),
        ], 'energy'),
        namespace='energy'
    )),
]