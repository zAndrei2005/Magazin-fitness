from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from aplicatie.models import Vizualizare

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = "Șterge vizualizările mai vechi de 7 zile"

    def handle(self, *args, **kwargs):
        limita = timezone.now() - timedelta(days=7)
        sters = Vizualizare.objects.filter(data__lt=limita).count()
        Vizualizare.objects.filter(data__lt=limita).delete()

        logger.info(f"Vizualizări vechi șterse: {sters}")
