# 🏋️‍♂️ Magazin Accesorii Fitness & Culturism

O aplicație web modernă dezvoltată în **Django**, dedicată sportivilor. Utilizatorii pot explora și achiziționa echipamente precum mănuși, centuri de ridicare, shakere și benzi elastice.

## ✨ Funcționalități Principale
* **Catalog Produse:** Vizualizare detaliată cu prețuri, dimensiuni și materiale.
* **Filtrare Avansată:** Căutare rapidă după preț, categorie, brand sau culoare.
* **Coș Virtual & Wishlist:** Experiență de cumpărare simplificată pentru clienții autentificați.
* **Sistem Administrativ:** Formular inteligent pentru produse cu calcul automat de preț (cost + adaos - reducere).
* **Task-uri Programate:** Gestionare automată a utilizatorilor neconfirmați și trimitere de newslettere săptămânale.

## 🛠️ Tehnologii Utilizate
* **Backend:** Python & Django
* **Bază de date:** SQLite (dezvoltare) 
* **Frontend:** HTML5, Template-uri Django, CSS 

## 🚀 Instalare și Rulare
1. Clonează repository-ul.
2. Creează și activează mediul virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Pe Windows: venv\Scripts\activate
3. Instalează dependențele:
   pip install -r requirements.txt
4. Rulează migrarea bazei de date:
   python manage.py migrate
5. Pornește serverul:
   python manage.py runserver

👨‍💻 Autor: Olteanu Andrei Cristian