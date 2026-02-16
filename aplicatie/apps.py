from django.apps import AppConfig

class AplicatieConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aplicatie"

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Produs

        @receiver(post_migrate)
        def create_groups(sender, **kwargs):
            # grup produse
            g_prod, _ = Group.objects.get_or_create(name="Administratori_produse")
            ct = ContentType.objects.get_for_model(Produs)
            perms = Permission.objects.filter(
                content_type=ct,
                codename__in=["add_produs", "change_produs", "delete_produs", "view_produs"]
            )
            g_prod.permissions.set(perms)

            # grup site (toate permisiunile)
            g_site, _ = Group.objects.get_or_create(name="Administratori_site")
            g_site.permissions.set(Permission.objects.all())
