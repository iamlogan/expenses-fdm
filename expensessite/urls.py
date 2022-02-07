from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib import admin


urlpatterns = [
    path("", include("expensesapp.urls")),
    path('accounts/', include('allauth.urls')),
    path("admin/", admin.site.urls),
]

'''
allauth templates and corresponding URLs:

account_inactive.html               /accounts/inactive
email_confirm.html	                /accounts/confirm-email/
login.html	                        /accounts/login/
logout.html	                        /accounts/logout/
password_reset.html	                /accounts/password/reset/
password_reset_done.html	        /accounts/password/reset/done/
password_reset_from_key.html	    /accounts/password/reset/key/<key>/
password_reset_from_key_done.html   /accounts/password/reset/key/done/
signup.html	                        /accounts/signup/
verification_sent.html	            /accounts/confirm-email/
'''