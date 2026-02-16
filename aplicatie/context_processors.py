from .models import Categorie

def categorii_context(request):
    return {'categorii': Categorie.objects.all()}
