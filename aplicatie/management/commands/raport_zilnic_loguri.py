from django.core.management.base import BaseCommand
import logging
from django.core.mail import mail_admins

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = "Trimite raport zilnic administratorilor"

    def handle(self, *args, **kwargs):
        mesaj = "Raport zilnic generat automat. Sistemul funcționează normal."

        mail_admins(
            subject="Raport zilnic aplicație",
            message=mesaj,
            html_message=f"""
                <h1 style="color:red;">Raport zilnic aplicație</h1>
                <p>{mesaj}</p>
            """
        )

        logger.critical("Raport zilnic trimis către administratori")
