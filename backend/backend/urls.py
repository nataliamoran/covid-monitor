from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('api/', include('covidmonitor.urls')),
    path('admin/', admin.site.urls),
]

# urlpatterns += [re_path('', TemplateView.as_view(template_name='index.html'))]