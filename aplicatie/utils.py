import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def genereaza_factura(user, comanda, total, total_produse):
    timestamp = int(time.time())

    folder = f"temporar-facturi/{user.username}"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/factura-{timestamp}.pdf"

    c = canvas.Canvas(path, pagesize=A4)
    y = 800

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "FACTURĂ COMANDĂ")
    y -= 40

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Client: {user.first_name} {user.last_name}")
    y -= 20
    c.drawString(50, y, f"Email: {user.email}")
    y -= 30

    for item in comanda.linii.all():
        c.drawString(
            50, y,
            f"{item.produs.nume} | {item.cantitate} x {item.pret_unitar} RON"
        )
        y -= 15

    y -= 20
    c.drawString(50, y, f"Total produse: {total_produse}")
    y -= 15
    c.drawString(50, y, f"Total de plată: {total} RON")

    c.save()
    return path
