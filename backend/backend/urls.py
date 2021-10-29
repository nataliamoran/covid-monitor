from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('covidmonitor/', include('covidmonitor.urls')),
    path('admin/', admin.site.urls),
]
