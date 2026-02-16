from django.contrib.sitemaps import Sitemap
from .models import Produs
from django.urls import reverse

class ProdusSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Produs.objects.all()

    def lastmod(self, obj):
        return obj.data_adaugare

class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['index', 'contact', 'produse']

    def location(self, item):
        return reverse(item)