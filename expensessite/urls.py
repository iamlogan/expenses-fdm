from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib import admin


urlpatterns = [
    path("", include("expensesapp.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    path("admin/", admin.site.urls),
]
