from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

from django.contrib.auth import get_user_model

logger = logging.getLogger('django')
User = get_user_model()


class Command(BaseCommand):
    help = "Șterge utilizatorii neconfirmați (non-admin)"

    def handle(self, *args, **kwargs):
        limita = timezone.now() - timedelta(
            minutes=settings.K_DELETE_UNCONFIRMED
        )

        useri = User.objects.filter(
            email_confirmat=False,
            date_joined__lt=limita,
            is_superuser=False,
            is_staff=False
        )

        for user in useri:
            logger.warning(
                f"Utilizator șters (email neconfirmat): {user.username}"
            )

        useri.delete()
