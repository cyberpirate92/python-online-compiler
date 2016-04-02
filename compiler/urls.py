from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^compiler$',views.testpage),
]