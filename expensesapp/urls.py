from django.urls import path
from django.views.generic import TemplateView

app_name = 'expensesapp'
urlpatterns = [
    path('', TemplateView.as_view(template_name="expensesapp/index.html")),
]
