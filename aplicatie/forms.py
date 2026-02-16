from django import forms
from datetime import date, datetime
from django.core.exceptions import ValidationError
from .models import Brand, Categorie, Furnizor, Culoare, Dimensiune, Produs
import re
from decimal import Decimal,ROUND_HALF_UP
from django.contrib.auth.forms import AuthenticationForm

def validate_major(dob: date):
    if dob is None:
        return
    today = date.today()
    years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if years < 18:
        raise ValidationError("Trebuie să aveți cel puțin 18 ani.")

_http_re = re.compile(r'\bhttps?://', re.IGNORECASE)
def validate_no_links(text: str):
    if not text:
        return
    if _http_re.search(text):
        raise ValidationError("Textul nu poate conține linkuri (http:// sau https://).")

_word_re = re.compile(r'[0-9A-Za-z]+', re.UNICODE)
def validate_message_words(text: str):
    if not text:
        return
    words = _word_re.findall(text)
    n = len(words)
    if n < 5 or n > 100:
        raise ValidationError("Mesajul trebuie să conțină între 5 și 100 de cuvinte.")
    too_long = [w for w in words if len(w) > 15]
    if too_long:
        raise ValidationError("Niciun cuvânt din mesaj nu poate depăși 15 caractere.")

def validate_tip_mesaj(value: str):
    if value == 'neselectat':
        raise ValidationError("Selectați un tip de mesaj valid.")

BAD_DOMAINS = {'guerillamail.com', 'yopmail.com'}
def validate_no_temp_email(email: str):
    if not email:
        return
    try:
        domain = email.split('@', 1)[1].lower()
    except IndexError:
        return  
    if domain in BAD_DOMAINS:
        raise ValidationError("Nu sunt permise adrese de e-mail temporare (ex. guerillamail/yopmail).")

def validate_cnp_digits(cnp: str):
    if not cnp:
        return
    if not re.fullmatch(r'\d{13}', cnp):
        raise ValidationError("CNP-ul trebuie să conțină exact 13 cifre.")

def validate_cnp_date(cnp: str):
    if not cnp:
        return
    if cnp[0] not in ('1', '2'):
        raise ValidationError("CNP-ul trebuie sa inceapa cu 1 sau 2.")
    yy = int(cnp[1:3])
    mm = int(cnp[3:5])
    dd = int(cnp[5:7])
    
    year = 1900 + yy
    try:
        datetime(year, mm, dd)
    except ValueError:
        raise ValidationError("CNP-ul conține o dată (YYMMDD) invalidă.")


def validate_capital_and_chars(text: str):
    if text is None or text == "":
        return  
    
    for ch in text:
        if not (ch.isalpha() or ch in {' ', '-'}):
            raise ValidationError("Sunt permise doar litere, spațiu și cratimă.")
   
    stripped = text.lstrip()
    if not stripped:
        raise ValidationError("Textul nu poate fi doar spații.")
    if not stripped[0].isalpha() or not stripped[0].isupper():
        raise ValidationError("Textul trebuie să înceapă cu literă mare.")

def validate_titlecase_after_delimiters(text: str):
    if text is None or text == "":
        return  
    prev_is_delim = True
    for ch in text:
        if ch in {' ', '-'}:
            prev_is_delim = True
        else:
            if ch.isalpha():
                if prev_is_delim and not ch.isupper():
                    raise ValidationError("După spațiu sau cratimă trebuie folosită literă mare.")
                prev_is_delim = False
            else:
                prev_is_delim = False
                

_last_word_re = re.compile(r'([0-9A-Za-z]+)(?!.*[0-9A-Za-z])', re.UNICODE)

def get_last_word(text: str):
    if not text:
        return None
    m = _last_word_re.search(text)
    return m.group(1) if m else None


TIP_MESAJ_CHOICES = [
    ('neselectat', 'neselectat'),
    ('reclamatie', 'reclamație'),
    ('intrebare', 'întrebare'),
    ('review', 'review'),
    ('cerere', 'cerere'),
    ('programare', 'programare'),
]

class ContactForm(forms.Form):
    nume = forms.CharField(
        max_length=10, 
        label='Nume', 
        required=True,
        validators=[validate_capital_and_chars, validate_titlecase_after_delimiters],
        widget = forms.TextInput(attrs={'placeholder': 'Nume (max 10 caractere)'}),
        error_messages = {'required': 'Numele este obligatoriu.'} 
    )
    prenume = forms.CharField(
        label="Prenume",
        max_length=10,
        required=False,validators=[validate_capital_and_chars, validate_titlecase_after_delimiters],
        widget=forms.TextInput(attrs={'placeholder': 'Prenume (max 10)'}),
    )
    cnp = forms.CharField(
        label="CNP",
        required=False,
        validators=[validate_cnp_digits, validate_cnp_date],
        min_length=13, max_length=13,
        widget=forms.TextInput(attrs={'placeholder': '13 cifre'})
    )
    data_nasterii = forms.DateField(
        label="Data nașterii",
        required=True,
        validators=[validate_major],
        widget=forms.DateInput(attrs={'type': 'date'}),
        error_messages={'required': 'Data nașterii este obligatorie.'}
    )
    email = forms.EmailField(
        label="E-mail",
        required=True,
        validators=[validate_no_temp_email],
        widget=forms.EmailInput(attrs={'placeholder': 'ex: nume@exemplu.ro'})
    )
    email_confirm = forms.EmailField(
        label="Confirmare e-mail",
        required=True,
        validators=[validate_no_temp_email],
        widget=forms.EmailInput(attrs={'placeholder': 'reintrodu e-mailul'})
    )
    tip_mesaj = forms.ChoiceField(
        label="Tip mesaj",
        choices=TIP_MESAJ_CHOICES,
        initial='neselectat',
        required=True,
        validators=[validate_tip_mesaj],
        widget=forms.Select()
    )
    subiect = forms.CharField(
        label="Subiect",
        max_length=100,
        required=True,
        validators=[validate_no_links, validate_capital_and_chars, validate_titlecase_after_delimiters],
        widget=forms.TextInput(attrs={'placeholder': 'Subiect (max 100)'}),
        error_messages={'required': 'Subiectul este obligatoriu.'}
    )
    zile_asteptare = forms.IntegerField(
        label=("Pentru review-uri/cereri minimul de zile de așteptare trebuie setat de la 4 incolo, "
               "iar pentru reclamatii/intrebari de la 2 incolo. Maximul e 30."),
        required=True,
        min_value=1, max_value=30,
        widget=forms.NumberInput(attrs={'placeholder': 'ex: 4'})
    )
    mesaj = forms.CharField(
        label="Mesaj (vă rugăm să vă semnați)",
        required=True,
        validators=[validate_no_links, validate_message_words],
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Scrie mesajul și semnează-te la final'})
    )
    
    def clean(self):
        cleaned = super().clean()

        nume  = (cleaned.get('nume') or '').strip()
        pren  = (cleaned.get('prenume') or '').strip()
        email = (cleaned.get('email') or '').strip()
        email2 = (cleaned.get('email_confirm') or '').strip()
        tip   = cleaned.get('tip_mesaj')
        zile  = cleaned.get('zile_asteptare')
        mesaj = cleaned.get('mesaj') or ''
        cnp   = (cleaned.get('cnp') or '').strip()
        dob   = cleaned.get('data_nasterii')  # datetime.date

        if email and email2 and email.casefold() != email2.casefold():
            self.add_error('email_confirm', "E-mailul de confirmare nu coincide cu e-mailul introdus.")

        if mesaj and nume:
            last = get_last_word(mesaj)
            if not last or last.casefold() != nume.casefold():
                self.add_error('mesaj', "Ultimul cuvant din mesaj trebuie sa fie numele (semnatura).")

        if zile is not None and tip:
            if tip in ('review', 'cerere') and zile < 4:
                self.add_error('zile_asteptare', "Pentru review/cerere, minimul este 4 zile.")
            if tip in ('reclamatie', 'intrebare') and zile < 2:
                self.add_error('zile_asteptare', "Pentru reclamație/întrebare, minimul este 2 zile.")
            if zile > 30:
                self.add_error('zile_asteptare', "Maximul de zile de așteptare este 30.")

        if dob and len(cnp) == 13 and cnp.isdigit():
            s  = cnp[0]
            yy = int(cnp[1:3])
            mm = int(cnp[3:5])
            dd = int(cnp[5:7])

            if s not in ('1', '2'):
                pass
            else:
                year = 2000 + yy
                try:
                    cnp_date = date(year, mm, dd)
                except ValueError:
                    cnp_date = None

                if cnp_date:
                    if (dob.year, dob.month, dob.day) != (cnp_date.year, cnp_date.month, cnp_date.day):
                        self.add_error('cnp', "CNP-ul nu corespunde cu data nașterii introdusă.")
                        self.add_error('data_nasterii', "Data nașterii nu corespunde cu data din CNP.")

            return cleaned

        
class FiltruProduseForm(forms.Form):
    nume = forms.CharField(
        label='Nume', 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Caută după nume...'}),
        error_messages={
            'invalid': 'Numele conține caractere nepermise.',
            'min_length': 'Numele trebuie să aibă cel puțin 2 caractere.',
        }
    )
    descriere = forms.CharField(
        label='Descriere conține',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Caută în descriere...'})
    )

    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        required=False,
        empty_label='Toate categoriile',
        widget=forms.Select()
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False, 
        empty_label='Toate brandurile',
        widget=forms.Select()
    )
    furnizor = forms.ModelChoiceField(
        queryset=Furnizor.objects.all(), 
        required=False, 
        empty_label='Toți furnizorii',
        widget=forms.Select()
    )

    culori = forms.ModelMultipleChoiceField(
        queryset=Culoare.objects.all(), 
        required=False,
        widget=forms.SelectMultiple()
    )
    dimensiuni = forms.ModelMultipleChoiceField(
        queryset=Dimensiune.objects.all(), 
        required=False,
        widget=forms.SelectMultiple(),
        label = "Dimensiuni"
    )

    stoc_disponibil = forms.NullBooleanField(
        label='În stoc', 
        required=False,
        widget=forms.Select(choices=[
            ('', 'Toate'),
            ('true', 'Disponibil'),
            ('false', 'Indisponibil')
        ])
    )

    pret_min = forms.DecimalField(
        label='Preț minim', 
        required=False,
        min_value=0, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Min'}),
        error_messages={
            'invalid': 'Introduceti un numar valid pentru pretul minim.',
            'min_value': 'Pretul minim nu poate fi negativ.',
        }
    )
    pret_max = forms.DecimalField(
        label='Preț maxim', 
        required=False, 
        min_value=0, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Max'}),
        error_messages={
            'invalid': 'Introduceti un numar valid pentru pretul maxim.',
            'min_value': 'Pretul maxim nu poate fi negativ.',
        }
    )

    data_min = forms.DateField(label='Data adăugare de la', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_max = forms.DateField(label='Data adăugare până la', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    nr_pe_pagina = forms.IntegerField(
        required = False,
        label = "Produse pe pagina",
        initial = '5',
        widget = forms.NumberInput()
    )
    
    def clean_nume(self):
        val = self.cleaned_data.get('nume')
        if not val:
            return val
        if len(val.strip()) < 2:
            raise forms.ValidationError("Numele trebuie să aibă cel puțin 2 caractere.")
        if not re.match(r'^[\w\s\-]+$', val, flags=re.UNICODE):
            raise forms.ValidationError("Numele poate conține doar litere, cifre, spații, '-' și '_'.")
        return val
    
    def clean(self):
        cleaned = super().clean()
        pret_min = cleaned.get('pret_min')
        pret_max = cleaned.get('pret_max')
        
        if pret_min is not None and pret_max is not None:
            if pret_min > pret_max:
                self.add_error('pret_max', "Prețul maxim trebuie să fie mai mare sau egal cu prețul minim.")

        return cleaned
 
   
_http_re = re.compile(r'\bhttps?://', re.I)
_word_re = re.compile(r'[0-9A-Za-zăâîșțĂÂÎȘȚ]+')

def validate_min_words(value: str, min_w=3):
    n = len(_word_re.findall(value or ""))
    if n < min_w:
        raise ValidationError(f"Trebuie sa existe cel putin {min_w} cuvinte.")

def validate_starts_with_capital(value: str):
    v = (value or "").lstrip()
    if not v or not v[0].isalpha() or not v[0].isupper():
        raise ValidationError("Textul trebuie sa înceapa cu litera mare.")
    
        
class ProdusForm(forms.ModelForm):
    stoc_initial = forms.IntegerField(
        label="Stoc inițial",
        min_value=0,
        required=True,
        help_text="Dacă e 0, produsul va fi marcat ca indisponibil.",
        error_messages={
        'required': 'Completati stocul initial.',
        'min_value': 'Stocul nu poate fi negativ.',
        'invalid': 'Introduceti un numar intreg valid pentru stoc.'
        }
    )
    reducere_pct = forms.DecimalField(
        label="Reducere (%)",
        min_value=0, max_value=90,
        decimal_places=2,
        required=False,
        initial=0,
        help_text="Opțional. Se aplică peste prețul introdus."
    )
    
    cost_achizitie = forms.DecimalField(
        label="Cost achiziție (RON)",
        min_value=0, decimal_places=2, required=True,
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'ex: 120.00'}),
        error_messages={
        'required': 'Completati costul de achizitie.',
        'min_value': 'Costul nu poate fi negativ.',
        'invalid': 'Introduceti un număr valid (ex: 99.99).'
        }
    )
    adaos_pct = forms.DecimalField(
        label="Adaos (%)",
        min_value=0, max_value=200, decimal_places=2, required=True,
        initial=20,
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'ex: 25.00'}),
        error_messages={
        'required': 'Introduceti adaosul comercial.',
        'min_value': 'Adaosul nu poate fi negativ.',
        'max_value': 'Adaosul nu poate depasi 200%.',
        'invalid': 'Introduceti o valoare numerica valida pentru adaos.'
    }
    )
    

    nume = forms.CharField(
        label='Denumire produs',
        widget=forms.TextInput(attrs={'placeholder': 'Denumire produs'}),
        validators=[validate_starts_with_capital, validate_no_links] ,
        error_messages={
        'required': 'Introduceti denumirea produsului.',
        'max_length': 'Numele este prea lung (maxim 100 de caractere).',
        'invalid': 'Numele contine caractere nepermise.'} 
    )
    descriere = forms.CharField(
        label='Descriere scurta',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        validators=[validate_no_links, validate_min_words],
        error_messages={
        'invalid': 'Descrierea trebuie să contina doar caractere alfanumerice.',
        }            
    )


    class Meta:
        model = Produs
        fields = [
            'nume',           
            'descriere',    
            'categorie',      
            'brand',         
            'furnizor',     
            'dimensiuni',   
            'culori', 
        ]
        labels = {
            'nume': 'Denumire produs',        
            'descriere': 'Descriere scurta',  
            'pret': 'Pret (RON)',
            'categorie': 'Categorie produs',
        }

    
    def clean_nume(self):
        val = (self.cleaned_data.get('nume') or '').strip()
        if len(val) < 3:
            raise ValidationError("Numele trebuie sa aiba minim 3 caractere.")
        if not re.fullmatch(r"[0-9A-Za-zăâîșțĂÂÎȘȚ \-]+", val):
            raise ValidationError("Numele poate contine doar litere/cifre/spatiu/cratima.")
        qs = Produs.objects.filter(nume__iexact=val)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Exista deja un produs cu acest nume.")
        return val

    def clean_pret(self):
        pret = self.cleaned_data.get('pret')
        if pret is None or pret <= 0:
            raise ValidationError("Pretul trebuie sa fie mai mare decat 0.")
        if pret > Decimal('100000'):
            raise ValidationError("Pretul este nerealist de mare (peste 100000 RON).")
        return pret

    def clean_descriere(self):
        txt = (self.cleaned_data.get('descriere') or '').strip()
        if _http_re.search(txt):
            raise ValidationError("Descrierea nu poate contine linkuri.")
        if len(re.findall(r"[0-9A-Za-zăâîșțĂÂÎȘȚ]+", txt)) < 3:
            raise ValidationError("Descrierea trebuie sa contina minim 3 cuvinte.")
        return txt
    
    
    def clean(self):
        cleaned = super().clean()
        pret = cleaned.get('pret')
        reducere = cleaned.get('reducere_pct') or Decimal('0')

        if pret is None:
            return cleaned

        pret_final = pret * (Decimal('100') - reducere) / Decimal('100')

        if pret_final < Decimal('10'):
            self.add_error('reducere_pct', "Reducerea este prea mare: prețul final ar scădea sub 10 RON.")
            raise ValidationError("Prețul final după reducere nu poate fi sub 10 RON.")

        return cleaned
    
    
    def save(self, commit=True):
        obj = super().save(commit=False)

        cost = self.cleaned_data.get('cost_achizitie')
        adaos = self.cleaned_data.get('adaos_pct') or Decimal('0')

        if cost is not None:
            pret = (cost * (Decimal('100') + adaos) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            obj.pret = pret
        
        reducere = self.cleaned_data.get('reducere_pct') or Decimal('0')
        if reducere:
            obj.pret = (obj.pret * (Decimal('100') - reducere) / Decimal('100')).quantize(Decimal('0.01'))

        stoc_initial = self.cleaned_data.get('stoc_initial', 0)
        obj.stoc_disponibil = stoc_initial > 0

        if not obj.data_adaugare:
            obj.data_adaugare = date.today()

        if commit:
            obj.save()
            self.save_m2m()
        return obj 
    

from django.contrib.auth import get_user_model   
from django.contrib.auth.forms import UserCreationForm 
User = get_user_model()
    
class CustomUserCreationForm(UserCreationForm):
    telefon = forms.CharField(
        label="Telefon",
        max_length=20,
        required=True,
        help_text="Introduceți un număr de telefon valid.",
    )
    tara = forms.CharField(
        label="Țară",
        max_length=50,
        required=True,
        help_text="Ex: România",
    )
    judet = forms.CharField(
        label="Județ",
        max_length=50,
        required=True,
    )
    oras = forms.CharField(
        label="Oraș",
        max_length=50,
        required=True,
    )
    strada = forms.CharField(
        label="Stradă",
        max_length=100,
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
    
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "telefon",
            "tara",
            "judet",
            "oras",
            "strada",
        )


    def clean_telefon(self):
        tel = (self.cleaned_data.get("telefon") or "").strip()
        
        if not re.fullmatch(r"[0-9+\-\s]{7,20}", tel):
            raise ValidationError("Telefonul poate conține doar cifre, +, -, spațiu (7-20 caractere).")
        return tel

    def clean_tara(self):
        tara = (self.cleaned_data.get("tara") or "").strip()
        if len(tara) < 3:
            raise ValidationError("Țara trebuie să aibă cel puțin 3 caractere.")
        if not re.fullmatch(r"[A-Za-zĂÂÎȘȚăâîșț\s\-]+", tara):
            raise ValidationError("Țara poate conține doar litere, spațiu și cratimă.")
        return tara

    def clean_judet(self):
        jud = (self.cleaned_data.get("judet") or "").strip()
        if not jud:
            raise ValidationError("Județul este obligatoriu.")
        if not jud[0].isupper():
            raise ValidationError("Județul trebuie să înceapă cu literă mare.")
        return jud

    def clean(self):
        cleaned = super().clean()
        tara = (cleaned.get("tara") or "").lower()
        judet = (cleaned.get("judet") or "").lower()

        if tara == "românia" and not judet:
            self.add_error("judet", "Pentru România, județul este obligatoriu.")
        return cleaned
    

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        label="Ține-mă minte 1 zi"
    )
    
class PromotieForm(forms.Form):
    nume = forms.CharField(
        label="Nume promoție",
        max_length=100
    )
    subiect = forms.CharField(
        label="Subiect e-mail",
        max_length=150
    )
    mesaj_baza = forms.CharField(
        label="Mesaj de bază",
        widget=forms.Textarea(attrs={'rows': 4})
    )
    durata_zile = forms.IntegerField(
        label="Durata promoției (zile)",
        min_value=1,
        initial=7
    )
    categorii = forms.ModelMultipleChoiceField(
        label="Categorii pentru promoție",
        queryset=Categorie.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    procent_discount = forms.IntegerField(
        label="Reducere (%)",
        min_value=0,
        max_value=90,
        initial=10
    )