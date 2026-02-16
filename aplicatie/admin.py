from django.contrib import admin
from .models import CustomUser, Organizator, Locatie, Furnizor, Brand, Categorie, Culoare, Dimensiune, Produs, Vizualizare, Promotie
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Organizator)

class LocatieAdmin(admin.ModelAdmin):
    list_display = ('oras', 'judet')  # afișează câmpurile în lista de obiecte
    list_filter = ('oras', 'judet')  # adaugă filtre laterale
    search_fields = ('oras',)  # permite căutarea după anumite câmpuri
    fieldsets = (
        ('Date generale', {
            'fields': ('oras', 'judet')
        }),
        ('Date Specificate', {
            'fields': ('adresa','cod_postal'),
            'classes': ('collapse',),  # secțiune pliabilă
        }),
    )

admin.site.register(Locatie, LocatieAdmin)

class FurnizorAdmin(admin.ModelAdmin):
    search_fields = ('nume', 'tara')
    
admin.site.register(Furnizor,FurnizorAdmin)

class BrandAdmin(admin.ModelAdmin):
    search_fields = ('nume', 'tara_origine')
    
admin.site.register(Brand, BrandAdmin)

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nume', 'numar_produse', 'culoare', 'icon')
    search_fields = ('nume', 'descriere')
    fieldsets = (
        ('Date generale', {'fields': ('nume', 'descriere', 'numar_produse')}),
        ('Afișare vizuală', {'fields': ('culoare', 'icon')}),
    )
    
admin.site.register(Categorie, CategorieAdmin)

class CuloareAdmin(admin.ModelAdmin):
    search_fields = ('nume','cod_hex')
    
admin.site.register(Culoare,CuloareAdmin)

class DimensiuneAdmin(admin.ModelAdmin):
    search_fields = ('eticheta', 'unitate_masura')
    
    list_display = ("eticheta", "unitate_masura", "disponibil", "lungime", "latime")
    
admin.site.register(Dimensiune,DimensiuneAdmin)

class ProdusAdmin(admin.ModelAdmin):
    search_fields = ('nume', 'descriere')
    list_display = ('id_produs','nume', 'pret', 'categorie', 'brand', 'stoc_disponibil', 'data_adaugare')
    ordering = ('-pret',)    
    
    list_filter = ('categorie', 'brand', 'stoc_disponibil', 'data_adaugare')
    list_per_page = 5
    
    fieldsets = (
        ('Date generale', {
            'fields': ('nume', 'pret', 'stoc_disponibil', 'data_adaugare', 'brand', 'categorie', 'furnizor','stoc'),
        }),
        ('Detalii opționale', {
            'classes': ('collapse',),  
            'fields': ('descriere', 'dimensiuni', 'culori'),
        }),
    )
    
admin.site.register(Produs,ProdusAdmin)

admin.site.site_header = "Panou administrativ OLTEANU Shop"
admin.site.site_title = "Admin OLTEANU Shop"
admin.site.index_title = "Bun venit în zona de administrare!"


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'country', 'newsletter', 'is_staff','blocat')
    list_filter  = ('blocat','is_staff', 'is_superuser', 'is_active', 'country', 'newsletter')

    # formularul de editare
    fieldsets = UserAdmin.fieldsets + (
        ('Informații suplimentare', {
            'fields': ('phone', 'country', 'county', 'street', 'birth_date', 'newsletter')
        }),
        ('Alte informații', {'fields': ('blocat',)}),
    )

    # formularul de creare
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informații suplimentare', {
            'classes': ('wide',),
            'fields': ('phone', 'country', 'county', 'street', 'birth_date', 'newsletter'),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Moderatori').exists():
            return (
                'username',
                'password',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
                'last_login',
                'date_joined',
            )
        return ()

admin.site.register(CustomUser,CustomUserAdmin) 

class VizualizareAdmin(admin.ModelAdmin):
    list_display = ('utilizator', 'produs', 'data_vizualizare')
    list_filter = ('utilizator', 'produs')

admin.site.register(Vizualizare, VizualizareAdmin)

class PromotieAdmin(admin.ModelAdmin):
    list_display = ('nume', 'data_creare', 'data_expirare', 'procent_discount', 'activ')
    filter_horizontal = ('categorii',)

admin.site.register(Promotie, PromotieAdmin)


