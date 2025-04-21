from django.contrib import admin
from django.urls import path, include
from energy import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include(
        ([
            path('', views.index, name='index'),
            path('country/<int:pk>/', views.country_detail, name='country_detail'),
        ], 'energy'),  # (patterns, app_name)
        namespace='energy'
    )),
]