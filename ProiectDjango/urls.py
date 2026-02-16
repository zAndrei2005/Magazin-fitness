"""
URL configuration for ProiectDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
from aplicatie import views
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from aplicatie.models import Produs
from aplicatie.sitemaps import ProdusSitemap, StaticSitemap

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("aplicatie.urls")),
]

info_produse = {
    'queryset': Produs.objects.all(),
    'date_field': 'data_adaugare',
}

sitemaps = {
    'produse_generic': GenericSitemap(info_produse, priority=0.7),
    'produse': ProdusSitemap,
    'static': StaticSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
]
