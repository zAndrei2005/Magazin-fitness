from django.urls import path
from . import views
urlpatterns = [
	path("", views.index, name="index"),
    path("info/", views.info, name="info"),
    path("log/", views.log_cereri, name="log"),
    path("exemplu/", views.afis_template, name="exemplu1"),
    path('despre/', views.despre, name='despre'),
    path('produse/', views.afis_produse, name='produse'),
    path('contact/', views.contact, name='contact'),
    path('cos_virtual/', views.cos_virtual, name='cos_virtual'),
    path("locatii", views.afis_locatii, name="locatii"), # EXEMPLU CURS
    path('produse/<int:pk>/', views.produs_detail, name='produs_detail'),
    path('produse/<str:sort>/', views.afis_produse, name='produse_sort'),
    path('categorii/', views.lista_categorii, name='categorii'),                 
    path('categorii/<str:nume_categorie>/', views.afis_categorie, name='categorie'), 
    path('contact/', views.contact, name = 'contact'),
    path('adauga_produs/', views.adauga_produs, name = 'adauga_produs'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profil/", views.profil_view, name="profil"),
    path("schimba-parola/", views.schimba_parola_view, name="schimba_parola"),
    path('confirma_mail/<str:cod>/', views.confirma_mail, name='confirma_mail'),
    path('register/', views.register_view, name="register"),
    path("promotii/", views.promotii_view, name="promotii"),
    path('interzis/', views.pagina_interzisa, name='interzis'),
    path("acorda_oferta/", views.acorda_oferta, name="acorda_oferta"),
    path("oferta/", views.oferta, name="oferta"),
    path("cos/", views.cos_view, name="cos"),
    path("cumpara/", views.cumpara_view, name="cumpara"),
]

