"""covidglassmorphism URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from UI import views
from django.conf.urls import static
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$',views.IndexPage,name="Index"),
    url('Index',views.IndexPage,name="Index"),
    url('Subscribe',views.SubscriptionPage,name="Subscribe"),
    url('Data',views.DataTablePage,name="Data"),
    url('Creators',views.CreatorPage,name="Creators"),
    url('Unsubscribe',views.UnsubscribePage,name="Unsubscribe"),
    url('Update',views.UpdatePage,name="Update"),
    url(r'^ajax/get_response/$', views.answer_me, name='get_response'),
    url(r'^ajax/predict/$', views.predicted_data, name='predict'),
]
