from django.apps import AppConfig


class ChatapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ChatAPI'

    def ready(self):
        import ChatAPI.signals