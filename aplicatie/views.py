from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime, date, timedelta
from urllib.parse import urlparse, parse_qs
from .models import Locatie, Produs, Categorie, CustomUser, Vizualizare, Promotie, ComandaItem, Comanda
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import FiltruProduseForm, ContactForm, ProdusForm, PromotieForm
from django.contrib import messages
from django import forms 
import re, os, json, secrets
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from pathlib import Path
from django.apps import apps
from .forms import LoginForm,CustomUserCreationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.template.loader import render_to_string
from django.db.models import Case, When, Value, IntegerField, Count
from django.core.mail import send_mass_mail, mail_admins
import logging
import json, time, os
from django.http import JsonResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from .utils import genereaza_factura


logger = logging.getLogger('django')

# Create your views here.

log_list = []
contor_accesari = 0
parametrii = []

d = {
    "Index": 0,
    "Info": 0,
    "Log": 0,
}

##################### PENTRU CONTACT ##############################
def age_years_months(dob: date, today: date | None = None):
    today = today or date.today()
    total_months = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:   
        total_months -= 1
    years = total_months // 12
    months = total_months % 12
    return years, months

def normalize_whitespace_and_newlines(text: str) -> str:
    if not text:
        return text
    # \n/\r -> spațiu
    text = re.sub(r'[\r\n]+', ' ', text)
    # comaseaza spatiile consecutive
    text = re.sub(r'\s+', ' ', text).strip()
    return text

_CAP_AFTER_TERM = re.compile(r'((?:\.{3}|[\.!\?])\s*)([a-zăâîșț])', re.IGNORECASE | re.UNICODE)

def capitalize_after_terminators(text: str) -> str:
    if not text:
        return text
    
    text = text[0].upper() + text[1:] if text[0].isalpha() else text
    
    def repl(m: re.Match):
        return m.group(1) + m.group(2).upper()
    return _CAP_AFTER_TERM.sub(repl, text)

def min_days_for_tip(tip: str) -> int | None:
    mapping = {'review': 4, 'cerere': 4, 'reclamatie': 2, 'intrebare': 2}
    return mapping.get((tip or '').lower())

def index(request):
    global log_list, contor_accesari, d
    
    accesare = Accesare(request)
    log_list.append(accesare)
    contor_accesari += 1
    d["Index"] += 1
    
    ip = request.META.get('REMOTE_ADDR')

    return render(request, 'aplicatie/index.html', {'ip_utilizator': ip})

def este_admin_site(user):
    return user.is_authenticated and (
        user.groups.filter(name="Administratori_site").exists() or user.is_superuser
    )

@login_required
def info(request):
    if not este_admin_site(request.user):
        return pagina_interzisa(request, titlu="Eroare 403", mesaj="Nu ai voie să accesezi /info")
    
    global log_list, contor_accesari, parametrii, d

    accesare = Accesare(request)
    log_list.append(accesare)
    contor_accesari += 1
    d["Info"] += 1

    tabel = request.GET.get("tabel")
    param_data = request.GET.get("data")
    if param_data is not None and "data" not in parametrii:
        parametrii.append("data")

    # Data afișată (HTML safe)
    data_html = afis_data(param_data)

    # Setăm coloanele afișate
    coloane = []
    if tabel:
        if tabel == "tot":
            coloane = ["id", "ip_client", "url", "data"]
        else:
            coloane = [c.strip() for c in tabel.split(",") if c.strip() in ["id", "ip_client", "url", "data"]]

    # Determinăm paginile cele mai accesate
    d_sortat = sorted(d.items(), key=lambda item: item[1])
    min_accesat = d_sortat[0][0]
    max_accesat = d_sortat[-1][0]
    
    ip = request.META.get('REMOTE_ADDR')

    return render(request, "aplicatie/info.html", {
        "log_list": log_list,
        "coloane": coloane,
        "parametrii": parametrii,
        "data_html": data_html,
        "param_data": param_data,
        "min_accesat": min_accesat,
        "max_accesat": max_accesat,
        "ip_utilizator": ip,
    })


def afis_data(param):    
    now = datetime.now()

    luni = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
            "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]
    zile = ["luni", "marti", "miercuri", "joi", "vineri", "sambata", "duminica"]

    if param == "zi":
        data_afis = f"{zile[now.weekday()]}, {now.day} {luni[now.month - 1]} {now.year}"
        return f"<h2>Data:</h2><p>{data_afis}</p>"

    elif param == "timp":
        timp_afis = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
        return f"<h2>Ora:</h2><p>{timp_afis}</p>"

    else:
        data_timp_afis = f"{zile[now.weekday()]}, {now.day} {luni[now.month - 1]} {now.year} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"
        return f"<h2>Data si ora:</h2><p>{data_timp_afis}</p>"
    
def get_ip(request):
    req_headers = request.META
    str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if str_lista_ip:
        return str_lista_ip.split(',')[-1].strip()
    else:
        return request.META.get('REMOTE_ADDR')

class Accesare:
    _id_counter = 1  

    def __init__(self, request):
        self.id = Accesare._id_counter
        Accesare._id_counter += 1

        self.ip_client = get_ip(request)
        self.url_accesat = request.build_absolute_uri() 
        self.data_accesare = datetime.now()

    def lista_parametri(self):
        return [
            ('id', self.id),
            ('ip_client', self.ip_client if self.ip_client else None),
            ('url', self.url_accesat if self.url_accesat else None),
            ('data', self.data_accesare if self.data_accesare else None)
        ]

    def url(self):
        return self.url_accesat

    def data(self, format_str="%d-%m-%Y %H:%M:%S"):
        return self.data_accesare.strftime(format_str)
    
    def pagina(self):
        if not self.url_accesat:
            return None
        parsed = urlparse(self.url_accesat)
        return parsed.path

@login_required
def log_cereri(request):
    if not este_admin_site(request.user):
        return pagina_interzisa(request, titlu="Eroare 403", mesaj="Nu ai voie să accesezi /log")
    
    global log_list, contor_accesari, parametrii, d

    ultimele = request.GET.get("ultimele")
    accesari = request.GET.get("accesari")
    iduri = request.GET.getlist("iduri")
    dubluri = request.GET.get("dubluri", "false").lower()

    if ultimele is not None and "ultimele" not in parametrii:
        parametrii.append("ultimele")
    if accesari is not None and "accesari" not in parametrii:
        parametrii.append("accesari")
    if iduri is not None and "iduri" not in parametrii:
        parametrii.append("iduri")
    if "dubluri" not in parametrii:
        parametrii.append("dubluri")

    accesare = Accesare(request)
    log_list.append(accesare)
    contor_accesari += 1
    d["Log"] += 1

    total_accesari = None
    accesari_detalii = None
    iduri_afis = None
    ultimele_afis = None

    if accesari == "nr":
        total_accesari = contor_accesari
    elif accesari == "detalii":
        accesari_detalii = log_list

    if iduri:
        toate_iduri = []
        for id in iduri:
            toate_iduri.extend(id.split(","))

        id_vizitate = []
        id_finale = []
        for x in toate_iduri:
            try:
                idx = int(x)
            except ValueError:
                continue
            if dubluri == "true" or idx not in id_vizitate:
                id_finale.append(idx)
                id_vizitate.append(idx)

        iduri_afis = [a for a in log_list if a.id in id_finale]

    if ultimele:
        try:
            n = int(ultimele)
        except ValueError:
            return HttpResponse("EROARE: 'ultimele' trebuie să fie un număr întreg.")
        ultimele_afis = log_list[-n:] if len(log_list) >= n else log_list
        
    accesari_detalii = [
        {
            "id": a.id,
            "ip_client": a.ip_client,
            "url": a.url(),
            "data": a.data()
        }
        for a in log_list
    ]

    ip = request.META.get('REMOTE_ADDR')
    
    return render(request, "aplicatie/log.html", {
        "total_accesari": total_accesari,
        "accesari_detalii": accesari_detalii,
        "iduri_afis": iduri_afis,
        "ultimele_afis": ultimele_afis,
        "ip_utilizator": ip
    })
                  
    
def afis_template(request):
    return render(request,"aplicatie/exemplu.html",
        {
            "titlu_tab":"Titlu fereastra",
            "titlu_articol":"Titlu afisat",
            "continut_articol":"Continut text"
        }
    )
    
def despre(request):
    ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie/despre.html', {'ip_utilizator': ip})

def contact(request):
    ip = request.META.get('REMOTE_ADDR')
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            y, m = age_years_months(cd['data_nasterii'])
            varsta_text = f"{y} ani și {m} luni"

            mesaj_norm = normalize_whitespace_and_newlines(cd['mesaj'])
            mesaj_norm = capitalize_after_terminators(mesaj_norm)

            tip = (cd.get('tip_mesaj') or '').lower()
            zile = cd.get('zile_asteptare')
            mind = min_days_for_tip(tip)
            urgent = bool(mind is not None and zile == mind)

            payload = {
                "nume": cd["nume"],
                "prenume": cd.get("prenume"),
                "email": cd["email"],
                "tip_mesaj": cd["tip_mesaj"],
                "subiect": cd["subiect"],
                "zile_asteptare": zile,
                "urgent": urgent,
                "varsta": varsta_text,          
                "mesaj": mesaj_norm,
                "ip": ip,
                "moment": timezone.now().isoformat(),  
            }

            app_dir = apps.get_app_config('aplicatie').path   
            out_dir = Path(app_dir) / "Mesaje"
            out_dir.mkdir(parents=True, exist_ok=True)

            now = timezone.now()
            timestamp = int(now.timestamp())   
            suffix = "_urgent" if urgent else ""
            filename = f"mesaj_{timestamp}{suffix}.json"
            out_path = out_dir / filename
            
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2) 

            messages.success(request, f"Mesajul a fost salvat în {out_path.name}.")
            return redirect('contact')

        else:
            messages.error(request, f"Formular invalid: {form.errors.as_text()}")
    else:
        form = ContactForm()
        
    return render(request, 'aplicatie/contact.html', {
        'ip_utilizator': ip,
        'form': form,
    })

def cos_virtual(request):
    ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie/in_lucru.html', {'ip_utilizator': ip})

def afis_locatii(request): 
    locatii = Locatie.objects.all()
    return render(request, 'aplicatie/locatii.html',{
        "locatii":locatii[0],
        "nr_locatii": len(locatii),
    })
    

def afis_produse(request, sort=None): 
    
    messages.debug(request, "A început procesarea listei de produse")
    messages.debug(request, f"Parametri GET: {request.GET}")
    
    logger.debug("DEBUG: A început procesarea paginii de listare produse.")
    logger.debug(f"DEBUG: Parametrii de filtrare primiți: {request.GET}")
    
    try:
        produse = Produs.objects.all()
    except Exception as e:
        logger.error(f"ERROR: Eroare la citirea produselor din baza de date: {e}")
        
        mail_admins(
        subject="Eroare critică la afișarea produselor",
        message=f"{e}",
        html_message=f"""
            <h1 style='color:red;'>Eroare la afișarea produselor</h1>
            <p style='background:red;color:white;'>{e}</p>
        """
        )

        produse = Produs.objects.none()  # să nu crape pagina
    
    if request.GET.get('reset') == '1':
        messages.info(request, "Filtrele au fost resetate. Vezi din nou toate produsele.")
        return redirect(request.path)
    
    sort = (sort or request.GET.get('sort') or 'a').lower()
    if sort not in ('a', 'd'):
        sort = 'a'

    qs = (Produs.objects
          .annotate(
              stoc_zero=Case(
                  When(stoc=0, then=Value(1)),
                  default=Value(0),
                  output_field=IntegerField()
              )
          )
          .select_related('categorie', 'brand', 'furnizor')
          .prefetch_related('dimensiuni', 'culori'))
        
    form = FiltruProduseForm(request.GET or None)
    nr_pe_pagina = 5
    if form.is_valid():
        cd = form.cleaned_data

        if cd.get('nume'):
            qs = qs.filter(nume__icontains=cd['nume'])
        if cd.get('descriere'):
            qs = qs.filter(descriere__icontains=cd['descriere'])

        if cd.get('categorie'):
            qs = qs.filter(categorie=cd['categorie'])
        if cd.get('brand'):
            qs = qs.filter(brand=cd['brand'])
        if cd.get('furnizor'):
            qs = qs.filter(furnizor=cd['furnizor'])

        if cd.get('culori'):
            qs = qs.filter(culori__in=cd['culori']).distinct()
        if cd.get('dimensiuni'):
            qs = qs.filter(dimensiuni__in=cd['dimensiuni']).distinct()

        if cd.get('stoc_disponibil') is True:
            qs = qs.filter(stoc_disponibil=True)
        elif cd.get('stoc_disponibil') is False:
            qs = qs.filter(stoc_disponibil=False)

        if cd.get('pret_min') is not None:
            qs = qs.filter(pret__gte=cd['pret_min'])
        if cd.get('pret_max') is not None:
            qs = qs.filter(pret__lte=cd['pret_max'])

        if cd.get('data_min'):
            qs = qs.filter(data_adaugare__gte=cd['data_min'])
        if cd.get('data_max'):
            qs = qs.filter(data_adaugare__lte=cd['data_max'])
        
        if cd.get('nr_pe_pagina'):
            try:
                nr_pe_pagina = int(cd['nr_pe_pagina'])
            except ValueError:
                nr_pe_pagina = 5            
            
    ordinea = 'pret' if sort == 'a' else '-pret'
    qs = qs.order_by('stoc_zero', ordinea)
    
    previous_nr_pe_pagina = request.session.get('last_page_size')
    if previous_nr_pe_pagina and previous_nr_pe_pagina != nr_pe_pagina:
        messages.warning(
            request,
            " Ati modificat numarul de produse per pagina. "
            "Este posibil sa fi sarit peste unele produse sau sa le vedeti din nou."
        )
        
    request.session['last_page_size'] = nr_pe_pagina
            
    paginator = Paginator(qs, nr_pe_pagina)
    page = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    qs_params = request.GET.copy()
    qs_params.pop('page', True)
    querystring = qs_params.urlencode()

    ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie/produse.html', {
        'form': form,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'ip_utilizator': ip,
        'sort': sort,
        'querystring': querystring,
    })
    
    
MAX_VIZUALIZARI = 5

def produs_detail(request, pk):
    ip = request.META.get('REMOTE_ADDR')
    try:
        produs = Produs.objects.get(pk=pk)  
    
    except Exception as e:
        
        logger.warning(f"WARNING: Produsul cu ID={pk} nu există.")
        
        subject = "Eroare în funcția produs_detail"
        message = f"Eroare detectată: {str(e)}"
        html_message = f"""
            <h1 style="color:red;">Eroare critică</h1>
            <p style="background-color:#ffdddd;padding:10px;">
                {str(e)}
            </p>
        """

        mail_admins(subject, message, html_message=html_message)

        messages.error(request, "A apărut o eroare internă.")
        return redirect("index")
    
    if request.user.is_authenticated:
        v = Vizualizare.objects.create(
            utilizator=request.user,
            produs=produs
        )

        viz_user = Vizualizare.objects.filter(utilizator=request.user).order_by('-data_vizualizare')

        extra = viz_user[MAX_VIZUALIZARI:]  
        if extra:
            Vizualizare.objects.filter(id__in=[x.id for x in extra]).delete()
            
    else:
        logger.warning("WARNING: Tentativă de acces la pagina de profil fără autentificare.")
            
    return render(request, 'aplicatie/produs_detail.html', {'produs': produs, 'ip_utilizator':ip,})

def lista_categorii(request):
    if request.GET.get('reset') == '1':
        messages.info(request, "Filtrele au fost resetate. Vezi din nou toate produsele.")
        return redirect(request.path)
    
    categorii = Categorie.objects.all()
    ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie/categorii.html', {'categorii': categorii,'ip_utilizator':ip})

def afis_categorie(request, nume_categorie, sort = None):
    if request.GET.get('reset') == '1':
        messages.info(request, "Filtrele au fost resetate. Vezi din nou toate produsele.")
        return redirect(request.path)
    
    categorie = get_object_or_404(Categorie, nume__iexact=nume_categorie)
    
    sort = (sort or request.GET.get('sort') or 'a').lower()
    if sort not in ('a', 'd'):
        sort = 'a'
    
    qs = (Produs.objects
               .filter(categorie=categorie)
               .select_related('brand', 'furnizor')
               .prefetch_related('culori', 'dimensiuni'))
    
    cat_from_query = request.GET.get('categorie') or request.GET.get('categorie_hidden')
    
    if cat_from_query: 
        try:
            if int(cat_from_query) != int(categorie.pk):
                messages.error(
                    request,
                    "Categoria nu poate fi modificata pe aceasta pagina. Am afisat doar produsele din categoria selectata."
                )
            safe_params = request.GET.copy()
            for key in ("categorie","categorie_hidden"):
                safe_params.pop(key,True)
            qs_string = safe_params.urlencode()
            target = request.path + (("?" + qs_string) if qs_string else "")
            return redirect(target)
        except ValueError:
            messages.error(
                request,
                "Valoarea categoriei este invalida. Am revenit la categoria corecta."
            )
            safe_params = request.GET.copy()
            for key in ("categorie", "categorie_hidden"):
                safe_params.pop(key, True)
            qs_string = safe_params.urlencode()
            target = request.path + (("?" + qs_string) if qs_string else "")
            return redirect(target)
    
    form = FiltruProduseForm(request.GET or None, initial = {'categorie' : categorie.pk})
    form.fields['categorie'].disabled = True
    nr_pe_pagina = 5
    if form.is_valid():
        cd = form.cleaned_data

        if cd.get('nume'):
            qs = qs.filter(nume__icontains=cd['nume'])
        if cd.get('descriere'):
            qs = qs.filter(descriere__icontains=cd['descriere'])

        if cd.get('brand'):
            qs = qs.filter(brand=cd['brand'])
        if cd.get('furnizor'):
            qs = qs.filter(furnizor=cd['furnizor'])

        if cd.get('culori'):
            qs = qs.filter(culori__in=cd['culori']).distinct()
        if cd.get('dimensiuni'):
            qs = qs.filter(dimensiuni__in=cd['dimensiuni']).distinct()

        if cd.get('stoc_disponibil') is True:
            qs = qs.filter(stoc_disponibil=True)
        elif cd.get('stoc_disponibil') is False:
            qs = qs.filter(stoc_disponibil=False)

        if cd.get('pret_min') is not None:
            qs = qs.filter(pret__gte=cd['pret_min'])
        if cd.get('pret_max') is not None:
            qs = qs.filter(pret__lte=cd['pret_max'])

        if cd.get('data_min'):
            qs = qs.filter(data_adaugare__gte=cd['data_min'])
        if cd.get('data_max'):
            qs = qs.filter(data_adaugare__lte=cd['data_max'])
        
        if cd.get('nr_pe_pagina'):
            try:
                nr_pe_pagina = int(cd['nr_pe_pagina'])
            except ValueError:
                nr_pe_pagina = 5    
            
    qs = qs.order_by('-pret' if sort == 'd' else 'pret')
    
    previous_nr_pe_pagina = request.session.get('last_page_size')
    if previous_nr_pe_pagina and previous_nr_pe_pagina != nr_pe_pagina:
        messages.warning(
            request,
            " Ati modificat numarul de produse per pagina. "
            "Este posibil sa fi sarit peste unele produse sau sa le vedeti din nou."
        )
        
    request.session['last_page_size'] = nr_pe_pagina
            
    paginator = Paginator(qs, nr_pe_pagina)
    page = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    qs_params = request.GET.copy()
    qs_params.pop('page', True)
    querystring = qs_params.urlencode()
    
    ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie/categorii.html', {
        'form': form,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'sort': sort,
        'querystring': querystring,
        'categorie_selectata': categorie,   
        'ip_utilizator': ip 
    })
    
@login_required
def adauga_produs(request):
    if not request.user.has_perm("aplicatie.add_produs"):
        return pagina_interzisa(
            request,
            titlu="Eroare adaugare produse",
            mesaj="Nu ai voie să adaugi produse"
        )
        
    if request.method == 'POST':
        form = ProdusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Produsul a fost adaugat cu succes.")
            return redirect('adauga_produs')  
    else:
        form = ProdusForm()

    ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie/adauga_produs.html', {'form': form, 'ip_utilizator':ip,})


def login_view(request):

    if request.user.is_authenticated:
        return redirect('profil')
    
    attempts = request.session.get("login_attempts", [])
    
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        username_try = request.POST.get("username")
        user_ip = request.META.get("REMOTE_ADDR")
        
        if form.is_valid():
            user = form.get_user()
            if user.blocat:
                messages.error(request, "Contul tău este blocat. Contactează un administrator.")
                return redirect('login')
            
            request.session["login_attempts"] = []
            
            if not getattr(user, "email_confirmat", False):
                messages.error(
                    request,
                    "Trebuie să îți confirmi adresa de e-mail înainte să te poți autentifica. "
                    "Verifică inbox-ul (și folderul Spam)."
                )
                return render(request, "aplicatie/login.html", {"form": form})
            
            logger.info(f"INFO: Utilizatorul {user.username} s-a autentificat cu succes.")

            login(request, user)

            request.session["profil_user"] = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "varsta": getattr(user, "varsta", None),
                "telefon": getattr(user, "telefon", None),
                "oras": getattr(user, "oras", None),
                "data_nasterii": str(getattr(user, "data_nasterii", "")),
                "gen": getattr(user, "gen", None),
            }

            if form.cleaned_data.get("remember_me"):
                request.session.set_expiry(24*60*60)  
            else:
                request.session.set_expiry(0)  

            return redirect("profil")  
        else:
            now = timezone.now().timestamp()
            attempts.append(now)
            request.session["login_attempts"] = attempts

            two_minutes_ago = now - 120
            recent_attempts = [t for t in attempts if t > two_minutes_ago]

            if len(recent_attempts) >= 3:
                subject = "Logari suspecte"
                message = f"""
                    Au existat 3 încercări eșuate de logare în mai puțin de 2 minute.
                    Username încercat: {username_try}
                    IP: {user_ip}
                """

                html_message = f"""
                    <h1 style='color:red;'>Logari suspecte</h1>
                    <p>Au existat <strong>3 încercări eșuate</strong> de logare în &lt; 2 minute.</p>
                    <p><strong>Username:</strong> {username_try}</p>
                    <p><strong>IP:</strong> {user_ip}</p>
                """
                
                logger.critical(f"CRITICAL: 3 login-uri eșuate pentru username {username_try} de la IP {user_ip}.")
                
                mail_admins(subject, message, html_message=html_message)

                request.session["login_attempts"] = []

            messages.error(request, "Date de logare incorecte.")
    else:
        form = LoginForm(request)

    return render(request, "aplicatie/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "V-ați delogat.")
    return redirect("index")


@login_required
def profil_view(request):
    date_profil = request.session.get("profil_user", {})

    return render(request, "aplicatie/profil.html", {
        "profil": date_profil
    })
    
@login_required
def schimba_parola_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # evita delogarea automata
            messages.success(request, "Parola a fost schimbată cu succes.")
            return redirect("profil")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "aplicatie/schimba_parola.html", {"form": form})

from django.core.mail import send_mail, EmailMessage

def trimite_email():
    send_mail(
        subject='Olteanu Andrei Cristian 242!',
        message='Salut. Ma numesc Olteanu Andrei Cristian,grupa242',
        html_message='<h1>Salut</h1><p>Ce mai faci?</p>',
        from_email='test.tweb.node@gmail.com',
        recipient_list=['test.tweb.node@gmail.com'],
        fail_silently=False,
    )

def confirma_mail(request, cod):
    user = get_object_or_404(CustomUser, cod=cod)

    if not user.email_confirmat:
        user.email_confirmat = True
        user.cod = None
        user.save()

    return render(request, 'aplicatie/confirmare_succes.html', {'user': user})

def register_view(request):

    if request.user.is_authenticated:
        return redirect('profil')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username_try = form.cleaned_data["username"]
            email_try = form.cleaned_data["email"]

            if username_try.lower() == "admin":
                subject = "cineva incearca sa ne preia site-ul"
                message = f"""
                    Cineva a încercat să se înregistreze cu username-ul 'admin'.
                    Email folosit: {email_try}
                """
                html_message = f"""
                    <h1 style="color:red;">Cineva încearcă să ne preia site-ul</h1>
                    <p>A fost detectată o tentativă de înregistrare cu username <strong>admin</strong>.</p>
                    <p><strong>Email folosit:</strong> {email_try}</p>
                """

                mail_admins(subject, message, html_message=html_message)
                
                logger.critical(f"CRITICAL: Tentativă de înregistrare cu username interzis 'admin' de la emailul {email_try}.")

                messages.error(request, "Acest username este interzis.")
                return redirect("register")

            user = form.save()

            logger.info(f"INFO: Cont nou creat pentru utilizatorul {user.username}.")
            
            user.cod = secrets.token_urlsafe(16)  
            user.email_confirmat = False
            user.save()

            confirm_url = request.build_absolute_uri(
                reverse('confirma_mail', args=[user.cod])
            )

            context = {
                'user': user,
                'confirm_url': confirm_url,
            }
            html_content = render_to_string(
                'aplicatie/email_confirmare.html',
                context
            )

            email = EmailMessage(
                subject='Bun venit pe Magazinul Fitness!',
                body=html_content,
                to=[user.email],
            )
            email.content_subtype = 'html'  
            try:
                email.send(fail_silently=False)
            except Exception as e:
                logger.error(f"Eroare la trimiterea emailului: {e}")
                
                mail_admins(
                    subject="EROARE LA TRIMITEREA EMAILULUI",
                    message=f"Eroarea a fost: {e}",
                    html_message=f"""
                        <h1 style='color:red;'>Eroare la trimiterea emailului</h1>
                        <p style='background:red;color:white;'>{e}</p>
                    """
                )


            messages.success(
                request,
                'Cont creat! Ți-am trimis un e-mail cu link de confirmare.'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'aplicatie/register.html', {'form': form})


K_VIZUALIZARI = 3  

@login_required
def promotii_view(request):
    if not request.user.is_staff:
        messages.error(request, "Nu aveți dreptul să trimiteți promoții.")
        return redirect('index')

    if request.method == 'POST':
        form = PromotieForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            data_expirare = timezone.now() + timedelta(days=cd['durata_zile'])

            promo = Promotie.objects.create(
                nume=cd['nume'],
                subiect=cd['subiect'],
                mesaj_baza=cd['mesaj_baza'],
                data_expirare=data_expirare,
                procent_discount=cd['procent_discount'],
                activ=True
            )
            promo.categorii.set(cd['categorii'])

            messages_to_send = []

            for categorie in cd['categorii']:
                utilizatori_ids = (
                    Vizualizare.objects
                    .filter(produs__categorie=categorie)
                    .values('utilizator')
                    .annotate(cnt=Count('id'))
                    .filter(cnt__gte=K_VIZUALIZARI)
                    .values_list('utilizator', flat=True)
                )

                utilizatori = CustomUser.objects.filter(
                    id__in=utilizatori_ids,
                    email_confirmat=True 
                ).exclude(email='')

                if not utilizatori:
                    continue

                nume_cat = categorie.nume.lower()
                if "supliment" in nume_cat:
                    template_name = "promotii/email_suplimente.txt"
                elif "accesorii" in nume_cat:
                    template_name = "promotii/email_accesorii.txt"
                else:
                    template_name = "promotii/email_suplimente.txt"

                context = {
                    'subiect': cd['subiect'],
                    'data_expirare': data_expirare,
                    'categorie': categorie,
                    'procent_discount': cd['procent_discount'],
                    'mesaj_baza': cd['mesaj_baza'],
                    'user': None,
                }
                text_body = render_to_string(template_name, context)

                to_emails = [u.email for u in utilizatori]

                messages_to_send.append((
                    cd['subiect'],             
                    text_body,                 
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                    to_emails                  
                ))

            if messages_to_send:
                send_mass_mail(messages_to_send, fail_silently=False)
                messages.success(request, "Promoțiile au fost trimise cu succes.")
            else:
                messages.info(request, "Nu a fost găsit niciun utilizator eligibil pentru promoțiile selectate.")

            return redirect('promotii') 
    else:
        form = PromotieForm()

    return render(request, "aplicatie/promotii.html", {"form": form})


def pagina_interzisa(request, mesaj="Nu ai permisiunea să accesezi această resursă.", titlu=None):
    # incrementare contor 403 în sesiune
    nr_403 = request.session.get('nr_403', 0) + 1
    request.session['nr_403'] = nr_403

    context = {
        'mesaj_personalizat': mesaj,
        'titlu': titlu,
        'nr_403': nr_403,
        'N_MAX_403': settings.N_MAX_403,
    }

    return HttpResponseForbidden(
        render(request, 'aplicatie/403.html', context)
    )
    
@login_required
def acorda_oferta(request):
    perm = Permission.objects.get(codename="vizualizeaza_oferta")
    request.user.user_permissions.add(perm)
    return redirect("oferta")

@login_required
def oferta(request):
    if not request.user.has_perm("aplicatie.vizualizeaza_oferta"):
        # contorizare acces 403 (task anterior)
        request.session["nr_403"] = request.session.get("nr_403", 0) + 1

        return HttpResponseForbidden(
            render(
                request,
                "403.html",
                {
                    "titlu": "Eroare afisare oferta",
                    "mesaj_personalizat": "Nu ai voie să vizualizezi oferta",
                },
            )
        )

    return render(request, "aplicatie/oferta.html")

@login_required
def logout_view(request):
    request.user.user_permissions.filter(
        codename='vizualizeaza_oferta'
    ).delete()

    logout(request)
    return redirect("login")

def cos_view(request):
    return render(request, "aplicatie/cos.html")

@login_required
def cumpara_view(request):
    try:
        # 1. Încărcăm datele primite de la JS
        cos = json.loads(request.body)
        if not cos:
            return JsonResponse({"status": "error", "message": "Cosul este gol"}, status=400)

        # 2. Creăm comanda părinte
        comanda = Comanda.objects.create(user=request.user)

        total = 0
        total_produse = 0

        # 3. Procesăm produsele (Scădem stocul și creăm itemii)
        for produs_id, data in cos.items():
            produs = Produs.objects.get(id_produs=produs_id)

            ComandaItem.objects.create(
                comanda=comanda,
                produs=produs,
                cantitate=data["cantitate"],
                pret_unitar=data["pret"]
            )

            total += data["cantitate"] * data["pret"]
            total_produse += data["cantitate"]

            produs.stoc -= data["cantitate"]
            produs.save()

        # 4. Generăm factura PDF
        pdf_path = genereaza_factura(request.user, comanda, total, total_produse)

        # 5. Încercăm trimiterea mailului (fără să blocăm procesul dacă eșuează)
        try:
            email = EmailMessage(
                subject="Factura comenzii tale",
                body="Atașat găsești factura comenzii.",
                to=[request.user.email]
            )
            email.attach_file(pdf_path)
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Eroare SMTP (trimitere mail): {e}")
            # Nu returnăm eroare aici, pentru că stocul a fost deja scăzut cu succes

        return JsonResponse({"status": "ok"})

    except Exception as e:
        print(f"Eroare generală la cumpara_view: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500) 
