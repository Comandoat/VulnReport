from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('gestion-securisee/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/kb/', include('kb.urls')),
    path('api/audit/', include('audit.urls')),
]
