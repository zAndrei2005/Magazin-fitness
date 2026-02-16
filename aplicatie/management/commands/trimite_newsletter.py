from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
import logging

from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail

logger = logging.getLogger('django')
User = get_user_model()


class Command(BaseCommand):
    help = "Trimite newsletter zilnic"

    def handle(self, *args, **kwargs):
        limita = timezone.now() - timedelta(
            minutes=settings.NEWSLETTER_MIN_AGE
        )

        useri = User.objects.filter(
            date_joined__lt=limita,
            email_confirmat=True
        )

        mesaje = []
        continut = [
            "Reduceri speciale la produsele tale preferate!",
            "Produse noi au apărut pe site!",
            "Nu rata ofertele săptămânii!",
            "Recomandări personalizate pentru tine!"
        ]

        for user in useri:
            mesaj = random.choice(continut)
            mesaje.append((
                "Newsletter Magazin",
                mesaj,
                None,
                [user.email]
            ))

            logger.info(f"Newsletter trimis către {user.email}")

        send_mass_mail(mesaje, fail_silently=False)
