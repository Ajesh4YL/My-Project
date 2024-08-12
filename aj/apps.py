from django.apps import AppConfig

class AjConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aj'

    def ready(self):
        import aj.signals
