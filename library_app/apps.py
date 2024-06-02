from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_permissions(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    # Get or create the SiteUsers group
    group, created = Group.objects.get_or_create(name='SiteUsers')

    # Get the 'can_add_library' permission
    permission = Permission.objects.get(codename='can add library')

    # Assign the permission to the group
    group.permissions.add(permission)

class LibraryAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library_app'

    def ready(self):
        import library_app.signals

