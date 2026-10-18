from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RentplayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentplay'
    verbose_name = _('RENTPLAY Real Estate')

    def ready(self):
        import rentplay.signals
