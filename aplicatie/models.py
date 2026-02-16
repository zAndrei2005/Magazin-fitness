from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse 

# Create your models here.

class Organizator(models.Model):
    nume = models.CharField(max_length=100)
    email = models.EmailField()
    def __str__(self):
        return self.nume

class Locatie(models.Model):
    adresa = models.CharField(max_length=255)
    oras = models.CharField(max_length=100)
    judet = models.CharField(max_length=100)
    cod_postal = models.CharField(max_length=10)
    nr = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.adresa}, {self.oras}"

class Furnizor(models.Model):
    id_furnizor = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=50)
    tara = models.CharField(max_length=50)
    email = models.EmailField()
    telefon = models.CharField(max_length=20)
    rating = models.FloatField()
    
    def __str__(self):
        return self.nume

class Brand(models.Model):
    id_brand = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=50)
    tara_origine = models.CharField(max_length=50)
    website = models.CharField(max_length=100)
    an_infiintare = models.IntegerField()

    def __str__(self):
        return self.nume


class Categorie(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=50)
    descriere = models.TextField()
    numar_produse = models.IntegerField()

    culoare = models.CharField(max_length=7, blank=True, help_text="ex: #4f46e5")
    icon = models.CharField(max_length=50, blank=True, help_text="ex: fa-dumbbell")
    
    def get_absolute_url(self):
        return reverse('categorie_detail', args=[self.pk])
    
    def __str__(self):
        return self.nume


class Culoare(models.Model):
    id_culoare = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=50)
    cod_hex = models.CharField(max_length=7)
    data_adaugare = models.DateField()
    intensitate = models.IntegerField()

    def __str__(self):
        return f"{self.nume} ({self.cod_hex})"


class Dimensiune(models.Model):
    id_dimensiune = models.AutoField(primary_key=True)
    eticheta = models.CharField(max_length=20)
    unitate_masura = models.CharField(max_length=10)
    disponibil = models.BooleanField()
    lungime = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    latime = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.eticheta} ({self.unitate_masura})"


class Produs(models.Model):
    id_produs = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    pret = models.DecimalField(max_digits=8, decimal_places=2)
    descriere = models.TextField()
    stoc_disponibil = models.BooleanField()
    stoc = models.PositiveIntegerField(default=0)
    data_adaugare = models.DateField()

    # Relații
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    furnizor = models.ForeignKey(Furnizor, on_delete=models.CASCADE)
    dimensiuni = models.ManyToManyField(Dimensiune)
    culori = models.ManyToManyField(Culoare)
    
    def get_absolute_url(self):
        return reverse('produs_detail', args=[self.pk])

    def __str__(self):
        return f"{self.nume} - {self.pret} RON"
    

class Voucher(models.Model):
    code = models.CharField(max_length=30, unique=True)
    
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  
    discount_amount  = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  
    valid_from = models.DateTimeField()
    valid_to   = models.DateTimeField()
    active     = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  # None = nelimitat
    used_count  = models.PositiveIntegerField(default=0)
    min_order_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

 
    eligible_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='vouchere_eligibile'
    )

    def is_valid_now(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def __str__(self):
        return f"{self.code} ({'activ' if self.is_valid_now() else 'expirat'})"


class Comanda(models.Model):
    STATUS_CHOICES = [
        ('noua', 'Nouă'),
        ('proc', 'În procesare'),
        ('ship', 'În livrare'),
        ('done', 'Finalizată'),
        ('cancel', 'Anulată'),
    ]
    METODA_PLATA = [
        ('card', 'Card'),
        ('ramburs', 'Ramburs'),
        ('transfer', 'Transfer bancar'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comenzi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='noua')

    metoda_plata = models.CharField(max_length=10, choices=METODA_PLATA, default='card')
    adresa_livrare = models.CharField(max_length=255)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    voucher = models.ForeignKey(Voucher, null=True, blank=True, on_delete=models.SET_NULL, related_name='comenzi')

    def recalc_total(self, save=True):
        subtotal = sum((li.cantitate * li.pret_unitar for li in self.linii.all()), Decimal('0.00'))
        total = subtotal

        if self.voucher and self.voucher.is_valid_now() and subtotal >= self.voucher.min_order_total:
            if self.voucher.discount_percent:
                total = total * (Decimal('100') - self.voucher.discount_percent) / Decimal('100')
            if self.voucher.discount_amount:
                total = total - self.voucher.discount_amount
            if total < 0:
                total = Decimal('0.00')

        total = total.quantize(Decimal('0.01'))
        self.total = total
        if save:
            self.save(update_fields=['total'])
        return total

    def __str__(self):
        return f"Comanda #{self.pk} - {self.user} - {self.get_status_display()}"


class ComandaItem(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='linii')
    produs  = models.ForeignKey('Produs', on_delete=models.PROTECT, related_name='linii_comanda')
    cantitate = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    pret_unitar = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [('comanda', 'produs')]  

    def line_total(self):
        return (self.pret_unitar * self.cantitate).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.produs} x {self.cantitate} pentru Comanda #{self.comanda_id}"


class Review(models.Model):
    user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviewuri')
    produs = models.ForeignKey('Produs', on_delete=models.CASCADE, related_name='reviewuri')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    titlu  = models.CharField(max_length=100, blank=True)
    text   = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved   = models.BooleanField(default=True)

    class Meta:
        unique_together = [('user', 'produs')]  
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.rating}/5 de la {self.user} pentru {self.produs}"
    
 
class CustomUser(AbstractUser):
    phone        = models.CharField(max_length=20, blank=True)
    country      = models.CharField(max_length=50, blank=True)
    county       = models.CharField(max_length=50, blank=True)  
    street       = models.CharField(max_length=100, blank=True)
    birth_date   = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    newsletter   = models.BooleanField(default=False)
    cod = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Cod de confirmare email."
    )
    email_confirmat = models.BooleanField(
        default=False,
        help_text="Daca emailul a fost confirmat"
    )
    
    blocat = models.BooleanField(default=False)
    
    class Meta:
        permissions = [
            ("vizualizeaza_oferta", "Poate vizualiza oferta speciala"),
        ]

    def __str__(self):
        return self.username 

class Vizualizare(models.Model):
    utilizator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vizualizari'
    )
    produs = models.ForeignKey(
        Produs,
        on_delete=models.CASCADE,
        related_name='vizualizari'
    )
    data_vizualizare = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_vizualizare']  

    def __str__(self):
        return f"{self.utilizator.username} a vizualizat {self.produs.nume} la {self.data_vizualizare}"
    
class Promotie(models.Model):
    nume = models.CharField(max_length=100)
    subiect = models.CharField(max_length=150)
    mesaj_baza = models.TextField()
    data_creare = models.DateTimeField(auto_now_add=True)
    data_expirare = models.DateTimeField()
    procent_discount = models.PositiveIntegerField(
        default=10,
        help_text="Reducere procentuală (ex: 10 pentru 10%)."
    )
    activ = models.BooleanField(default=True)
    categorii = models.ManyToManyField(
        Categorie,
        related_name='promotii'
    )

    def __str__(self):
        return f"{self.nume} (expiră la {self.data_expirare})"
    
